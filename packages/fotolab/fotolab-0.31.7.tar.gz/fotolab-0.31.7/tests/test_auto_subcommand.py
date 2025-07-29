# pylint: disable=C0114,C0116


def test_auto_subcommand(cli_runner, image_file):
    """Test auto subcommand."""
    img_path = image_file("sample.png")
    ret = cli_runner("auto", str(img_path))
    assert ret.returncode == 0
