import importlib.util
import os
from types import ModuleType
from typing import Any

import py3_kit


class WechatOcr:
    def __init__(
            self,
            wechat_ocr_file_path: str | None = None,
            weixin_dir_path: str | None = None
    ):
        pyd = py3_kit.assets.get_assets_file_path("wcocr.pyd")
        spec = importlib.util.spec_from_file_location("wcocr", pyd)
        module: ModuleType = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.wcocr = module

        if wechat_ocr_file_path is None:
            wechat_ocr_file_path = py3_kit.assets.get_assets_file_path("WeChatOCR", "WeChatOCR.exe")

        if weixin_dir_path is None:
            weixin_dir_path = py3_kit.assets.get_assets_file_path("Weixin")

        self.wcocr.init(wechat_ocr_file_path, weixin_dir_path)

    def ocr(self, image_file_path: str) -> dict[str, Any]:
        image_file_path = os.path.abspath(image_file_path)
        result = self.wcocr.ocr(image_file_path)
        return result
