import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Literal, Type, TypeVar, Union

from colorama import Style
from typefit import Fitter
from typefit.nodes import Node
from typefit.reporting import ErrorFormatter, ErrorReporter, PrettyJson5Formatter

from .exceptions import UserException

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


@dataclass
class Project:
    """
    Describes the basic fields of a project

    Other Parameters
    ----------------
    name
        Display name for this project
    component
        Component that we're building (api or front so far)
    required_files
        Some files that need to be created before the install phase
    """

    name: str
    component: str
    required_files: Dict[str, str]


@dataclass
class ApiProject(Project):
    """
    Extra fields for Python projects

    Other Parameters
    ----------------
    server
        Name of the server that's going to be running (gunicorn, daphne or granian)
    wsgi
        Name of the WSGI module
    asgi
        Name of the ASGI module
    celery
        Name of the Celery module
    """

    server: str
    wsgi: str
    asgi: str
    celery: str


@dataclass
class FrontProject(Project):
    """Front-end project, for now no extra fields"""


@dataclass
class KeyUrl:
    """
    For when the key of a repo is specified from its URL (other means might
    appear in the future)
    """

    url: str


@dataclass
class Repo:
    """
    An apt repo to be added to the sources list
    """

    source: str
    key: KeyUrl


@dataclass
class Apt:
    """
    In case the base image is missing some packages, we provide through here a
    way to install packages from apt.

    Other Parameters
    ----------------
    repos
        Extra apt repos to install
    packages
        Packages (key) with the version to install (value). The version can be
        "*", which will install the default version, or something else, which
        will install the exact specified version.
    """

    repos: Dict[str, Repo]
    packages: Dict[str, str]


@dataclass
class Config:
    """
    Structure of a configuration file
    """

    project: Union[ApiProject, FrontProject]
    apt: Apt


def guess_api_config(path: Path) -> Dict:
    """
    Based on the source code we can already guess most of the configuration.
    For a normal project, you shouldn't need to manually create a model-w.toml
    file, which only exists to cover edge cases.

    Everything here is expecting to see Model W conventions respected. If not,
    things might fail. It's definitely not bullet-proof against any kind of
    project, that's not the scope.

    The output of this function will be merged with the config file (if any).
    """

    pp_path = path / "pyproject.toml"
    lock_path = path / "poetry.lock"

    if not pp_path.exists():
        return {}

    with open(pp_path, mode="rb") as f:
        pp = tomllib.load(f)

    if lock_path.exists():
        with open(lock_path, mode="rb") as f:
            lock = tomllib.load(f)
    else:
        lock = {"package": []}

    poetry = pp.get("tool", {}).get("poetry", {})
    has_daphne = any(x["name"] == "daphne" for x in lock["package"])
    has_gunicorn = any(x["name"] == "gunicorn" for x in lock["package"])
    
    required_files = {}
    package_root = None

    for package in poetry.get("packages", []):
        if isinstance(package, str):
            if package_root is None:
                package_root = package
            required_files[f"{package}/__init__.py"] = ""
        elif isinstance(package, dict):
            if package_root is None:
                package_root = package["include"]

            if src_from := package.get("from"):
                prefix = f'{src_from.rstrip("/")}/'
            else:
                prefix = ""

            required_files[f'{prefix}{package["include"]}/__init__.py'] = ""

    asgi = wsgi = celery = ""

    if package_root is not None:
        asgi_path = path / package_root / "django" / "asgi.py"
        wsgi_path = path / package_root / "django" / "wsgi.py"
        celery_path = path / package_root / "django" / "celery.py"
        
        asgi = f"{package_root.replace('/', '.')}.django.asgi:application" if asgi_path.exists() else ""
        wsgi = f"{package_root.replace('/', '.')}.django.wsgi:application" if wsgi_path.exists() else ""
        celery = f"{package_root.replace('/', '.')}.django.celery:app" if celery_path.exists() else ""


    # Currently, we support 3 servers, but will drop Daphne and Gunicorn in the future.
    # Daphne and Gunicorn will not be installed by the preset, but by the project to override the preset.
    server = "granian"
    if has_daphne:
        server = "daphne"
    elif has_gunicorn:
        server = "gunicorn"

    return {
        "project": {
            "name": poetry.get("name"),
            "component": "api",
            "server": server,
            "required_files": required_files,
            "asgi": asgi,
            "wsgi": wsgi,
            "celery": celery,
        },
        "apt": {
            "repos": {},
            "packages": {},
        },
    }


def guess_front_config(path: Path) -> Dict:
    """
    Same as guess_api_config() but for the front.
    """

    pkg_path = path / "package.json"

    if not pkg_path.exists():
        return {}

    with open(pkg_path, mode="r", encoding="utf-8") as f:
        pkg = json.load(f)

    return {
        "project": {
            "name": pkg.get("name"),
            "component": "front",
            "required_files": {},
        },
        "apt": {
            "repos": {},
            "packages": {},
        },
    }


def guess_config(path: Path) -> Dict:
    """
    See guess_api_config on how we guess the config.
    """

    if (path / "pyproject.toml").exists():
        return guess_api_config(path)
    elif (path / "package.json").exists():
        return guess_front_config(path)
    else:
        return {}


class ConfigFitErrorReporter(ErrorReporter):
    """
    Customize the way typefit reports errors to have something printed
    nicely.
    """

    def __init__(self, formatter: ErrorFormatter):
        self.formatter = formatter

    def report(self, node: "Node") -> None:
        raise UserException(
            f"Impossible to validate config:{Style.RESET_ALL}\n\n{self.formatter.format(node)}"
        )


T = TypeVar("T")


def typefit(t: Type[T], value: Any) -> T:
    """
    Typefit with custom error reporting.
    """

    return Fitter(
        error_reporter=ConfigFitErrorReporter(
            formatter=PrettyJson5Formatter(colors="terminal16m")
        )
    ).fit(t, value)


def get_config(path: Path) -> Config:
    """
    Guesses the default config then reads the model-w.toml file at the root
    of the project (if any) and merges them together to produice the global
    Config.

    Parameters
    ----------
    path
        Root of the project
    """

    default = guess_config(path)

    if (mwt_path := path / "model-w.toml").exists():
        with open(mwt_path, mode="rb") as f:
            user = tomllib.load(f)
    else:
        user = {}

    project = {**default.get("project", {}), **user.get("project", {})}

    if "required_files" in user.get("project", {}):
        project["required_files"] = user["project"]["required_files"]

    if (user_repos := user.get("apt", {}).get("repos")) is not None:
        repos = user_repos
    else:
        repos = default.get("apt", {}).get("repos", {})

    if (user_packages := user.get("apt", {}).get("packages")) is not None:
        packages = user_packages
    else:
        packages = default.get("apt", {}).get("packages", {})

    return typefit(
        Config,
        dict(
            project=project,
            apt=dict(
                repos=repos,
                packages=packages,
            ),
        ),
    )
