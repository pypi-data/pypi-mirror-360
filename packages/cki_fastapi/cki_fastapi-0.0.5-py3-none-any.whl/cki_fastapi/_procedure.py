from collections import defaultdict
from datetime import datetime, timezone
from email.message import EmailMessage
import logging
import logging.config
import secrets
import sys
import tempfile
from typing_extensions import deprecated
import pyrfc6266
import asyncio
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
import requests
from ._metadata import FilePathInput, FilePathsInput, FilePathOutput, FilePathsOutput, ProcedureInfo, RootWidget
from inspect import Parameter, Signature, signature
from typing import Annotated, Any, Callable, DefaultDict, Literal, Optional, Sequence, Union
from dataclasses import dataclass
from pydantic import BaseModel, Field, create_model
from fastapi import Header, BackgroundTasks, Depends, FastAPI
from fastapi.routing import APIRouter
import json
import os.path

logger = logging.getLogger('cki_fastapi')

_file_cache_dir = tempfile.TemporaryDirectory()
_file_id_to_path: dict[int, str] = {}
_file_id_to_path_rev: dict[str, int] = {}
logger.debug("Using temp directory %s", _file_cache_dir.name)

timeout = (5, 100)

class RunAction(BaseModel):
    type: Literal['run'] = 'run'
    run_id: int


class InitInputsAction(BaseModel):
    type: Literal['init_inputs']


class UpdateInputAction(BaseModel):
    type: Literal['update_input']
    input_name: str


class UpdateInputCellsAction(BaseModel):
    """
    This action represents a modification to one or more cells in a rectangular range of a table input.
    The range is identified by row indices and column names.
    """
    type: Literal['update_input_cells']
    input_name: str
    rows: list[int]
    columns: list[str]

class InsertInputRowsAction(BaseModel):
    """
    This action represents insertion or addition of one or more rows of a table input identified by row indices after the insertion is done.
    If rows were inserted by pasting copied rows, blank is False, otherwise it is True.
    """
    type: Literal['insert_input_rows']
    input_name: str
    rows: list[int]
    blank: bool

class DeleteInputRowsAction(BaseModel):
    """
    This action represents deletion of one or more rows of a table input identified by row indices before the deletion.
    Note that the current value of the table does not have the deleted rows.
    """
    type: Literal['delete_input_rows']
    input_name: str
    rows: list[int]

class ClickAction(BaseModel):
    type: Literal['click']
    widget_name: str

ProcedureAction = Annotated[Union[RunAction, 
                                  InitInputsAction,
                                  UpdateInputAction, 
                                  UpdateInputCellsAction, 
                                  InsertInputRowsAction,
                                  DeleteInputRowsAction,
                                  ClickAction], Field(discriminator="type")]

_UpdateAction = Annotated[Union[InitInputsAction, 
                                UpdateInputAction,
                                UpdateInputCellsAction,
                                InsertInputRowsAction,
                                DeleteInputRowsAction,
                                ClickAction], Field(discriminator="type")]

StatusCategory = Literal["none"] | Literal["message"] | Literal["warning"] | Literal["error"]


class Validation(BaseModel):
    category: StatusCategory
    status_code: int
    message: str
    input_name: str = ""


_cat_num = {"none": 0, "message": 1, "warning": 2, "error": 3}


class _RunContext(BaseModel):
    run_type: Literal["direct"] | Literal["link"] | Literal["checklist"] | Literal["run"] | Literal[
        "schedule"] | Literal["api"] | Literal["email"] | Literal["workflow"] | Literal["retry"] = "api"
    parent_run_id: int | None = None
    run_info: dict | None = None
    link_id: int | None = None


@dataclass
class _SendEmailRecord:
    config_key: str
    eml_file_path: str
    bcc: str
    retain: bool
    retry_hours: float

class _EmailManager:
    def __init__(self, context: 'ProcedureContext') -> None:
        self.records: list[_SendEmailRecord] = []
        self.context = context
        self._id = -1

    def append(self, record: _SendEmailRecord):
        self.records.append(record)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        run_id = self.context._run_id
        if run_id is None:
            return
        assert _ck_client is not None
        if exc_type is None:
            for record in self.records:
                self._id = self._id + 1
                _ck_client.send_email(record, run_id=run_id, id=self._id, immediate=False, keep_alive=False)


