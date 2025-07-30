# Model W Docker

A tool so that your Dockerfile looks like this:

```Dockerfile
FROM modelw/base:2023.03

COPY --chown=user package.json package-lock.json ./

RUN modelw-docker install

COPY --chown=user . .

RUN modelw-docker build

CMD ["modelw-docker", "serve"]
```

## Organization

This repository contains different elements that work together, found in
sub-directories here:

-   `src` &mdash; Contains the source of the `modelw-docker` package, that is
    published on Pypi.
-   `image` &mdash; Is the source for the Docker image that can be used as a
    base for all Model&nbsp;W projects.
-   `demo` &mdash; A demo project used to test the image during development

## `modelw-docker`

This is a helper that is pre-installed in the Docker image and helps you build
and run a Model&nbsp;W project.

If called from the root of a project, it will automatically detect the project's
type and run appropriate commands for each step of the build. If later on the
way the Docker image is built or the requirements of Model&nbsp;W change, it is
expected that those changes can be reflected in the `modelw-docker` package
without requiring the developers to change their Dockerfiles.

### Available actions

-   `modelw-docker install` &mdash; Installs the project's dependencies (creates
    the virtualenv, runs `npm install` or whatever is required). It only
    requires the dependencies files to run (`package.json`/`package-lock.json`
    for front components, `pyproject.toml`/`poetry.lock` for api components).
-   `modelw-docker build` &mdash; Builds the project. It requires the project to
    be installed first. It also requires all the source code to be present.
-   `modelw-docker serve` &mdash; Runs the project. It requires the project to
    be installed and built first.
-   `modelw-docker run` &mdash; Runs a command in the project's virtualenv. It
    requires the project to be installed first.

The reason why `install` and `build` are separate and why you need first to copy
just the dependencies list and then the source code is to allow for caching of
the dependencies. This way, the dependencies are only re-installed when the
dependencies list changes, not when the source code changes. This makes very
fast builds when only the source code changes.

### Dry run

There is a `--dry-run` option for all the commands that will just print what
would have been done but not do it. The dry run mode is automatically enabled if
you run the package outside of Docker in order to avoid fucking up your desktop.

### Config file

All the settings are automatically detected, however if something isn't to your
taste you can always override it using a `model-w.toml` file, following this
structure:

```toml
[project]
# For printing purposes
name = "demo_project"
# Either "front" or "api"
component = "api"

[project.required_files]
# All the files to be created before the install step and their content
"src/demo_project/__init__.py" = ""

[apt.repos]
# APT repositories to be added, you need to give both the source and the key
# for each one of them
pgdg.source = "deb http://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main"
pgdg.key = { url = "https://www.postgresql.org/media/keys/ACCC4CF8.asc" }

[apt.packages]
# APT packages to be installed. Put * to install the default version, or a
# version number to install a specific version.
gdal-bin = "*"
```

In addition, Python project also have the following settings:

```toml
[project]
# [...]
# Either "gunicorn", "daphne" or "granian"
server = "daphne"

# Modules that have the WSGI and ASGI entry points
wsgi = "demo_project.django.wsgi:application"
asgi = "demo_project.django.asgi:application"
```

## Contribution

The Docker image and the package are auto-built and published on Docker Hub and
Pypi respectively. The build is triggered by pushing a tag to the repository
(for the Python package) and for each branch's head (for the Docker image).

If you want to make a release, the Makefile will help you:

```bash
make release VERSION=2022.10.0
```

This will use Git Flow to make the release, and then also make sure to update
the version in the Dockerfile and the `modelw-docker` package.

Once this is done, you have to:

-   Push the tag to the repository
-   Push develop and master
-   Make sure you update support branches accordingly (this cannot be automated
    it's a human decision)

> **Note** &mdash; If you're releasing a new major version of Model&nbsp;W, you
> need to update the `image/Dockerfile` to match the new "upper" version limit.
> This script will only update the "lower" version limit, to make sure the image
> is built with the package you just released.
