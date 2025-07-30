from os import defpath, getenv
from pathlib import Path
from typing import Sequence

from .config import Config
from .exceptions import UserException
from .output import Printer


def project_path(extra_path: Sequence[str]) -> str:
    """
    Prepends to the system PATH the locations specific to our project

    Parameters
    ----------
    extra_path
        Locations to be prepended
    """

    return ":".join([*extra_path, getenv("PATH", defpath)])


def run_api(path: Path, command: str, args: Sequence[str]) -> None:
    """
    Detects where Poetry puts its virtualenv and adds it to the path

    Parameters
    ----------
    path
        Root path of the project
    command
        Name of the binary to run
    args
        Arguments to that binary
    """

    printer = Printer.instance()

    venv_path = (
        (
            printer.exec(
                "Getting virtualenv path",
                path,
                ["poetry", "env", "info", "-p"],
                return_stdout=True,
            )
            or b"/dry/run"
        )
        .decode("utf-8")
        .rstrip("\n")
    )

    printer.env_patch["PATH"] = project_path([f'{Path(venv_path).resolve() / "bin"}'])
    printer.handover("Running command", path, [command, *args])


def run_front(path: Path, command: str, args: Sequence[str]) -> None:
    """
    Adds the node_modules/.bin directory to the path

    Parameters
    ----------
    path
        Root path of the project
    command
        Name of the binary to run
    args
        Arguments to that binary
    """

    printer = Printer.instance()

    printer.env_patch["PATH"] = project_path(
        [f"{path.resolve() / 'node_modules' / '.bin'}"]
    )
    printer.handover("Running command", path, [command, *args])


def run(config: Config, path: Path, command: str, args: Sequence[str]) -> None:
    """
    Runs a binary knowing the component's specific path

    Parameters
    ----------
    config
        Component's configuration
    path
        Root path of the project
    command
        Name of the binary to run
    args
        Arguments to that binary
    """

    printer = Printer.instance()
    printer.chapter(f"Running a command for {config.project.name}")
    printer.doing(f"Detected project type: {config.project.component}")

    if config.project.component == "api":
        return run_api(path, command, args)
    elif config.project.component == "front":
        return run_front(path, command, args)
    else:
        raise UserException(f"Unknown component: {config.project.component}")