class ProcedureContext:
    def __init__(self, procedure_id: int, user_id: int, session_id: str):
        self.procedure_id = procedure_id
        self.user_id = user_id
        self.session_id = session_id
        self._run_context: _RunContext | None = None
        self._run_id: int | None = None
        self._entry_id = -1
        self._validations: list[Validation] = []
        self._input_validations: dict[str, Validation] = {}
        self._managers: list[Any] = []
        self.temp_dir: str = self.with_(tempfile.TemporaryDirectory())
        self._email_manager: _EmailManager = self.with_(_EmailManager(self))
    
    
    # before_commit: Callable | None = None
    
    def with_(self, manager):
        self._managers.append(manager)
        return manager.__enter__()
    
    def _commit(self):
        ex_info = [None, None, None]
        while self._managers:
            m = self._managers.pop()
            try:
                m.__exit__(*ex_info)
            except Exception:
                self._exit_with_exc_info(sys.exc_info())
                raise

    def _rollback(self, status: str):
        try:
            raise ValueError(status)
        except ValueError:
            self._exit_with_exc_info(sys.exc_info())
    
    def _exit_with_exc_info(self, ex_info):
        while self._managers:
            m = self._managers.pop()
            try:
                m.__exit__(*ex_info)
            except Exception:
                pass

    def _report_status_entry(self, validation: Validation):
        if self._run_id is None:
            return
        self._entry_id = self._entry_id + 1
        assert _ck_client is not None
        _ck_client.store_log_entry(self._run_id, self._entry_id, validation.model_dump())

    def report_input_validation(self, input_name: str, category: StatusCategory, message: str):
        if not input_name:
            raise ValueError("input_name must be specified")

        validation = Validation(category=category, status_code=0, message=message, input_name=input_name)
        self._validations.append(validation)

        old = self._input_validations.get(input_name)
        if old is None or _cat_num[old.category] < _cat_num[category]:
            self._input_validations[input_name] = validation

        self._report_status_entry(validation)

    def report_status(self, status_code: int, category: StatusCategory, message: str):
        validation = Validation(category=category, status_code=status_code, message=message)
        self._validations.append(validation)

        self._report_status_entry(validation)

    def send_email_immediately(self, *, config_key: str, eml_file_path: str, bcc: str | list[str] = "", retain=False, retry_hours=12.0, keep_alive=False):
        if self._run_id is None:
            return
        em = self._email_manager
        if isinstance(bcc, list):
            bcc = ', '.join(bcc)
        record = _SendEmailRecord(config_key, eml_file_path, bcc, retain, retry_hours)
        assert _ck_client is not None
        em._id = em._id + 1
        _ck_client.send_email(record, run_id=self._run_id, id=em._id, immediate=True, keep_alive=keep_alive)

    def send_email_on_success(self, *, config_key: str, eml_file_path: str, bcc: str | list[str] = "", retain=False, retry_hours=12.0):
        if self._run_id is None:
            return
        if isinstance(bcc, list):
            bcc = ', '.join(bcc)
        record = _SendEmailRecord(config_key, eml_file_path, bcc, retain, retry_hours)
        self._email_manager.append(record)

    def _get_final_status(self):
        err = False
        warn = False
        for v in self._validations:
            if v.category == "warning":
                warn = True
            elif v.category == "error":
                err = True
                break
        if err:
            return "Failed"
        elif warn:
            return "SucceededWarn"
        else:
            return "Succeeded"

def _withSignature(sig: Signature):
    def decorator(func):
        func.__signature__ = sig
        return func
    return decorator


class _BkgRunResult(BaseModel):
    id: int


_router: APIRouter = APIRouter(prefix="/procedures")
_modules: dict[str, 'ModuleInfo'] = {}
_static_path: str | None = None

@dataclass
class _FilePathNames:
    scalar: list[str]
    array: list[str]
    table: dict[str, list[str]]


