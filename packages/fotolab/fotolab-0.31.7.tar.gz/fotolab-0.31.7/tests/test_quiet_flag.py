# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-q", "--quiet"])
def test_no_debug_logs(cli_runner, option):
    ret = cli_runner(option)
    assert "debug=True" not in ret.stderr
