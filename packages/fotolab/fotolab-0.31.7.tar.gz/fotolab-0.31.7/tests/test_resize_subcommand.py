# pylint: disable=C0114,C0116


def test_resize_subcommand(cli_runner, image_file):
    img_path = image_file("sample.png")
    ret = cli_runner("resize", str(img_path), "--width", "200")
    assert ret.returncode == 0
