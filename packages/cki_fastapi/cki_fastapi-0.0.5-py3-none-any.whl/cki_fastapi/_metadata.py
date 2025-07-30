from abc import ABC, abstractmethod
from dataclasses import dataclass
from inspect import Parameter, Signature
from typing import Annotated, Any, Literal, Optional, Protocol, cast, get_args, get_origin
from types import NoneType, UnionType
from pydantic import BaseModel
from datetime import date

# Rules for ProcedureInputInfo and ProcedureOutputInfo subtypes
# All properties that will be set by the user directly should be constructor arguments
# Input / Output property names should be unique across all input / output subtypes respectively.
# Properties with the same name should have the same type, meaning, and default value across all input / output subtypes
# Property names should be in snake case
# type must be the first property so that it is serialized first

class ProcedureInputInfo:
    type: str
    name: str

    def get_TextInputOptions(self: Any):
        try:
            return TextInputOptions(self.must_match_options, self.static_options, self.db_options, self.dynamic_options_name)
        except AttributeError:
            return None


class ProcedureOutputInfo:
    type: str
    name: str


class NumberInput(ProcedureInputInfo):
    def __init__(self, *, required=True, readonly=False, trigger_update=False, label: str | None = None, tooltip: str | None = None, placeholder: str | None = None, display_format=""):
        super().__init__()
        self.type = "number"
        self.required = required
        self.readonly = readonly
        self.trigger_update = trigger_update
        self.label = label
        self.tooltip = tooltip
        self.placeholder = placeholder
        self.display_format = display_format


class DateInput(ProcedureInputInfo):
    def __init__(self, *, required=True, readonly=False, trigger_update=False, label: str | None = None, tooltip: str | None = None):
        super().__init__()
        self.type = "date"
        self.required = required
        self.readonly = readonly
        self.trigger_update = trigger_update
        self.label = label
        self.tooltip = tooltip


class DbOptions:
    def __init__(self, *, connection_name: str, schema: str, table: str, column: str, group_column="", live_filter: Literal["contains", "prefix", "word_prefix"] = "contains"):
        self.connection_name = connection_name
        self.schema = schema
        self.table = table
        self.column = column
        self.group_column = group_column
        self.live_filter = live_filter


@dataclass
class TextInputOptions:
    must_match_options: bool
    static_options: list[str] | None
    db_options: DbOptions | None
    dynamic_options_name: str


class TextInput(ProcedureInputInfo):
    def __init__(self, *, required=True, readonly=False, trigger_update=False, label: str | None = None, tooltip: str | None = None, placeholder: str | None = None, multiline=False, must_match_options=False, static_options: list[str] | None = None, db_options: DbOptions | None = None, dynamic_options_output_name: str = ""):
        super().__init__()
        self.type = "text"
        self.required = required
        self.readonly = readonly
        self.label = label
        self.tooltip = tooltip
        self.placeholder = placeholder
        self.multiline = multiline
        self.trigger_update = trigger_update
        self.must_match_options = must_match_options
        self.static_options = static_options
        self.db_options = db_options
        self.dynamic_options_name = dynamic_options_output_name


class TextListInput(ProcedureInputInfo):
    def __init__(self, *, required=True, readonly=False, trigger_update=False, label: str | None = None, tooltip: str | None = None, must_match_options=False, static_options: list[str] | None = None, db_options: DbOptions | None = None, dynamic_options_output_name: str = ""):
        super().__init__()
        self.type = "textlist"
        self.required = required
        self.readonly = readonly
        self.label = label
        self.tooltip = tooltip
        self.trigger_update = trigger_update
        self.must_match_options = must_match_options
        self.static_options = static_options
        self.db_options = db_options
        self.dynamic_options_name = dynamic_options_output_name


class BooleanInput(ProcedureInputInfo):
    def __init__(self, *, required=True, readonly=False, trigger_update=False, label: str | None = None, tooltip: str | None = None):
        super().__init__()
        self.type = "boolean"
        self.required = required
        self.readonly = readonly
        self.label = label
        self.tooltip = tooltip
        self.trigger_update = trigger_update


class FilePathInput(ProcedureInputInfo):
    def __init__(self, *, required=True, readonly=False, trigger_update=False, label: str | None = None, tooltip: str | None = None, file_types: list[str], sample_file_names: list[str] | None = None):
        super().__init__()
        self.type = "filepath"
        self.required = required
        self.readonly = readonly
        self.trigger_update = trigger_update
        self.label = label
        self.tooltip = tooltip
        self.file_types = file_types
        self.sample_file_names = sample_file_names


class FilePathsInput(ProcedureInputInfo):
    def __init__(self, *, required=True, readonly=False, trigger_update=False, label: str | None = None, tooltip: str | None = None, file_types: list[str], sample_file_names: list[str] | None = None):
        super().__init__()
        self.type = "filepaths"
        self.required = required
        self.readonly = readonly
        self.trigger_update = trigger_update
        self.label = label
        self.tooltip = tooltip
        self.file_types = file_types
        self.sample_file_names = sample_file_names


