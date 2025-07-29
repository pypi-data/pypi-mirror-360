# pylint: disable=C0114,C0116


def test_montage_subcommand(cli_runner, image_file):
    img_path = image_file("sample.png")
    ret = cli_runner("montage", str(img_path), str(img_path))
    assert ret.returncode == 0