class _ProcInfoFull:
    def __init__(self, proc_func, *, unique_id: str, name: str, group: str, version: int, immediate: bool, inputs_require_initialization: bool, page_template: RootWidget | None) -> None:
        self.func = proc_func
        sig = signature(proc_func)
        self.sig = sig
        proc = ProcedureInfo(sig, unique_id=unique_id, name=name, group=group, version=version,
                             immediate=immediate, inputs_require_initialization=inputs_require_initialization, page_template=page_template)
        self.basic = proc

        orig_inputs_type: type[BaseModel] = sig.parameters['inputs'].annotation
        inputs_type = None
        ifp_names = [inp.name for inp in proc.inputs if isinstance(inp, FilePathInput)]
        ifps_names = [inp.name for inp in proc.inputs if isinstance(inp, FilePathsInput)]
        if ifp_names:
            inputs_type = create_model('Inputs', __base__=orig_inputs_type)
            # change field annotation to file id (int) instead of file path (str)
            for inp_name in ifp_names:
                fp_field = inputs_type.model_fields[inp_name]
                fp_field.annotation = Optional[int]
                fp_field.default = None
        if ifps_names:
            if inputs_type is None:
                inputs_type = create_model('Inputs', __base__=orig_inputs_type)
            # change field annotation to file id (int) instead of file path (str)
            for inp_name in ifps_names:
                fp_field = inputs_type.model_fields[inp_name]
                fp_field.annotation = Optional[list[int]]
                fp_field.default = None

        if inputs_type is None:
            inputs_type = orig_inputs_type
        else:
            inputs_type.model_rebuild(force=True)

        orig_outputs_type = sig.return_annotation
        outputs_type = None
        dyn_opts_inp_out: dict[str, str] = {}
        for inp in proc.inputs:
            opts = inp.get_TextInputOptions()
            if opts and opts.dynamic_options_name:
                dyn_opts_inp_out[inp.name] = opts.dynamic_options_name
        
        ofp_names = []
        ofps_names = []
        if orig_outputs_type is not None:
            if len(dyn_opts_inp_out) > 0:
                # drop dynamic options fields from outputs
                outputs_type = create_model('Outputs', __base__=orig_outputs_type)
                for inp_name, outp_name in dyn_opts_inp_out.items():
                    del outputs_type.model_fields[outp_name]
            
            ofp_names = [outp.name for outp in proc.outputs if isinstance(outp, FilePathOutput)]
            ofps_names = [outp.name for outp in proc.outputs if isinstance(outp, FilePathsOutput)]
            if ofp_names:
                if outputs_type is None:
                    outputs_type = create_model('Outputs', __base__=orig_outputs_type)
                # change field annotation to file id (int) instead of file path (str)
                for outp_name in ofp_names:
                    fp_field = outputs_type.model_fields[outp_name]
                    fp_field.annotation = Optional[int]
                    fp_field.default = None
            if ofps_names:
                if outputs_type is None:
                    outputs_type = create_model('Outputs', __base__=orig_outputs_type)
                # change field annotation to file id (int) instead of file path (str)
                for outp_name in ofps_names:
                    fp_field = inputs_type.model_fields[outp_name]
                    fp_field.annotation = Optional[list[int]]
                    fp_field.default = None

        if outputs_type is None:
            outputs_type = orig_outputs_type
        else:
            outputs_type.model_rebuild(force=True)

        self.inputs_type = inputs_type
        self.outputs_type = outputs_type

        self.filepath_input_names = _FilePathNames(ifp_names, ifps_names, {})
        self.filepath_output_names = _FilePathNames(ofp_names, ofps_names, {})
        self.dyn_opts_inp_out = dyn_opts_inp_out
        
    func: Any
    sig: Signature
    basic: ProcedureInfo
    inputs_type: type[BaseModel]
    outputs_type: type[BaseModel] | None
    filepath_input_names: _FilePathNames
    filepath_output_names: _FilePathNames
    dyn_opts_inp_out: dict[str, str]


def _extract_file_ids(obj: dict[str, Any], names: _FilePathNames):
    ids: set[int] = set()
    for name in names.scalar:
        file_id: int | None = obj[name]
        if file_id:
            ids.add(file_id)

    for name in names.array:
        file_ids: list[int] | None = obj[name]
        if file_ids:
            for file_id in file_ids:
                ids.add(file_id)

    return list(ids)


def _extract_file_paths(obj: dict[str, Any], names: _FilePathNames):
    paths: set[str] = set()
    for name in names.scalar:
        file_path: str = obj[name]
        if file_path:
            paths.add(file_path)

    for name in names.array:
        file_paths: list[str] | None = obj[name]
        if file_paths:
            for file_path in file_paths:
                if file_path:
                    paths.add(file_path)

    return list(paths)


