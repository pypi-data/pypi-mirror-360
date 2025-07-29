# pylint: disable=C0114,C0116

import platform
import sys

from fotolab import __version__


def test_env_output(cli_runner):
    ret = cli_runner("env")

    actual_sys_version = sys.version.replace("\n", "")
    actual_platform = platform.platform()

    expected_output = (
        f"fotolab: {__version__}\n"
        f"python: {actual_sys_version}\n"
        f"platform: {actual_platform}\n"
    )

    assert ret.stdout == expected_output
    assert ret.stderr == ""
    assert ret.returncode == 0
