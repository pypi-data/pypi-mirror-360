## Mynd

Mynd is a toolbox for working with georeferenced images and geometric computer vision.


### Installing dependencies

```shell
uv sync                         # install current package's dependencies
uv sync --package mynd-core     # install dependencies of specified package
uv sync --package myndms        # install dependencies of specified package
uv sync --all-packages          # install dependencies of all packages
```

### Running tests

```shell
uv run pytest
uv run --package mynd-core pytest
uv run --package myndms pytest
```

### Building packages

```shell
uv build                        # build current project
uv build --package mynd-core    # build a specific package
uv build --package myndms       # build a specific package
uv build --all-packages         # build all packages
```

### Docker

```shell
docker build -t mynd:base-latest -f docker/base/Dockerfile .

# Build docker images
docker-compose build

# Run docker containers
docker-compose up
```

### References

- Setup guide for Docker Compose: (https://docs.docker.com/compose/)[https://docs.docker.com/compose/]
- Setup guide for Docker Desktop: (https://docs.docker.com/desktop/)[https://docs.docker.com/desktop/]
