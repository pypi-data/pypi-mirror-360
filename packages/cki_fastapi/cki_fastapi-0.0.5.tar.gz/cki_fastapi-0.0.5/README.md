## Publishing this package

Increment the package version in pyproject.toml.  
Run `uv build` to build the package. The package is generated in the dist directory. Older builds are not automatically cleaned. Delete them manually.  
Run `uv publish --token <PyPi_token_here>` to publish it to PyPi.