class TableInput(ProcedureInputInfo):
    def __init__(self, *, required=True, readonly=False, trigger_update=False, label: str | None = None, tooltip: str | None = None, can_add_rows=True, can_delete_rows=True):
        super().__init__()
        self.type = "table"
        self.required = required
        self.readonly = readonly
        self.trigger_update = trigger_update
        self.label = label
        self.tooltip = tooltip
        self.can_add_rows = can_add_rows
        self.can_delete_rows = can_delete_rows
        self.columns = []

    columns: list[ProcedureInputInfo]


class NumberOutput(ProcedureOutputInfo):
    def __init__(self, *, label: str | None = None, tooltip: str | None = None, display_format=""):
        super().__init__()
        self.type = "number"
        self.label = label
        self.tooltip = tooltip
        self.display_format = display_format


class DateOutput(ProcedureOutputInfo):
    def __init__(self, label: str | None = None, tooltip: str | None = None):
        super().__init__()
        self.type = "date"
        self.label = label
        self.tooltip = tooltip


class BooleanOutput(ProcedureOutputInfo):
    def __init__(self, label: str | None = None, tooltip: str | None = None):
        super().__init__()
        self.type = "boolean"
        self.label = label
        self.tooltip = tooltip


class TextOutput(ProcedureOutputInfo):
    def __init__(self, label: str | None = None, tooltip: str | None = None, multiline=False, preformatted=False):
        super().__init__()
        self.type = "text"
        self.label = label
        self.tooltip = tooltip
        self.multiline = multiline
        self.preformatted = preformatted


class FilePathOutput(ProcedureOutputInfo):
    def __init__(self, *, file_types: list[str], label: str | None = None, tooltip: str | None = None):
        super().__init__()
        self.type = "filepath"
        self.file_types = file_types
        self.label = label
        self.tooltip = tooltip


class FilePathsOutput(ProcedureOutputInfo):
    def __init__(self, *, file_types: list[str], label: str | None = None, tooltip: str | None = None):
        super().__init__()
        self.type = "filepaths"
        self.file_types = file_types
        self.label = label
        self.tooltip = tooltip


class TableOutput(ProcedureOutputInfo):
    def __init__(self, label: str | None = None, tooltip: str | None = None):
        super().__init__()
        self.type = "table"
        self.columns = []
        self.label = label
        self.tooltip = tooltip

    columns: list[ProcedureOutputInfo]


def _get_parameter_type(p: Parameter):
    if get_origin(p.annotation) is Annotated:
        inputs_type, _ = get_args(p.annotation)
    else:
        inputs_type = p.annotation
    return inputs_type

def _extractOptionalType(t):
    if get_origin(t) is UnionType:
        ts = get_args(t)
        if len(ts) == 2:
            if ts[0] is type(None):
                return ts[1], True
            elif ts[1] is type(None):
                return ts[0], True
    return t, False


def _get_input_meta(field_info):
    f_type = field_info.annotation
    if field_info.metadata:
        for m in field_info.metadata:
            if isinstance(m, ProcedureInputInfo):
                return m
    if f_type == Optional[float]:
        return NumberInput()
    elif f_type == Optional[date]:
        return DateInput()
    elif f_type == Optional[bool]:
        return BooleanInput()
    elif f_type == str:
        return TextInput()
    elif f_type == Optional[list[str]]:
        return TextListInput()
    else:
        f_type_non_opt, is_opt = _extractOptionalType(f_type)
        if get_origin(f_type_non_opt) is list:
            f_row_type, *others = get_args(f_type_non_opt)
            if len(others) == 0 and issubclass(f_row_type, BaseModel):
                return TableInput()
    return None

