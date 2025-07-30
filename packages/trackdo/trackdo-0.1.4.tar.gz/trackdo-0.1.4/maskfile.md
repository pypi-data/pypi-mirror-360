# Python Project Mask File

## clean

> This command cleans the build artifacts

```bash
rm -rf dist/
rm -rf .nox/
rm -rf htmlcov/
rm -rf .coverage*
```

## lint

> Run linting checks with ruff

```bash
nox -s ruff_check
```

## fix

> Fix linting issues with ruff

```bash
nox -s ruff_fix
```

## typecheck

> Run type checking with pyright

```bash
nox -s pyright
```

## test

> This command runs the tests using nox

```bash
nox -s tests
```

## check

> Run all quality checks (lint + typecheck + test)

```bash
$MASK lint
$MASK typecheck
$MASK test
```

## bump (patch_version)

> Bump the version of the local project specifying the patch level: `minor`, `major`, `patch`

```bash
bump2version ${patch_version} --allow-dirty
```

## build

> This command builds the project via uv

```bash
uv build
```

## publish (location)

> This command publishes the package to PyPI or Twine to local pypi server

```bash
if [ "$location" = "pypi" ]; then
    export UV_PUBLISH_TOKEN=$(op read "op://Private/PyPI Prod/api_key")
    uv publish --index pypi dist/* --token $UV_PUBLISH_TOKEN
elif [ "$location" = "twine" ]; then
    twine upload -r local dist/*
else
    echo "Invalid location specified. Use 'pypi' or 'twine'."
fi
```

## full (patch_version)

> This command runs the full build and publish process

```bash
$MASK clean
$MASK check
$MASK bump ${patch_version}
$MASK build
$MASK publish
```
