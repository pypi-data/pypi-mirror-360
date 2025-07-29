# pylint: disable=C0114,C0116


def test_animate_subcommand(cli_runner, image_file):
    img_path1 = image_file("sample.png")
    img_path2 = image_file("sample.png")
    ret = cli_runner("animate", str(img_path1), str(img_path2))
    assert ret.returncode == 0
