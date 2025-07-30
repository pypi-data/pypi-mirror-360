""" runvenv init """
import os
import sys
import pathlib
import hashlib
import argparse
import platform
import subprocess

__version__ = "0.4"

REQUIREMENTS_FILES = [
    "requirements.txt",
    ".requirements.txt",
    ".requirements.venv",
]


def _get_venv_path(venv_name: str) -> pathlib.Path:
    if not venv_name:
        venv_name = ".venv"

    venv_path = pathlib.Path(venv_name).absolute()
    return venv_path


def run(venv_name: str, arguments: list[str]):
    """ run a list of python arguments inside a venv """
    if not arguments or len(arguments) < 1:
        return

    venv_path = _get_venv_path(venv_name)
    is_windows = platform.system() == "Windows"

    env = os.environ
    venv_bin = venv_path / ("Scripts" if is_windows else "bin")
    env["PATH"] = str(venv_bin) + os.pathsep + env["PATH"]
    env["VIRTUAL_ENV"] = str(venv_path)
    python_exe = pathlib.Path(sys.executable).stem
    arguments = [str(venv_bin / python_exe)] + arguments
    subprocess.check_call(args=arguments, env=env)


def create(venv_name: str, requirements: str):
    """ create a venv """
    venv_path = _get_venv_path(venv_name)
    cwd_path = pathlib.Path(os.getcwd())

    if not venv_path.exists():
        subprocess.check_call(
            [sys.executable, "-m", "venv", venv_path]
        )

    requirement_path = None
    if requirements:
        requirement_path = pathlib.Path(requirements).absolute()
    else:
        for file in REQUIREMENTS_FILES:
            if (cwd_path / file).exists():
                requirement_path = cwd_path / file
                break

    if requirement_path and requirement_path.exists():
        with open(requirement_path, encoding="utf8") as requirement_file:
            content = requirement_file.read().encode()
            requirements_hash = hashlib.md5(content).hexdigest()

            if (venv_path / ".runvenv_hash").exists():
                with open(venv_path / ".runvenv_hash", encoding="utf8") as hash_file:
                    existing_hash = hash_file.read()
                    if existing_hash == requirements_hash:
                        return  # venv is up-to-date

            run(
                venv_name=venv_name,
                arguments=["-m", "pip", "install", "-r", str(requirement_path)]
            )

            with open(venv_path / ".runvenv_hash", "w", encoding="utf8") as hash_file:
                hash_file.write(requirements_hash)

def main():
    """ main function called from __main__ """
    parser = argparse.ArgumentParser(
        prog="runvenv",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
Runs a script or module in a venv and forwards *any* parameter.
This includes non positional arguments like --help, --init, --path, --requirements, etc.

With no parameters given this help will be shown. To only create a venv and not run anything \
you can use the --init parameter. If the venv does not exist yet, it will create it and also install \
all requirements in either reqirements.txt, .requirements.txt or .requirements.venv if availabe.

A custom venv path or requirements file can be configured via parameters.
"""
    )

    parser.add_argument(
        "--init",
        action="store_true",
        help="only initialize the venv"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=__version__
    )

    parser.add_argument(
        "--path",
        default=".venv",
        help="venv path, either relative to cwd or absolute"
    )

    parser.add_argument(
        "--requirements",
        default=None,
        help="path file with requirements to install in venv"
    )

    parser.add_argument(
        "--module",
        "-m",
        action="store_true",
        help="run a module instead of a python script"
    )

    parser.add_argument(
        "forwards",
        nargs=argparse.REMAINDER,
        help="all remaining arguments will be forwarded"
    )

    args = sys.argv
    if len(args) == 1:
        parser.print_help()
        sys.exit()

    arguments = parser.parse_args(args[1:])

    create(
        venv_name=arguments.path,
        requirements=arguments.requirements
    )

    argument_list = ["-m"] if arguments.module else []
    argument_list.extend(arguments.forwards)
    run(
        venv_name=arguments.path,
        arguments=argument_list
    )