def _process_input_field_type(model_name, f_meta: ProcedureInputInfo, f_type, errors: list[str]):
    f_name = f_meta.name
    if isinstance(f_meta, TableInput):
        f_type_non_opt, is_opt = _extractOptionalType(f_type)
        if get_origin(f_type_non_opt) is list:
            f_row_type, *others = get_args(f_type_non_opt)
            if len(others) == 0 and issubclass(f_row_type, BaseModel):
                _set_table_input_columns(f_meta, f_row_type, errors)
            else:
                errors.append(
                    f"The type for input field {model_name}.{f_name} should be list[sub_class_of_BaseModel] | None because it is annotated with TableInput")
        else:
            errors.append(
                f"The type for input field {model_name}.{f_name} should be list[sub_class_of_BaseModel] | None because it is annotated with TableInput")
    elif isinstance(f_meta, NumberInput):
        if f_type != Optional[float]:
            errors.append(
                f"The type for input field {model_name}.{f_name} should be float | None instead of {f_type} because it is annotated with NumberInput")
    elif isinstance(f_meta, DateInput):
        if f_type != Optional[date]:
            errors.append(
                f"The type for input field {model_name}.{f_name} should be date | None instead of {f_type} because it is annotated with DateInput")
    elif isinstance(f_meta, BooleanInput):
        if f_type != Optional[bool]:
            errors.append(
                f"The type for input field {model_name}.{f_name} should be bool | None instead of {f_type} because it is annotated with BooleanInput")
    elif isinstance(f_meta, TextInput):
        if f_type != str and f_type != str | None:
            errors.append(
                f"The type for input field {model_name}.{f_name} should be str instead of {f_type} because it is annotated with TextInput")
    elif isinstance(f_meta, TextListInput):
        if f_type != list[str] | None:
            errors.append(
                f"The type for input field {model_name}.{f_name} should be list[str] | None instead of {f_type} because it is annotated with TextListInput")
    elif isinstance(f_meta, FilePathInput):
        if f_type != str and f_type != str | None:
            errors.append(
                f"The type for input field {model_name}.{f_name} should be str instead of {f_type} because it is annotated with FilePathInput")
    elif isinstance(f_meta, FilePathsInput):
        if f_type != list[str] | None:
            errors.append(
                f"The type for input field {model_name}.{f_name} should be list[str] | None instead of {f_type} because it is annotated with FilePathsInput")
    else:
        raise ValueError(f"Input of type {type(f_meta)} was encountered in {
                         model_name}.{f_name} but it is not yet supported")


def _process_output_field_type(model_name: str, f_meta: ProcedureOutputInfo, f_type, errors: list[str]):
    f_name = f_meta.name
    if isinstance(f_meta, TableOutput):
        f_type_non_opt, is_opt = _extractOptionalType(f_type)
        if get_origin(f_type_non_opt) is list:
            f_row_type, *others = get_args(f_type_non_opt)
            if len(others) == 0 and issubclass(f_row_type, BaseModel):
                _set_table_output_columns(f_meta, f_row_type, errors)
            else:
                errors.append(
                    f"The type for output field {model_name}.{f_name} should be list[sub_class_of_BaseModel] | None because it is annotated with TableOutput")
        else:
            errors.append(
                f"The type for output field {model_name}.{f_name} should be list[sub_class_of_BaseModel] | None because it is annotated with TableOutput")
    elif isinstance(f_meta, NumberOutput):
        if f_type != Optional[float]:
            errors.append(
                f"The type for input field {model_name}.{f_name} should be float | None instead of {f_type} because it is annotated with NumberOutput")
    elif isinstance(f_meta, DateOutput):
        if f_type != Optional[date]:
            errors.append(
                f"The type for input field {model_name}.{f_name} should be date | None instead of {f_type} because it is annotated with DateOutput")
    elif isinstance(f_meta, BooleanOutput):
        if f_type != Optional[bool]:
            errors.append(
                f"The type for input field {model_name}.{f_name} should be bool | None instead of {f_type} because it is annotated with BooleanOutput")
    elif isinstance(f_meta, TextOutput):
        if f_type != str and f_type != str | None:
            errors.append(
                f"The type for input field {model_name}.{f_name} should be str instead of {f_type} because it is annotated with TextOutput")
    elif isinstance(f_meta, FilePathOutput):
        if f_type != str and f_type != str | None:
            errors.append(
                f"The type for input field {model_name}.{f_name} should be str instead of {f_type} because it is annotated with FilePathOutput")
    elif isinstance(f_meta, FilePathsOutput):
        if f_type != list[str] | None:
            errors.append(
                f"The type for input field {model_name}.{f_name} should be list[str] | None instead of {f_type} because it is annotated with FilePathsOutput")
    else:
        raise ValueError(f"Input of type {type(f_meta)} was encountered in {model_name}.{f_name} is not yet supported")


def _get_output_meta(field_info):
    f_type = field_info.annotation
    if field_info.metadata:
        for m in field_info.metadata:
            if isinstance(m, ProcedureOutputInfo):
                return m
    if f_type == Optional[float]:
        return NumberOutput()
    elif f_type == Optional[date]:
        return DateOutput()
    elif f_type == Optional[bool]:
        return BooleanOutput()
    elif f_type == str:
        return TextOutput()
    else:
        f_type_non_opt, is_opt = _extractOptionalType(f_type)
        if get_origin(f_type_non_opt) is list:
            f_row_type, *others = get_args(f_type_non_opt)
            if len(others) == 0 and issubclass(f_row_type, BaseModel):
                return TableOutput()
    return None


def _set_table_input_columns(input: TableInput, row_type: type[BaseModel], errors: list[str]):
    fields = row_type.model_fields
    for f_name, f_info in fields.items():
        f_type = f_info.annotation
        f_meta = _get_input_meta(f_info)
        if f_meta:
            f_meta.name = f_name
            _process_input_field_type(row_type.__name__, f_meta, f_type, errors)
            input.columns.append(f_meta)
        else:
            errors.append(f"No metadata found for field {f_name} of input field {
                          input.name} and its type is not one of the supported types for which metadata can be inferred")