def _map_file_ids_to_paths(obj: dict[str, Any], names: _FilePathNames):
    for inp_name in names.scalar:
        file_id: int | None = obj[inp_name]
        obj[inp_name] = ""
        if file_id:
            obj[inp_name] = _file_id_to_path[file_id]

    for inp_name in names.array:
        file_ids: list[int] | None = obj[inp_name]
        file_paths: list[str] = []
        obj[inp_name] = file_paths
        if file_ids:
            for file_id in file_ids:
                file_paths.append(_file_id_to_path[file_id])


def _map_file_paths_to_ids(obj: dict[str, Any], file_paths_to_ids: dict[str, int], names: _FilePathNames):
    for inp_name in names.scalar:
        file_path = obj[inp_name]
        obj[inp_name] = file_paths_to_ids.get(file_path, None) if file_path else None

    for inp_name in names.array:
        file_paths: list[str] | None = obj[inp_name]
        file_ids: list[int] = []
        obj[inp_name] = file_ids
        if file_paths:
            obj[inp_name] = [file_id for file_id in (file_paths_to_ids.get(
                file_path, None) for file_path in file_paths if file_path) if file_id]


def _context_from_args(kwargs: dict[str, Any], info: _ProcInfoFull):
    user_id = kwargs['x_codekraft_user_id']
    del kwargs['x_codekraft_user_id']

    session_id = kwargs['x_codekraft_session_id']
    del kwargs['x_codekraft_session_id']

    context = ProcedureContext(procedure_id=info.basic.reg_id, user_id=user_id, session_id=session_id)
    kwargs['context'] = context

    return context


async def _preprocess_args(kwargs: dict[str, Any], inputs_dump: dict[str, Any], info: _ProcInfoFull, orig_inputs_type: type[BaseModel]):

    file_ids = _extract_file_ids(inputs_dump, info.filepath_input_names)
    if file_ids:
        assert _ck_client is not None
        await _ck_client.download_files_async(file_ids)
    if orig_inputs_type is not info.inputs_type:
        inputs = inputs_dump
        _map_file_ids_to_paths(inputs, info.filepath_input_names)
        inputs = orig_inputs_type(**inputs)
        kwargs['inputs'] = inputs

def _run_procedure(info: _ProcInfoFull, kwargs: dict[str, Any]):

    assert _ck_client is not None

    action: RunAction = kwargs['action']
    context: ProcedureContext = kwargs['context']
    outputs = None
    status = ""
    try:
        outputs = info.func(**kwargs)
        status = context._get_final_status()
    except Exception as ex:
        logger.error(f"Unhandled exception in procedure {info.basic.name}", exc_info=True)
        status = "LogicError"
        context.report_status(10002, "error", str(ex))
    
    if outputs is not None:
        outputs = outputs.model_dump(mode="json")
    
        for dyn_opts_name in info.dyn_opts_inp_out.values():
            del outputs[dyn_opts_name]

        file_paths = _extract_file_paths(outputs, info.filepath_output_names)
        file_ids ={}
        try:
            file_ids = _ck_client.upload_files(file_paths)
        except Exception as ex:
            logger.error(f"CodeKraft API call to upload output files for {info.basic.name} failed", exc_info=True)
            status = "InternalError"
            context.report_status(10002, "error", f"Failed to store output file(s)\n{str(ex)}")
        _map_file_paths_to_ids(outputs, file_ids, info.filepath_output_names)

        file_names = {v: os.path.basename(k) for k, v in file_ids.items()}
        try:
            _ck_client.store_outputs(info.basic.reg_id, action.run_id, outputs, file_names)
        except Exception as ex:
            logger.error(f"CodeKraft API call to store outputs for {info.basic.name} failed", exc_info=True)
            status = "InternalError"
            context.report_status(10002, "error", f"Failed to store output(s)\n{str(ex)}")
    # if status == "Succeeded" or status == "SucceededWarn":
    #     if context.before_commit:
    #         try:
    #             context.before_commit()
    #             status = context._get_final_status()
    #         except Exception as ex:
    #             # TODO: log the exception
    #             status = "LogicError"
    #             context.report_status(10002, "error", str(ex))
    if status == "Succeeded" or status == "SucceededWarn":
        try:
            context._commit()
        except Exception as ex:
            logger.error(f"__exit__ call failed on one of the context managers for {info.basic.name}", exc_info=True)
            status = "Failed"
            context.report_status(10002, "error", f"Failed to commit\n{str(ex)}")
    else:
        context._rollback(status)

    assert context._run_context is not None
    _ck_client.set_procedure_ended(action.run_id, info.basic.reg_id, status, context._run_context.model_dump())
    
    if info.basic.immediate:
        if info.sig.return_annotation is not info.outputs_type and info.outputs_type is not None:
            if outputs is None:
                outputs = {}
            outputs = info.outputs_type(**outputs)
        return outputs

