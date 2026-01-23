import os

import py3_kit


def test_wechat_ocr():
    wechat_ocr = py3_kit.wechat_ocr.WechatOcr()
    image_file_path = os.path.join("test_file", "img.png")
    result = wechat_ocr.ocr(image_file_path)
    print(result)


if __name__ == '__main__':
    test_wechat_ocr()
