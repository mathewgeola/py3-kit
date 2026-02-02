import os

import py3_kit


def test_wechat_ocr():
    wechat_ocr = py3_kit.wechat_ocr.WechatOcr(
        # os.getenv("APPDATA") + r"\Tencent\WeChat\XPlugin\Plugins\WeChatOCR\7079\extracted\WeChatOCR.exe",
        # r"C:\Program Files\Tencent\Weixin\4.1.6.46"
    )
    image_file_path = os.path.join("test_file", "img.png")
    result = wechat_ocr.ocr(image_file_path)
    print(result)


if __name__ == '__main__':
    test_wechat_ocr()
