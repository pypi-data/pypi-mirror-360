# pylint: disable=C0114,C0116


def test_border_subcommand(cli_runner, image_file):
    img_path = image_file("sample.png")
    ret = cli_runner("border", str(img_path), "--width", "10")
    assert ret.returncode == 0