def _create_run_operation(info: _ProcInfoFull, dependencies: Sequence[Depends] | None):
    orig_params = info.sig.parameters
    orig_inputs_type: type[BaseModel] = orig_params['inputs'].annotation

    params: list[Parameter] = []
    for par in orig_params.values():
        if par.kind == Parameter.POSITIONAL_ONLY:
            raise ValueError(f"positional only argument {par.name} is not supported")
        if par.name == 'inputs':
            params.append(Parameter('inputs', Parameter.POSITIONAL_OR_KEYWORD, annotation=info.inputs_type))
        elif par.name != 'context' and par.name != 'action':
            params.append(par)
    params.append(Parameter('context', Parameter.POSITIONAL_OR_KEYWORD, annotation=_RunContext))
    params.append(Parameter('x_codekraft_user_id', Parameter.POSITIONAL_OR_KEYWORD,
                  annotation=Annotated[int, Header()]))
    params.append(Parameter('x_codekraft_session_id', Parameter.POSITIONAL_OR_KEYWORD,
                  annotation=Annotated[str, Header()]))

    result_type = None
    if info.basic.immediate:
        result_type = create_model('Result', __base__=_BkgRunResult, validations=(
            list[Validation], ...), outputs=(info.outputs_type, ...))
    else:
        params.append(Parameter("background_tasks", Parameter.POSITIONAL_OR_KEYWORD, annotation=BackgroundTasks))
        result_type = _BkgRunResult

    run_sig = info.sig.replace(parameters=params, return_annotation=result_type)
    
    deps = [Depends(_initialize)]
    if dependencies:
        deps.append(dependencies)
    @_router.post("/run/" + info.basic.unique_id, dependencies=deps)
    @_withSignature(run_sig)
    async def run(**kwargs):
        assert _ck_client is not None
        # Preprocess
        run_context: _RunContext = kwargs['context']

        inputs = kwargs['inputs']
        inputs_dump = inputs.model_dump(mode="json")
        
        context = _context_from_args(kwargs, info)
        run_id = await _ck_client.set_procedure_started_async(info.basic.reg_id, info.basic.reg_version, context.user_id, inputs_dump, run_context.model_dump())
        context._run_id = run_id
        context._run_context = run_context
        
        await _preprocess_args(kwargs, inputs_dump, info, orig_inputs_type)

        kwargs['action'] = RunAction(run_id=run_id)

        if info.basic.immediate:
            # Call
            outputs = await run_in_threadpool(_run_procedure, info, kwargs)

            # Postprocess
            return result_type(id=run_id, validations=context._validations, outputs=outputs)
        else:
            background_tasks: BackgroundTasks = kwargs['background_tasks']
            del kwargs['background_tasks']
            background_tasks.add_task(_run_procedure, info, kwargs)
            return _BkgRunResult(id=run_id)

def _update_procedure(info, kwargs):
    # Call the function
    context: ProcedureContext = kwargs['context']
    outputs = None
    try:
        outputs = info.func(**kwargs)
    except Exception as e:
        logger.error(f"Unhandled exception in procedure {info.basic.name}", exc_info=True)
    context._rollback("Failed")
    return outputs

