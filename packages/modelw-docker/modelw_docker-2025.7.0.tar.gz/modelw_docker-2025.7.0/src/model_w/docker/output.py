import os
import shlex
import shutil
import subprocess
from typing import List, Optional

from colorama import Back, Fore, Style

from .exceptions import UserException


def make_to_print(args: List[str], become: str) -> str:
    """
    Prettify arguments of the command that will be executed for printing
    purposes.
    """

    to_print = " ".join(shlex.quote(x) for x in args)

    if become:
        to_print = f"{Fore.BLUE}sudo -u {shlex.quote(become)} {Fore.GREEN}{to_print}"

    return to_print


def make_args(args: List[str], become: str) -> List[str]:
    """
    Generates the real args for the command, depending on if there will be a
    sudo or not.

    Parameters
    ----------
    args
        Args of the command
    become
        Name of the user that should run that command (if any)
    """

    if become:
        return ["sudo", "-u", become, *args]

    return args


class Printer:
    """
    Utility class to print what we're doing and to execute commands
    """

    _instance = None

    def __init__(self):
        self.blank = None
        self.env_patch = {}
        self._dry_run = False

    @classmethod
    def instance(cls):
        """
        This class keeps track of the number of blank lines printed. It's
        better to keep the same instance throughout the project, which you can
        do by call this method.
        """

        if not cls._instance:
            cls._instance = cls()

        return cls._instance

    @property
    def dry_run(self):
        """
        Getter for the dry_run mode
        """

        return self._dry_run

    @dry_run.setter
    def dry_run(self, value: bool):
        """
        Sets the dry run mode on or off and prints the change (if it's a
        change)

        Parameters
        ----------
        value
            New value for the dry_run mode
        """

        old_val = self._dry_run

        if old_val != value:
            self._dry_run = value
            self._print(f"{Fore.YELLOW}Dry run: {value}{Style.RESET_ALL}")

    def jump(self, n: int):
        if self.blank is not None:
            for _ in range(self.blank, n):
                print("", flush=True)
        else:
            self.blank = 0

        self.blank += n

    def clear(self):
        self.blank = 0

    def print(self, msg: str):
        self._print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")

    def error(self, msg: str):
        self.jump(2)
        self._print(f"{Fore.WHITE}{Back.RED}{msg}{Style.RESET_ALL}")
        self.jump(1)

    def _print(self, msg: str):
        print(msg, flush=True)
        self.clear()

    def chapter(self, msg: str):
        """
        Prints a big chapter

        Parameters
        ----------
        msg
            Message of the chapter
        """

        self.jump(3)
        self.print(
            f"{Fore.MAGENTA}=====[ {Style.BRIGHT}{msg}{Style.NORMAL} ]====={Style.RESET_ALL}"
        )
        self.jump(2)

    def doing(self, msg: str):
        """
        Prints a step

        Parameters
        ----------
        msg
            Message of the step
        """

        self.jump(2)
        self.print(f"{Fore.CYAN}--> {Style.BRIGHT}{msg}{Style.RESET_ALL}")
        self.jump(1)

    def exec(
        self,
        reason: str,
        cwd: str,
        args: List[str],
        return_stdout: bool = False,
        become: str = "",
    ) -> Optional[bytes]:
        """
        Executes a command

        Parameters
        ----------
        reason
            Text on the step that will be printed
        cwd
            Working dir for this command
        args
            Args of the command (including the command itself)
        return_stdout
            Whether or not to return the content of stdout (otherwise it'll be
            printed in the console)
        become
            Run as another user using sudo
        """

        self.doing(reason)

        extra = {}

        if return_stdout:
            extra["stdout"] = subprocess.PIPE

        if self.env_patch:
            extra["env"] = {**os.environ, **self.env_patch}

        self.print(f"+ {make_to_print(args, become)}")

        try:
            if not self.dry_run:
                ret = subprocess.run(make_args(args, become), cwd=cwd, **extra)

                if ret.returncode:
                    raise UserException("Could not execute command")

                return ret.stdout
        finally:
            self.clear()
            self.jump(1)

    def handover(
        self,
        reason: str,
        cwd: str,
        args: List[str],
        become: str = "",
    ):
        """
        Calls exec() to become another command

        Parameters
        ----------
        reason
            What to print as a step
        cwd
            Working directory to use
        args
            Arguments, including the command
        become
            User to run this command as (using sudo)
        """

        self.doing(reason)

        self.print(f"% {make_to_print(args, become)}")

        try:
            if not self.dry_run:
                os.chdir(cwd)
                full_args = make_args(args, become)
                env = {**os.environ, **self.env_patch}
                bin_command = shutil.which(full_args[0], path=env.get("PATH"))

                if not bin_command:
                    raise UserException(f"Could not find command {full_args[0]}")

                self.clear()
                self.jump(1)

                os.execvpe(bin_command, full_args, env=env)
        finally:
            self.clear()
            self.jump(1)

    def pipe(
        self,
        reason: str,
        cwd: str,
        args_left: List[str],
        args_right: List[str],
        become_left: str = "",
        become_right: str = "",
        return_stdout: bool = False,
    ) -> Optional[bytes]:
        """
        Pipes a command into another

        Parameters
        ----------
        reason
            Reason to give as a step
        cwd
            Working directory for these commands
        args_left
            Arguments of the left-hand command
        args_right
            Arguments of the right-hand command
        become_left
            Who to run the left command as
        become_right
            Who to run the right command as
        return_stdout
            Capture the stdout of the right command
        """

        self.doing(reason)

        print_left = make_to_print(args_left, become_left)
        print_right = make_to_print(args_right, become_right)
        self.print(f"+ {print_left} | {print_right}")

        try:
            if not self.dry_run:
                extra_right = {}
                extra_left = {}

                if return_stdout:
                    extra_right["stdout"] = subprocess.PIPE

                if self.env_patch:
                    extra_right["env"] = {**os.environ, **self.env_patch}
                    extra_left["env"] = {**os.environ, **self.env_patch}

                p_left = subprocess.Popen(
                    make_args(args_left, become_left),
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    **extra_left,
                )
                p_right = subprocess.Popen(
                    make_args(args_right, become_right),
                    cwd=cwd,
                    stdin=p_left.stdout,
                    **extra_right,
                )

                p_left.wait()
                p_right.wait()

                if p_left.returncode or p_right.returncode:
                    raise UserException("Could not execute command")

                return p_right.stdout
        finally:
            self.clear()
            self.jump(1)
