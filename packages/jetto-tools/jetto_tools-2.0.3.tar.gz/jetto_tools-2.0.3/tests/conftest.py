import os
import sys
import subprocess
from pathlib import Path

import pytest

this_file = Path(__file__).resolve()


@pytest.fixture(params=[40], ids=["shell_timeout"])
def run_in_shell_wrapper(request):
    if isinstance(request.param, int):
        shell_timeout = request.param

    env = dict(os.environ)
    env['PYTHONPATH'] = f"{this_file.parent.parent}:{env.get('PYTHONPATH', '')}"

    def run_in_shell(cmd):
        """ Run a command in the shell

        Convinience function to test CLI commands

        Args:
            cmd: String with the command to be run

        Returns:
            Result of the run command
        """
        cmd = str(cmd)
        output = subprocess.run(
            cmd, capture_output=True, shell=True,
            timeout=shell_timeout, encoding='UTF-8',
            env=env,
        )

        if output.returncode != 0:
            print('stdout:', output.stdout)
            print('stderr:', output.stderr)
            raise subprocess.CalledProcessError(output.returncode, cmd)

        return output

    return run_in_shell


@pytest.fixture()
def datadir():
    path = Path(this_file.parent / "../testdata").resolve()
    assert path.is_dir()
    return path
