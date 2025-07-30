from pathlib import Path

from .config import Config
from .exceptions import UserException
from .output import Printer


def build_api(path: Path) -> None:
    """
    Django requires no transpiling on itself but all the static assets need to
    be collected into a single directory for WhiteNoise to be able to serve
    them.
    """

    printer = Printer.instance()

    printer.chapter("Building Django static files")

    printer.env_patch["BUILD_MODE"] = "yes"

    printer.exec(
        "Collecting static files",
        path,
        ["poetry", "run", "python", "manage.py", "collectstatic", "--noinput"],
    )


def build_front(path: Path) -> None:
    """
    Compile the front with npm run build
    """

    printer = Printer.instance()

    printer.chapter("Building front project")

    printer.env_patch["BUILD_MODE"] = "true"

    printer.exec(
        "Running front build script",
        path,
        ["npm", "run", "build"],
    )


def build(config: Config, path: Path) -> None:
    """
    The build phase takes the code from Git and transforms it into runnable
    code.
    """

    printer = Printer.instance()
    printer.chapter(f"Building {config.project.name}")
    printer.doing(f"Detected project type: {config.project.component}")

    if config.project.component == "api":
        return build_api(path)
    elif config.project.component == "front":
        return build_front(path)
    else:
        raise UserException(f"Unknown component: {config.project.component}")
