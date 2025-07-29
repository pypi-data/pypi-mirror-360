# pylint: disable=C0114,C0116


def test_watermark_subcommand(cli_runner, image_file):
    img_path = image_file("sample.png")
    ret = cli_runner("watermark", str(img_path), "--text", "Test")
    assert ret.returncode == 0