def _create_update_operation(info: _ProcInfoFull, dependencies: Sequence[Depends] | None):
    orig_params = info.sig.parameters
    orig_inputs_type: type[BaseModel] = orig_params['inputs'].annotation

    params: list[Parameter] = []
    for par in orig_params.values():
        if par.kind == Parameter.POSITIONAL_ONLY:
            raise ValueError(f"positional only argument {par.name} is not supported")
        if par.name == 'inputs':
            params.append(Parameter('inputs', Parameter.POSITIONAL_OR_KEYWORD, annotation=info.inputs_type))
        elif par.name == 'action':
            params.append(Parameter('action', Parameter.POSITIONAL_OR_KEYWORD, annotation=_UpdateAction))
        elif par.name != 'context':
            params.append(par)
    params.append(Parameter('x_codekraft_user_id', Parameter.POSITIONAL_OR_KEYWORD,
                  annotation=Annotated[int, Header()]))
    params.append(Parameter('x_codekraft_session_id', Parameter.POSITIONAL_OR_KEYWORD,
                  annotation=Annotated[str, Header()]))

    dyn_opts_type = create_model('DynOpts', **{k: (Optional[list[str]], None)
                                 for k in info.dyn_opts_inp_out})

    result_type = create_model('Result', inputs=(info.inputs_type, ...), dynamic_options=(
        dyn_opts_type, ...), validations=(list[Validation], ...), outputs=(info.outputs_type, ...), file_names=(dict[int, str], ...))

    upd_sig = info.sig.replace(parameters=params, return_annotation=result_type)
    
    deps = [Depends(_initialize)]
    if dependencies:
        deps.append(dependencies)
    @_router.post("/updateui/" + info.basic.unique_id, dependencies=deps)
    @_withSignature(upd_sig)
    async def updateui(**kwargs):
        # Preprocess
        
        inputs = kwargs['inputs']
        inputs_dump = inputs.model_dump(mode="json")
        context = _context_from_args(kwargs, info)
        await _preprocess_args(kwargs, inputs_dump, info, orig_inputs_type)
        inputs = kwargs['inputs']
        
        outputs = await run_in_threadpool(_update_procedure, info, kwargs)

        # Postprocess
        dyn_opts = dyn_opts_type()
        if outputs is not None:
            for in_name, out_name in info.dyn_opts_inp_out.items():
                setattr(dyn_opts, in_name, getattr(outputs, out_name, []))
            if info.sig.return_annotation is not info.outputs_type and info.outputs_type is not None:
                outputs = outputs.model_dump(mode="json")
                _map_file_paths_to_ids(outputs, {}, info.filepath_output_names)
                outputs = info.outputs_type(**outputs)
        elif info.outputs_type is not None:
            outputs = info.outputs_type()
        if orig_inputs_type is not info.inputs_type:
            inputs = inputs.model_dump(mode="json")
            _map_file_paths_to_ids(inputs, _file_id_to_path_rev, info.filepath_input_names)
            inputs = info.inputs_type(**inputs)
        result = result_type(inputs=inputs, dynamic_options=dyn_opts, validations=context._validations, file_names={}, outputs=outputs)

        return result


class _TokenInfo(BaseModel):
    token: str
    token_expiry: datetime

class _SampleFileInfo(BaseModel):
    path: str
    

async def _download_sample_file(input: _SampleFileInfo):
    if _static_path is None:
        raise ValueError("set_static_path must be called at initialization")
    if '../' in input.path or '..\\' in input.path:
        raise ValueError("invalid input path")
    if input.path.startswith('/') or input.path.startswith('\\'):
        raise ValueError("invalid input path")
    full_path = os.path.realpath(os.path.join(_static_path, input.path))

    common = os.path.commonpath([_static_path, full_path])
    if common != _static_path:
        raise ValueError("invalid input path")
    
    return FileResponse(full_path)

