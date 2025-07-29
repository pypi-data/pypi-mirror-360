# pylint: disable=C0114,C0116


def test_halftone_subcommand(cli_runner, image_file):
    img_path = image_file("sample.png")
    ret = cli_runner("halftone", str(img_path))
    assert ret.returncode == 0
