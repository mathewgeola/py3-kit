import os
from tempfile import NamedTemporaryFile
from typing import Literal

import cv2
import numpy as np
import pillow_avif  # type: ignore
from PIL import Image


def to_jpg(
        image_file_path: str,
        /,
        jpg_file_path: str | None = None,
        quality: int = 100,
        keep_original: bool = False
) -> str | None:
    try:
        with open(image_file_path, "rb") as file:
            prefix_text = file.read(3).hex()
            n = 2
            file.seek(-n, 2)
            suffix_text = file.read(n).hex()
            text = prefix_text + suffix_text

        image_file_path = os.path.abspath(image_file_path)
        if jpg_file_path is not None:
            jpg_file_path = os.path.abspath(jpg_file_path)
        else:
            jpg_file_path = os.path.splitext(image_file_path)[0] + os.path.extsep + "jpg"

        if image_file_path == jpg_file_path and text == "ffd8ffffd9":
            return jpg_file_path

        jpg_dir_path = os.path.dirname(jpg_file_path)
        os.makedirs(jpg_dir_path, exist_ok=True)

        with Image.open(image_file_path) as image:
            if image.mode in ("RGBA", "LA"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])
                image = background
            elif image.mode == "P":
                image.seek(0)  # image.n_frames
                image = image.convert("RGB")
            elif image.mode == "RGB":
                pass
            else:
                return None

            with NamedTemporaryFile(suffix=os.path.extsep + "jpg", delete=False, dir=jpg_dir_path) as ntf:
                temp_file_path = ntf.name
                image.save(temp_file_path, "JPEG", quality=quality)
            os.replace(temp_file_path, jpg_file_path)

        if not keep_original:
            from pathlib import Path
            if (
                    jpg_file_path != image_file_path and
                    (p := Path(image_file_path)).exists() and
                    str(p.resolve()) == str(p.absolute())
            ):
                os.remove(image_file_path)

        return jpg_file_path
    except Exception as e:  # noqa
        return None


def resize(image: cv2.typing.MatLike, new_w: int, new_h: int) -> cv2.typing.MatLike:
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def concat(
        input_image_file_paths: list[str],
        output_image_file_path: str,
        orientation: Literal["vertical", "horizontal"] = "vertical",
        output_image_vertical_width: int | float | None = None,
        output_image_horizontal_height: int | float | None = None
) -> bool:
    try:
        input_images = [cv2.imread(i, cv2.IMREAD_UNCHANGED) for i in input_image_file_paths]

        if any(i is None for i in input_images):
            return False

        if orientation == "vertical":
            if output_image_vertical_width is None:
                output_image_vertical_width = min(i.shape[1] for i in input_images)

            resized_images = []
            for i in input_images:
                h, w = i.shape[:2]
                new_w = int(output_image_vertical_width)
                new_h = int(h * new_w / w)
                resized_image = resize(i, new_w, new_h)
                resized_images.append(resized_image)

            output_image_height = sum(i.shape[0] for i in resized_images)

            output_image = np.ones((output_image_height, output_image_vertical_width, 3), dtype=np.uint8) * 255

            y = 0
            for i in resized_images:
                h = i.shape[0]
                output_image[y:y + h, :i.shape[1]] = i
                y += h

            return cv2.imwrite(output_image_file_path, output_image)

        elif orientation == "horizontal":
            if output_image_horizontal_height is None:
                output_image_horizontal_height = min(i.shape[0] for i in input_images)

            resized_images = []
            for i in input_images:
                h, w = i.shape[:2]
                new_h = int(output_image_horizontal_height)
                new_w = int(w * new_h / h)
                resized_image = resize(i, new_w, new_h)
                resized_images.append(resized_image)

            output_image_width = sum(i.shape[1] for i in resized_images)

            output_image = np.ones((output_image_horizontal_height, output_image_width, 3), dtype=np.uint8) * 255

            x = 0
            for i in resized_images:
                w = i.shape[1]
                output_image[:i.shape[0], x:x + w] = i
                x += w

            return cv2.imwrite(output_image_file_path, output_image)

        else:
            return False

    except Exception as e:  # noqa
        return False