class _CodeKraftClient:
    def __init__(self, app: FastAPI) -> None:

        self.ck_url = os.getenv('CODEKRAFT_URL', '')
        self.app_name = os.getenv('CODEKRAFT_KEY', '')
        if self.ck_url:
            if not self.ck_url.endswith('/'):
                self.ck_url = self.ck_url + '/'
            self.token_url = self.ck_url + 'api/extapp/token'
        else:
            raise ValueError(f"Environment variable CODEKRAFT_URL must be set")

        self.session_key = ""
        self.token = ""
        self.token_expiry = None
        self.auth_header = ""
        self.started = False
        app.post("/codekraft/token")(self._accept_token_async)
        app.post("/procedures/downloadsample")(_download_sample_file)

        self.loop = asyncio.get_running_loop()
        self.loop.create_task(_initialize())
        # To call and wait for an async function from within a sync function that runs on the thread pool, use the following
        # asyncio.run_coroutine_threadsafe(some_function_async(), self.loop).result()

    async def request_token_async(self):
        if self.token_expiry is None or (self.token_expiry - datetime.now(timezone.utc)).total_seconds() <= 5.0:
            self.session_key = secrets.token_urlsafe(16)
            await run_in_threadpool(self._post_token_request)

    def _request_token(self):
        if self.token_expiry is None or (self.token_expiry - datetime.now(timezone.utc)).total_seconds() <= 5.0:
            # The token request requires the loop to be running because _accept_token_async will run on the loop
            assert self.loop is not None
            self.session_key = secrets.token_urlsafe(16)
            self._post_token_request()
            
    def _post_token_request(self):
        logger.info(f"requesting fresh codekraft auth token")
        response = requests.post(self.token_url,
                                     json={'app_name': self.app_name, 'random_session_key': self.session_key}, timeout=timeout)
        if not response.ok:
            response.raise_for_status()

    async def _accept_token_async(self, token_info: _TokenInfo) -> None:
        self.token = token_info.token
        self.token_expiry = token_info.token_expiry
        self.auth_header = f"CodeKraftKey {self.session_key}.{self.token}"
        logger.info(f"codekraft auth token received with expiry {self.token_expiry}")
    
    async def start_async(self):
        try:
            await self.request_token_async()
        except:
            logger.error("Failed to get codekraft token", exc_info=True)
            return
        try:
            id_map = await run_in_threadpool(self._post_start)
            for m in _modules.values():
                m._update_registration(id_map)
        except:
            logger.error("Failed to start codekraft integration")
            return
        self.started = True
    
    def _post_start(self):
        data = json.dumps({'modules': list(_modules.values())}, default=vars)
        logger.info(f"registering procedures")
        resp = requests.post(self.ck_url + 'api/extapp/start',
                             headers={'authorization': self.auth_header, 'content-type': 'application/json'}, data=data, timeout=timeout)
        if resp.ok:
            logger.info(f"procedures registered")
            dict = resp.json()
            return {k: (v["id"], v["version"]) for k, v in dict.items()}
        else:
            raise ValueError(f"Failed to start: {resp.text}")

    async def download_files_async(self, ids: list[int]):
        for id in ids:
            if id not in _file_id_to_path or not os.path.exists(_file_id_to_path[id]):
                await self.request_token_async()
                file_path = await run_in_threadpool(self._download_file, id)
                _file_id_to_path[id] = file_path
                _file_id_to_path_rev[file_path] = id
    
    def _download_file(self, id: int):
        resp = requests.get(
            self.ck_url + f'api/extapp/downloadfile/{id}', headers={'authorization': self.auth_header}, stream=True, timeout=timeout)
        if resp.ok:
            cd = resp.headers.get('content-disposition')
            fname = pyrfc6266.parse_filename(cd or "") or "file"
            unique_dir = tempfile.mkdtemp(dir=_file_cache_dir.name)
            file_path = os.path.join(unique_dir, fname)
            with open(file_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=10 * 1024):
                    f.write(chunk)
            return file_path
        else:
            raise ValueError(f"Failed to download file: {resp.text}")
    
    async def set_procedure_started_async(self, id: int, version: int, user_id: int, inputs: Any, run_context: Any):
        await self.request_token_async()
        data = {'id': id, 'version': version, 'user_id': user_id, 'inputs': inputs, 'run_context': run_context}
        return await run_in_threadpool(self._post_proc_started, data)
    
    def _post_proc_started(self, data: dict[str, Any]) -> int:
        resp = requests.post(self.ck_url + 'api/extapp/procstarted',
                             headers={'authorization': self.auth_header}, json=data, timeout=timeout)
        if resp.ok:
            return resp.json()
        else:
            raise ValueError(f"Failed to start the procedure with id {data['id']}: {resp.text}")
        
    def set_procedure_ended(self, run_id: int, proc_id: int, status: str, run_context: dict[str, Any]):
        self._request_token()
        data = {'run_id': run_id, 'procedure_id': proc_id, 'status': status, 'run_context': run_context}
        resp = requests.post(self.ck_url + 'api/extapp/procended',
                             headers={'authorization': self.auth_header}, json=data, timeout=timeout)
        if not resp.ok:
            raise ValueError(f"Failed to end the procedure with id {proc_id}: {resp.text}")
        
    def store_log_entry(self, run_id: int, entry_id: int, entry: dict[str, Any]):
        self._request_token()
        data = {'run_id': run_id, 'entry_id': entry_id, 'entry': entry }
        resp = requests.post(self.ck_url + 'api/extapp/storelogentry',
                             headers={'authorization': self.auth_header}, json=data, timeout=timeout)
        if not resp.ok:
            raise ValueError(f"Failed to write log entry: {resp.text}")
        
    def upload_files(self, paths: list[str]):
        file_path_to_id: dict[str, int] = {}
        for path in paths:
            self._request_token()
            with open(path, 'rb') as file:
                resp = requests.post(self.ck_url + 'api/extapp/uploadfile',
                                 headers={'authorization': self.auth_header}, files={'file': (os.path.basename(path), file)}, timeout=timeout)
            if resp.ok:
                file_path_to_id[path] = resp.json()["id"]
            else:
                raise ValueError(f"Failed to upload file: {resp.text}")
        return file_path_to_id

    def store_outputs(self, proc_id: int, run_id: int, outputs: dict[str, Any], file_names: dict[int, str]):
        self._request_token()
        data = {'run_id': run_id, 'procedure_id': proc_id, 'outputs': outputs, 'file_names': file_names}
        resp = requests.post(self.ck_url + 'api/extapp/storeoutputs',
                             headers={'authorization': self.auth_header}, json=data, timeout=timeout)
        if not resp.ok:
            raise ValueError(f"Failed to write outputs: {resp.text}")

    def send_email(self, record: _SendEmailRecord, *, run_id: int, id: int, immediate: bool, keep_alive: bool):
        self._request_token()
        with open(record.eml_file_path, 'rb') as file:
            resp = requests.post(self.ck_url + 'api/extapp/sendemail',
                                 headers={'authorization': self.auth_header},
                                 data={'run_id': run_id, 
                                       'config_key': record.config_key, 
                                       'id': id, 
                                       'bcc': record.bcc,
                                       'retain': record.retain, 
                                       'retry_hours': record.retry_hours,
                                       'immediate': immediate,
                                       'keep_alive': keep_alive},
                                 files={'file': (os.path.basename(record.eml_file_path), file)},
                                 timeout=timeout)
        if not resp.ok:
            raise ValueError(f"Failed to send email: {resp.text}")
        