def _set_table_output_columns(output: TableOutput, row_type: type[BaseModel], errors: list[str]):
    fields = row_type.model_fields
    for f_name, f_info in fields.items():
        f_type = f_info.annotation
        f_meta = _get_output_meta(f_info)
        if f_meta:
            f_meta.name = f_name
            _process_output_field_type(row_type.__name__, f_meta, f_type, errors)
            output.columns.append(f_meta)
        else:
            errors.append(f"No metadata found for field {f_name} of input field {
                          output.name} and its type is not one of the supported types for which metadata can be inferred")


class PropertyName[T](str):
    pass


type WidgetName = str


class PropertySetter[T]:
    def __init__(self, target: 'PageWidget', property: PropertyName[T]):
        self.target = target
        self.property = property

    def value(self, v: T):
        self.target.properties[self.property] = v


def _set_primitive(d: dict[str, Any] | None, key: str, value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if d is None:
        d = {}
    d[key] = value
    return d

class Dumpable(Protocol):
    def dump(self) -> dict[str, Any] | None:
        pass

def _set_dumpable(d: dict[str, Any] | None, key: str, dumpable: Dumpable | None) -> dict[str, Any] | None:
    return _set_primitive(d, key, None if dumpable is None else dumpable.dump())
    


type WidgetAlignment = Literal["stretch", "start", "end", "center"]

# Naming conventions for WidgetsLayout subtypes
# Properties for widget name(s) should be widgets, widget_*, or widgets_*
# It should be possible to set all properties via the constructor
# Property names and corresponding constructor argument names should match except for widget name(s)

class WidgetsLayout(ABC):

    @abstractmethod
    def _dump_override(self, d: dict[str, Any]) -> None:
        pass

    def dump(self):
        d: dict[str, Any] = {}
        d["type"] = type(self).__name__
        self._dump_override(d)
        if len(d) <= 1:
            return None
        return d


class StackLayout(WidgetsLayout):
    def __init__(self, widgets: list[WidgetName] | None, *, h_align_items: WidgetAlignment | None = None, gap: str | None = None) -> None:
        self.widgets = widgets
        self.h_align_items = h_align_items
        self.gap = gap
        # Keep in sync with _dump_override

    def _dump_override(self, d: dict[str, Any]):
        super()._dump_override(d)
        _set_primitive(d, "widgets", self.widgets)
        _set_primitive(d, "h_align_items", self.h_align_items)
        _set_primitive(d, "gap", self.gap)

    h_align: PropertyName[WidgetAlignment] = PropertyName("StackLayout.h_align")


class WrapLayout(WidgetsLayout):
    def __init__(self, *, start: list[WidgetName] | None, end: list[WidgetName] | None, v_align_items: WidgetAlignment | None = None, gap: str | None = None) -> None:
        self.widgets_start = start
        self.widgets_end = end
        self.v_align_items = v_align_items
        self.gap = gap
        # Keep in sync with _dump_override

    def _dump_override(self, d: dict[str, Any]):
        super()._dump_override(d)
        _set_primitive(d, "widgets_start", self.widgets_start)
        _set_primitive(d, "widgets_end", self.widgets_end)
        _set_primitive(d, "v_align_items", self.v_align_items)
        _set_primitive(d, "gap", self.gap)

    v_align: PropertyName[WidgetAlignment] = PropertyName("WrapLayout.v_align")


class ColumnLayout(WidgetsLayout):
    def __init__(self, *, start: list[WidgetName] | None, fill: WidgetName, end: list[WidgetName] | None = None, h_align_items: WidgetAlignment | None = None, gap: str | None = None):
        self.widgets_start = start
        self.widget_fill = fill
        self.widgets_end = end
        self.h_align_items = h_align_items
        self.gap = gap
        # Keep in sync with _dump_override

    def _dump_override(self, d: dict[str, Any]):
        super()._dump_override(d)
        _set_primitive(d, "widgets_start", self.widgets_start)
        _set_primitive(d, "widget_fill", self.widget_fill)
        _set_primitive(d, "widgets_end", self.widgets_end)
        _set_primitive(d, "h_align_items", self.h_align_items)
        _set_primitive(d, "gap", self.gap)

    h_align: PropertyName[WidgetAlignment] = PropertyName("ColumnLayout.h_align")


class RowLayout(WidgetsLayout):
    def __init__(self, *, start: list[WidgetName] | None, fill: WidgetName, end: list[WidgetName] | None = None, v_align_items: WidgetAlignment | None = None, gap: str | None = None):
        self.widgets_start = start
        self.widget_fill = fill
        self.widgets_end = end
        self.v_align_items = v_align_items
        self.gap = gap
        # Keep in sync with _dump_override

    def _dump_override(self, d: dict[str, Any]):
        super()._dump_override(d)
        _set_primitive(d, "widgets_start", self.widgets_start)
        _set_primitive(d, "widget_fill", self.widget_fill)
        _set_primitive(d, "widgets_end", self.widgets_end)
        _set_primitive(d, "v_align_items", self.v_align_items)
        _set_primitive(d, "gap", self.gap)

    v_align: PropertyName[WidgetAlignment] = PropertyName("RowLayout.v_align")


class SplitLayout(WidgetsLayout):
    def __init__(self, *, start: WidgetName | None, end: WidgetName | None, initial_orientation: Literal["horizontal", "vertical"], resize: Literal["start", "end", "auto"] | None = None, initial_size: str | None = None):
        self.widget_start = start
        self.widget_end = end
        self.orientation = initial_orientation
        self.resize = resize
        self.initial_size = initial_size
        # Keep in sync with _dump_override

    def _dump_override(self, d: dict[str, Any]):
        super()._dump_override(d)
        _set_primitive(d, "widget_start", self.widget_start)
        _set_primitive(d, "widget_end", self.widget_end)
        _set_primitive(d, "orientation", self.orientation)
        _set_primitive(d, "resize", self.resize)
        _set_primitive(d, "initial_size", self.initial_size)


class ClipLayout(WidgetsLayout):
    def __init__(self, widgets: list[WidgetName] | None, *, v_align_items: WidgetAlignment | None = None, gap: str | None = None) -> None:
        self.widgets = widgets
        self.v_align_items = v_align_items
        self.gap = gap
        # Keep in sync with _dump_override

    def _dump_override(self, d: dict[str, Any]):
        super()._dump_override(d)
        _set_primitive(d, "widgets", self.widgets)
        _set_primitive(d, "v_align_items", self.v_align_items)
        _set_primitive(d, "gap", self.gap)

    v_align: PropertyName[WidgetAlignment] = PropertyName("ClipLayout.v_align")


class FormLayout(WidgetsLayout):
    def __init__(self, widgets: list[WidgetName] | None, *, gap: str | None = None) -> None:
        self.widgets = widgets
        self.gap = gap
        # Keep in sync with _dump_override

    def _dump_override(self, d: dict[str, Any]):
        super()._dump_override(d)
        _set_primitive(d, "widgets", self.widgets)
        _set_primitive(d, "gap", self.gap)


class PageWidget(ABC):
    def __init__(self):
        self.visible: bool | None = None
        self.disable_default_styles: Literal["all", "self", "no", "inherit"] | None = None
        self.properties: dict[str, Any] = {}

    def property[T](self, name: PropertyName[T]) -> PropertySetter[T]:
        return PropertySetter(self, name)

    def style(self, property: str) -> PropertySetter[str]:
        return PropertySetter(self, PropertyName[str](f"Style.{property}"))

    def _dump_override(self, d: dict[str, Any]) -> None:
        pass

    def dump(self):
        d: dict[str, Any] = {}
        d["type"] = type(self).__name__
        d["name"] = self.name  # type: ignore
        _set_primitive(d, "visible", self.visible)
        _set_primitive(d, "disable_default_styles", self.disable_default_styles)
        p: dict[str, Any] | None = None
        for k, v in self.properties.items():
            p = _set_primitive(p, k, v)
        _set_primitive(d, "properties", p)
        self._dump_override(d)
        if len(d) <= 2:
            return None
        return d


ButtonSize = Literal["small", "medium", "large"]

class Button(PageWidget, ABC):
    def __init__(self, *, label: str | None = None, size: ButtonSize | None = None):
        super().__init__()
        self.label = label
        self.size = size
        # Keep in sync with _dump_override

    def _dump_override(self, d: dict[str, Any]):
        super()._dump_override(d)
        _set_primitive(d, "label", self.label)
        _set_primitive(d, "size", self.size)


class ViewDraftsWidget(PageWidget):
    def __init__(self):
        super().__init__()
        # Keep in sync with _dump_override

    # def _dump_override(self, d: dict[str, Any]):
    #     super()._dump_override(d)
    #     dump instance fields

    name: Literal["view_drafts"] = "view_drafts"


class CancelButton(Button):
    def __init__(self):
        super().__init__()
        # Keep in sync with _dump_override

    # def _dump_override(self, d: dict[str, Any]):
    #     super()._dump_override(d)
    #     dump instance fields

    name: Literal["cancel_button"] = "cancel_button"


class RetryButton(Button):
    def __init__(self):
        super().__init__()
        # Keep in sync with _dump_override

    # def _dump_override(self, d: dict[str, Any]):
    #     super()._dump_override(d)
    #     dump instance fields

    name: Literal["retry_button"] = "retry_button"


class EditInputsButton(Button):
    def __init__(self):
        super().__init__()
        # Keep in sync with _dump_override

    # def _dump_override(self, d: dict[str, Any]):
    #     super()._dump_override(d)
    #     dump instance fields

    name: Literal["edit_inputs_button"] = "edit_inputs_button"


class NewInputsButton(Button):
    def __init__(self):
        super().__init__()
        # Keep in sync with _dump_override

    # def _dump_override(self, d: dict[str, Any]):
    #     super()._dump_override(d)
    #     dump instance fields

    name: Literal["new_inputs_button"] = "new_inputs_button"


class ShowInListButton(Button):
    def __init__(self):
        super().__init__()
        # Keep in sync with _dump_override

    # def _dump_override(self, d: dict[str, Any]):
    #     super()._dump_override(d)
    #     dump instance fields

    name: Literal["show_in_list_button"] = "show_in_list_button"


class RunDetailsTitleWidget(PageWidget):
    def __init__(self):
        super().__init__()
        # Keep in sync with _dump_override

    # def _dump_override(self, d: dict[str, Any]):
    #     super()._dump_override(d)
    #     dump instance fields

    name: Literal["run_details_title"] = "run_details_title"


class RunStatusWidget(PageWidget):
    def __init__(self):
        super().__init__()
        # Keep in sync with _dump_override

    # def _dump_override(self, d: dict[str, Any]):
    #     super()._dump_override(d)
    #     dump instance fields

    name: Literal["run_status"] = "run_status"


class RunDetailsDateWidget(PageWidget):
    def __init__(self):
        super().__init__()
        # Keep in sync with _dump_override

    # def _dump_override(self, d: dict[str, Any]):
    #     super()._dump_override(d)
    #     dump instance fields

    name: Literal["run_details_date"] = "run_details_date"


class RunDetailsUserWidget(PageWidget):
    def __init__(self):
        super().__init__()
        # Keep in sync with _dump_override

    # def _dump_override(self, d: dict[str, Any]):
    #     super()._dump_override(d)
    #     dump instance fields

    name: Literal["run_details_user"] = "run_details_user"


class RunDetailsWidget(PageWidget):
    def __init__(self):
        super().__init__()

        self.title = RunDetailsTitleWidget()
        self.status = RunStatusWidget()
        self.date = RunDetailsDateWidget()
        self.user = RunDetailsUserWidget()
        self.cancel_button = CancelButton()
        self.retry_button = RetryButton()
        self.edit_inputs_button = EditInputsButton()
        self.new_inputs_button = NewInputsButton()
        self.show_in_list_button = ShowInListButton()

        # Keep in sync with _dump_override

        self.layout: WidgetsLayout | None = None

    def _dump_override(self, d: dict[str, Any]):
        super()._dump_override(d)
        _set_dumpable(d, "title", self.title)
        _set_dumpable(d, "status", self.status)
        _set_dumpable(d, "date", self.date)
        _set_dumpable(d, "user", self.user)
        _set_dumpable(d, "cancel_button", self.cancel_button)
        _set_dumpable(d, "retry_button", self.retry_button)
        _set_dumpable(d, "edit_inputs_button", self.edit_inputs_button)
        _set_dumpable(d, "new_inputs_button", self.new_inputs_button)
        _set_dumpable(d, "show_in_list_button", self.show_in_list_button)

        _set_dumpable(d, "layout", self.layout)

    name: Literal["run_details"] = "run_details"


class RunLogEntriesWidget(PageWidget):
    def __init__(self):
        super().__init__()
        # Keep in sync with _dump_override

    # def _dump_override(self, d: dict[str, Any]):
    #     super()._dump_override(d)
    #     dump instance fields

    name: Literal["run_log_entries"] = "run_log_entries"


class InputWidget(PageWidget):
    def __init__(self, input_name: str):
        super().__init__()
        self.name = f"inputs_{input_name}"
        self.label_position: Literal["top", "side"] | None = None
        self.show_label: bool | None = None
        # Keep in sync with _dump_override

    def _dump_override(self, d: dict[str, Any]):
        super()._dump_override(d)
        _set_primitive(d, "label_position", self.label_position)
        _set_primitive(d, "show_label", self.show_label)


class OutputWidget(PageWidget):
    def __init__(self, output_name: str):
        super().__init__()
        self.name = f"outputs_{output_name}"
        self.label_position: Literal["top", "side"] | None = None
        self.show_label: bool | None = None
        # Keep in sync with _dump_override

    def _dump_override(self, d: dict[str, Any]):
        super()._dump_override(d)
        _set_primitive(d, "label_position", self.label_position)
        _set_primitive(d, "show_label", self.show_label)


class TextWidget(PageWidget):
    def __init__(self, identifier: str, *, content: str):
        super().__init__()
        self.name = f"widgets_{identifier}"
        self.content = content
        self.color: str | None = None
        self.background_color: str | None = None
        # Keep in sync with _dump_override

    def _dump_override(self, d: dict[str, Any]):
        super()._dump_override(d)
        _set_primitive(d, "content", self.content)
        _set_primitive(d, "color", self.color)
        _set_primitive(d, "background_color", self.background_color)


class ActionButton(Button):
    def __init__(self, identifier: str, *, label: str, size: ButtonSize | None = None):
        super().__init__(label=label, size=size)
        self.name = f"widgets_{identifier}"
        # Keep in sync with _dump_override

    # def _dump_override(self, d: dict[str, Any]):
    #     super()._dump_override(d)
    #     dump instance fields


class InputsWidget(PageWidget):
    def __init__(self):
        super().__init__()

        self._inputs: dict[str, InputWidget] = {}

        self.layout: WidgetsLayout | None = None
        # Keep in sync with _dump_override

    def _dump_override(self, d: dict[str, Any]):
        super()._dump_override(d)
        p: dict[str, Any] | None = None
        for k, v in self._inputs.items():
            p = _set_dumpable(p, k, v)
        _set_primitive(d, "widgets", p)
        _set_dumpable(d, "layout", self.layout)

    name: Literal["inputs"] = "inputs"

    def get(self, input_name: str) -> InputWidget:
        if input_name not in self._inputs:
            item = InputWidget(input_name)
            self._inputs[input_name] = item
            return item
        item = self._inputs[input_name]
        return item


class OutputsWidget(PageWidget):
    def __init__(self):
        super().__init__()

        self._outputs: dict[str, OutputWidget] = {}

        self.layout: WidgetsLayout | None = None
        # Keep in sync with _dump_override

    def _dump_override(self, d: dict[str, Any]):
        super()._dump_override(d)
        p: dict[str, Any] | None = None
        for k, v in self._outputs.items():
            p = _set_dumpable(p, k, v)
        _set_primitive(d, "widgets", p)
        _set_dumpable(d, "layout", self.layout)

    name: Literal["outputs"] = "outputs"

    def get(self, output_name: str) -> OutputWidget:
        if output_name not in self._outputs:
            item = OutputWidget(output_name)
            self._outputs[output_name] = item
            return item
        item = self._outputs[output_name]
        return item


class MainAreaWidget(PageWidget):
    def __init__(self):
        super().__init__()

        self.inputs = InputsWidget()
        self.outputs = OutputsWidget()
        # Keep in sync with _dump_override

        self.layout: WidgetsLayout | None = None

    def _dump_override(self, d: dict[str, Any]):
        super()._dump_override(d)
        _set_dumpable(d, "inputs", self.inputs)
        _set_dumpable(d, "outputs", self.outputs)
        _set_dumpable(d, "layout", self.layout)

    name: Literal["main_area"] = "main_area"


class ApprovalStatusWidget(PageWidget):
    def __init__(self):
        super().__init__()
        # Keep in sync with _dump_override

    # def _dump_override(self, d: dict[str, Any]):
    #     super()._dump_override(d)
    #     dump instance fields

    name: Literal["approval_status"] = "approval_status"


class ClearInputsButton(Button):
    def __init__(self):
        super().__init__()
        # Keep in sync with _dump_override

    # def _dump_override(self, d: dict[str, Any]):
    #     super()._dump_override(d)
    #     dump instance fields

    name: Literal["clear_inputs"] = "clear_inputs"


class RunButton(Button):
    def __init__(self):
        super().__init__()
        # Keep in sync with _dump_override

    # def _dump_override(self, d: dict[str, Any]):
    #     super()._dump_override(d)
    #     dump instance fields

    name: Literal["run_button"] = "run_button"


class RejectButton(Button):
    def __init__(self):
        super().__init__()
        # Keep in sync with _dump_override

    # def _dump_override(self, d: dict[str, Any]):
    #     super()._dump_override(d)
    #     dump instance fields

    name: Literal["reject_button"] = "reject_button"


class SaveDraftButton(Button):
    def __init__(self):
        super().__init__()
        # Keep in sync with _dump_override

    # def _dump_override(self, d: dict[str, Any]):
    #     super()._dump_override(d)
    #     dump instance fields

    name: Literal["save_draft_button"] = "save_draft_button"


class ActionsWidget(PageWidget):
    def __init__(self):
        super().__init__()

        self.clear_inputs_button = ClearInputsButton()
        self.run_button = RunButton()
        self.reject_button = RejectButton()
        self.save_draft_button = SaveDraftButton()
        # Keep in sync with _dump_override

        self.layout: WidgetsLayout | None = None

    def _dump_override(self, d: dict[str, Any]):
        super()._dump_override(d)
        _set_dumpable(d, "clear_inputs_button", self.clear_inputs_button)
        _set_dumpable(d, "run_button", self.run_button)
        _set_dumpable(d, "reject_button", self.reject_button)
        _set_dumpable(d, "save_draft_button", self.save_draft_button)
        _set_dumpable(d, "layout", self.layout)

    name: Literal["actions"] = "actions"


class ContainerWidget(PageWidget):
    def __init__(self, identifier: str, layout: WidgetsLayout):
        super().__init__()
        self.name = f"widgets_{identifier}"
        self.layout = layout
        # Keep in sync with _dump_override


    def _dump_override(self, d: dict[str, Any]):
        super()._dump_override(d)
        _set_dumpable(d, "layout", self.layout)


class RootWidget(PageWidget):
    def __init__(self):
        super().__init__()

        self.view_drafts = ViewDraftsWidget()
        self.run_details = RunDetailsWidget()
        self.run_log_entries = RunLogEntriesWidget()
        self.main_area = MainAreaWidget()
        self.approval_status = ApprovalStatusWidget()
        self.actions = ActionsWidget()
        self._widgets: dict[str, PageWidget] = {}

        self.layout: WidgetsLayout | None = None

    def text(self, identifier: str, *, content: str) -> TextWidget:
        if identifier not in self._widgets:
            item = TextWidget(identifier, content=content)
            self._widgets[identifier] = item
            return item
        raise ValueError(f"A widget with identifier {identifier} has already been added")

    def button(self, identifier: str, *, label: str, size: ButtonSize | None = None) -> ActionButton:
        if identifier not in self._widgets:
            item = ActionButton(identifier, label=label, size=size)
            self._widgets[identifier] = item
            return item
        raise ValueError(f"A widget with identifier {identifier} has already been added")

    def container(self, identifier: str, layout: WidgetsLayout) -> ContainerWidget:
        if identifier not in self._widgets:
            item = ContainerWidget(identifier, layout)
            self._widgets[identifier] = item
            return item
        raise ValueError(f"A widget with identifier {identifier} has already been added")

    def _dump_override(self, d: dict[str, Any]):
        super()._dump_override(d)
        _set_dumpable(d, "view_drafts", self.view_drafts)
        _set_dumpable(d, "run_details", self.run_details)
        _set_dumpable(d, "run_log_entries", self.run_log_entries)
        _set_dumpable(d, "main_area", self.main_area)
        _set_dumpable(d, "approval_status", self.approval_status)
        _set_dumpable(d, "actions", self.actions)

        p: dict[str, Any] | None = None
        for k, v in self._widgets.items():
            p = _set_dumpable(p, k, v)
        _set_primitive(d, "widgets", p)

        _set_dumpable(d, "layout", self.layout)

    name: Literal["root"] = "root"

class ProcedureInfo:
    def __init__(self, proc_sig: Signature, *, unique_id: str, name: str, group: str, version: int, immediate, inputs_require_initialization, page_template: RootWidget | None):
        self.reg_id = None  # type: ignore
        self.reg_version = None  # type: ignore

        # The two fields above would always be set before the procedure can be run but are set at the point of registration.

        self.unique_id = unique_id.lower()
        self.name = name
        self.group = group
        self.version = version
        self.immediate = immediate
        self.inputs_require_initialization = inputs_require_initialization

        self.errors = []
        self.inputs = []
        self.outputs = []

        self.page_template = page_template.dump() if page_template else None

        dyn_output_names: set[str] = set()
        for k, p in proc_sig.parameters.items():
            if k == "inputs":
                inputs_type = _get_parameter_type(p)
                if issubclass(inputs_type, BaseModel):
                    fields = inputs_type.model_fields
                    for f_name, f_info in fields.items():
                        f_type = f_info.annotation
                        f_meta = _get_input_meta(f_info)
                        if f_meta:
                            f_meta.name = f_name
                            f_topts = f_meta.get_TextInputOptions()
                            if f_topts is not None and f_topts.dynamic_options_name:
                                dyn_output_names.add(f_topts.dynamic_options_name)
                            _process_input_field_type(inputs_type.__name__, f_meta, f_type, self.errors)
                            self.inputs.append(f_meta)
                        else:
                            self.errors.append(
                                f"No metadata found for input field {f_name} and its type is not one of the supported types for which metadata can be inferred")
                else:
                    self.errors.append("The type of the inputs argument should be a subclass of BaseModel")
        outputs_type = proc_sig.return_annotation
        if outputs_type is Signature.empty:
            self.errors.append(
                "The procedure must have an explicitly annotated return type")
        elif outputs_type is not None:
            if issubclass(outputs_type, BaseModel):
                fields = outputs_type.model_fields
                for f_name, f_info in fields.items():
                    if f_name in dyn_output_names:
                        continue
                    f_type = f_info.annotation
                    f_meta = _get_output_meta(f_info)
                    if f_meta:
                        f_meta.name = f_name
                        _process_output_field_type(outputs_type.__name__, f_meta, f_type, self.errors)
                        self.outputs.append(f_meta)
                    else:
                        self.errors.append(
                            f"No metadata found for output field {f_name} and its type is not one of the supported types for which metadata can be inferred")
            else:
                self.errors.append(
                    "The output type of the procedure must be a subclass of BaseModel")

    reg_id: int
    reg_version: int
    unique_id: str
    name: str
    group: str
    version: int
    immediate: bool
    inputs_require_initialization: bool

    inputs: list[ProcedureInputInfo]
    outputs: list[ProcedureOutputInfo]
    errors: list[str]
