# Singleton Mask File

## clean

> This command cleans the build artifacts

```bash
rm -rf dist/
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

## test

> This command runs the tests using pytest

```bash
pytest -s
```

## publish (publish_location)

> This command publishes the package to PyPI (or locally) officially, isn't that great?

```bash
if [ "${publish_location}" = "local" ]; then
    twine upload -r local dist/* # uploads to a local repository
else
    export UV_PUBLISH_TOKEN=$(op read "op://Private/PyPI Prod/api_key")
    uv publish --index pypi dist/* --token $UV_PUBLISH_TOKEN
fi
```

## full (patch_version) (publish_location)

> This command runs the full build and publish process

```bash
$MASK clean
$MASK bump ${patch_version}
$MASK build
$MASK publish ${publish_location}
```