_ck_client: _CodeKraftClient | None = None

async def _initialize():
    # This is used as a dependency
    # Making it async ensures that it is called on the main thread and does not require synchronization
    if not _ck_client:
        raise RuntimeError("configure method must be called on ModuleInfo at app startup")
    if _ck_client.started:
        return
    await _ck_client.start_async()  # type: ignore

_all_procedures: dict[Any, ProcedureInfo] = {}

class ModuleInfo:
    def __init__(self, *, name: str, display_name: str):
        self.name = name
        self.display_name = display_name
        self.procedures = []
        _modules[self.name] = self

    name: str
    display_name: str
    procedures: list[ProcedureInfo]

    def _update_registration(self, id_map: dict[str, tuple[int, int]]):
        for proc in self.procedures:
            proc.reg_id, proc.reg_version = id_map[proc.unique_id]
    
    def include_procedures(self, *procs):
        for proc in procs:
            if proc in _all_procedures:
                self.procedures.append(_all_procedures[proc])
            else:
                raise ValueError(f"The function {proc} must be decorated with procedure")

def configure(app: FastAPI, static_path: str):
    app.include_router(_router)

    global _static_path
    _static_path = os.path.realpath(static_path)

    global _ck_client
    if _ck_client is None:
        _ck_client = _CodeKraftClient(app)

    all_errors = [proc.name + ": " + e for m in _modules.values() for proc in m.procedures for e in proc.errors]
    if all_errors:
        raise ValueError("The following errors were encountered in the definitions of functions decorated with procedure:\n" +
                            '\n'.join(all_errors))
    

def procedure(*, unique_id: str, name: str, group="", version: int, immediate=False, inputs_require_initialization=False, page_template: RootWidget | None = None, dependencies: Optional[Sequence[Depends]] = None):

    def decorator(proc_func):

        info = _ProcInfoFull(proc_func, unique_id=unique_id, name=name, group=group, version=version, immediate=immediate, inputs_require_initialization=inputs_require_initialization, page_template=page_template)
        
        _all_procedures[proc_func] = info.basic

        _create_run_operation(info, dependencies)

        _create_update_operation(info, dependencies)

        return proc_func

    return decorator
