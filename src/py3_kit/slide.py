import hashlib
import importlib.util
import json
import os
import random
from io import BytesIO
from pathlib import Path
from types import ModuleType
from typing import TypeVar, Literal, Any

import ddddocr
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image
from PIL import ImageDraw
from jinja2 import Template

import py3_kit


def draw_dotted_rect(draw, x1, y1, x2, y2, color, step=6, dot_len=2):
    """
    step    : 点之间的间隔
    dot_len : 每个点/小线段的长度
    """

    # 上边
    for x in range(x1, x2, step):
        draw.line((x, y1, x + dot_len, y1), fill=color)

    # 下边
    for x in range(x1, x2, step):
        draw.line((x, y2, x + dot_len, y2), fill=color)

    # 左边
    for y in range(y1, y2, step):
        draw.line((x1, y, x1, y + dot_len), fill=color)

    # 右边
    for y in range(y1, y2, step):
        draw.line((x2, y, x2, y + dot_len), fill=color)


def render_slider_on_bg_image(
        bytes_bg_image: bytes,
        bytes_slider_image: bytes,
        slider_x: int,
        slider_y: int,
        out_file_path: str,
        plt_show: bool = False
):
    bg_image = Image.open(BytesIO(bytes_bg_image)).convert("RGBA")
    slider_image = Image.open(BytesIO(bytes_slider_image)).convert("RGBA")

    result = bg_image.copy()
    result.paste(slider_image, (slider_x, slider_y), slider_image)

    draw = ImageDraw.Draw(result)

    x1, y1 = slider_x, slider_y
    x2 = slider_x + slider_image.width - 1
    y2 = slider_y + slider_image.height - 1

    draw_dotted_rect(
        draw,
        x1, y1, x2, y2,
        color=(255, 0, 0, 255),
        step=6,  # 间隔
        dot_len=2  # 点大小
    )

    if out_file_path:
        result.save(out_file_path)

    if plt_show:
        plt.figure(figsize=(8, 4))
        plt.imshow(result)
        plt.axis("off")
        plt.show()

    return result


def get_double_image_slide_distance(
        base64_bg_image: str,
        base64_slider_image: str,
        bg_image_render_width: int | None = None,
        image_dir_path: str | None = None
) -> int:
    """
    获取双图滑动距离

    :param base64_bg_image: 背景图片 base64 字符串
    :param base64_slider_image: 滑块图片 base64 字符串
    :param bg_image_render_width: 背景图片 (渲染宽度)
    :param image_dir_path: 图片保存目录
    :return: 滑块图片 在 背景图片 上需要滑动的距离 (计算渲染后滑动的距离)
    """

    bg_base64_image = py3_kit.image.Base64Image(base64_bg_image)
    slider_base64_image = py3_kit.image.Base64Image(base64_slider_image)

    name = hashlib.sha256(bg_base64_image.to_bytes_image() + slider_base64_image.to_bytes_image()).hexdigest()

    bg_image_file_prefix = name + "-bg-image"
    slider_image_file_prefix = name + "-slider-image"

    bg_image_file_name = f"{bg_image_file_prefix}.{bg_base64_image.ext}"
    slider_image_file_name = f"{slider_image_file_prefix}.{slider_base64_image.ext}"

    bg_image_file_path = os.path.join(image_dir_path, bg_image_file_name) if image_dir_path else None
    slider_image_file_path = os.path.join(image_dir_path, slider_image_file_name) if image_dir_path else None

    bytes_bg_image = bg_base64_image.to_bytes_image(bg_image_file_path)
    bytes_slider_image = slider_base64_image.to_bytes_image(slider_image_file_path)

    det = ddddocr.DdddOcr(ocr=False, det=False, show_ad=False)
    result = det.slide_match(bytes_slider_image, bytes_bg_image, simple_target=True)
    x = result["target"][0]
    y = result["target"][1]

    if image_dir_path:
        file_path = os.path.join(image_dir_path, name + "-result-image.png")
        render_slider_on_bg_image(bytes_bg_image, bytes_slider_image, x, y, file_path)

    if bg_image_render_width is not None:
        bg_image_origin_width = Image.open(BytesIO(bytes_bg_image)).size[0]
        x *= (bg_image_render_width / bg_image_origin_width)

    slide_distance = round(x)

    return slide_distance


X = TypeVar("X", bound=int)
Y = TypeVar("Y", bound=int)

SlidePoint = tuple[X, Y]
SlidePoints = list[SlidePoint]
SlideMode = Literal["bezier_curve", "ghost_cursor"]


def get_slide_points_by_bessel_function(slide_distance: int, **kwargs: Any) -> SlidePoints:
    """
    https://github.com/2833844911/gurs/raw/refs/heads/main/cBezier.py

    Args:
        slide_distance:
        **kwargs:

    Returns:

    """
    py = py3_kit.assets.get_assets_file_path("cBezier.py")
    spec = importlib.util.spec_from_file_location("cBezier", py)
    module: ModuleType = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    BezierTrajectory = module.bezierTrajectory

    bt = BezierTrajectory()
    kw = {
        "numberList": random.randint(25, 45),
        "le": 4,
        "deviation": 10,
        "bias": 0.5,
        "type": 2,
        "cbb": 1,
        "yhh": 5
    }
    """
    numberList: 返回的数组的轨迹点的数量 numberList = 150
    le: 几阶贝塞尔曲线，越大越复杂 如 le = 4
    deviation: 轨迹上下波动的范围 如 deviation = 10
    bias: 波动范围的分布位置 如 bias = 0.5
    type: 0表示均速滑动，1表示先慢后快，2表示先快后慢，3表示先慢中间快后慢 如 type = 1
    cbb: 在终点来回摆动的次数
    yhh: 在终点来回摆动的范围
    """
    kw.update(kwargs)
    result = bt.trackArray([0, 0], [slide_distance, 0], **kw)
    result = result["trackArray"].tolist()
    slide_points = [(round(i[0]), round(i[1])) for i in result]
    return slide_points


def get_slide_points_by_ghost_cursor(slide_distance: int, **_kwargs: Any) -> SlidePoints:
    """
    npm install -g ghost-cursor

    Args:
        slide_distance:
        **_kwargs:

    Returns:

    """
    js_code = '''function sdk(from,to){const{path}=require("ghost-cursor");return path(from,to,{useTimestamps:false})}'''  # noqa
    result = py3_kit.py3_execute.js.execute_javascript_by_execjs(
        js_code=js_code, func_name="sdk",
        func_args=({"x": 0, "y": 0}, {"x": slide_distance, "y": 0})
    )
    slide_points = [(round(i["x"]), round(i["y"])) for i in result]
    return slide_points


def get_slide_points(slide_distance: int, slide_mode: SlideMode = "bezier_curve", **kwargs: Any) -> SlidePoints:
    if slide_mode == "bezier_curve":
        slide_points = get_slide_points_by_bessel_function(slide_distance, **kwargs)
    elif slide_mode == "ghost_cursor":
        slide_points = get_slide_points_by_ghost_cursor(slide_distance, **kwargs)
    else:
        raise ValueError(f"Unsupported slide_mode: {slide_mode:!r}")
    return slide_points


T = TypeVar("T", bound=int)

TimeInterval = int | tuple[int, int]
SlideTrajectory = tuple[X, Y, T]
SlideTrajectories = list[SlideTrajectory]


def get_slide_trajectories_by_slide_points(slide_points: SlidePoints, time_interval: TimeInterval) -> SlideTrajectories:
    slide_trajectories = []
    t = 0
    for slide_point in slide_points:
        x, y = slide_point

        if isinstance(time_interval, int):
            t += time_interval
        else:
            if isinstance(time_interval, tuple) and len(time_interval) == 2:
                if all(map(lambda _: isinstance(_, int), time_interval)):
                    t += random.randint(*time_interval)
                else:
                    raise ValueError(f"Unsupported time_interval: {time_interval!r}")
            else:
                raise ValueError(f"Unsupported time_interval: {time_interval!r}")

        slide_trajectory = (x, y, t)
        slide_trajectories.append(slide_trajectory)
    return slide_trajectories


def get_slide_trajectories_by_resources(slide_distance: int) -> SlideTrajectories:
    dir_path = py3_kit.assets.get_assets_file_path("assets")
    file_paths, _ = py3_kit.file.get_file_paths_and_dir_paths(dir_path)
    items = [
        json.loads(Path(p).read_text(encoding="utf-8"))
        for p in file_paths
        if p.endswith(".json")
    ]
    item = random.choice(items)

    manual_slide_trajectories = []
    start_x, start_y, start_t = 0, 0, 0
    for idx, i in enumerate(item["slideTrajectories"]):
        if idx == 0:
            x = 0
            y = 0
            t = 0
            start_x = i["x"]
            start_y = i["y"]
            start_t = i["t"]
        else:
            x = i["x"] - start_x
            y = i["y"] - start_y
            t = i["t"] - start_t
        manual_slide_trajectories.append((x, y, t))

    rate = slide_distance / item["slideDistance"]

    # slide_trajectories = [
    #     (round(m[0] * rate), round(m[1] * rate), round(m[2] * rate)) for m in manual_slide_trajectories
    # ]

    slide_trajectories = [(round(m[0] * rate), round(m[1]), m[2]) for m in manual_slide_trajectories]
    return slide_trajectories


def get_format_slide_trajectories(
        slide_trajectories: SlideTrajectories,
        x_offset: bool,
        y_offset: bool,
        t_offset: bool,
        t_divide_by_1000: bool
) -> SlideTrajectories:
    format_slide_trajectories = []
    current_x, current_y, current_t = 0, 0, 0
    for slide_trajectory in slide_trajectories:
        x, y, t = slide_trajectory
        if x_offset is True:
            offset_x = x - current_x
            current_x = x
            x = offset_x
        if y_offset is True:
            offset_y = y - current_y
            current_y = y
            y = offset_y
        if t_offset is True:
            offset_t = t - current_t
            current_t = t
            t = offset_t
        format_slide_trajectory = (x, y, t)
        format_slide_trajectories.append(format_slide_trajectory)

    if t_divide_by_1000 is True:
        format_slide_trajectories = list(
            map(lambda _: (_[0], _[1], float(f"{_[2] / 1e3:.2f}")), format_slide_trajectories)
        )

    return format_slide_trajectories


def get_slide_js(selector: str, slide_trajectories: SlideTrajectories) -> str:
    # language=javascript
    js_code = '''function sdk (selector, slideTrajectories) {
      const element = document.querySelector(selector);

      let accumulatedTime = 0;

      for (let i = 0; i < slideTrajectories.length; i++) {
        const [x, y, t] = slideTrajectories[i];

        accumulatedTime += t;

        let type;
        if (i === 0) {
          type = "mousedown";
        } else if (i !== slideTrajectories.length - 1) {
          type = "mousemove";
        } else {
          type = "mouseup";
        }

        function triggerMouseEvent (element, type, x, y) {
          const event = new MouseEvent(type, {
            bubbles: true,
            cancelable: true,
            view: window,
            clientX: x,
            clientY: y,
          });
          element.dispatchEvent(event);
        }

        setTimeout(() => { triggerMouseEvent(element, type, x, y); }, accumulatedTime);
      }
    }'''
    js_code += "\n"
    js_code += '''sdk("{{ selector }}", {{ slideTrajectories }});'''
    template = Template(js_code)
    slide_js = template.render(selector=selector, slideTrajectories=json.loads(json.dumps(slide_trajectories)))
    return slide_js


def plot_slide_trajectories(
        slide_trajectories: SlideTrajectories,
        show: bool = False,
        save: bool = False,
        save_file_path: str | None = None
) -> None:
    matplotlib.use("TkAgg")

    xs = list(map(lambda _: _[0], slide_trajectories))
    ys = list(map(lambda _: _[1], slide_trajectories))
    ts = list(map(lambda _: _[2], slide_trajectories))

    plt.figure(figsize=(10, 8))

    plt.subplot(2, 1, 1)
    plt.plot(xs, ys, color="red")
    plt.title("xy")
    plt.xlabel("x axis")
    plt.ylabel("y axis")

    plt.subplot(2, 2, 3)
    plt.plot(ts, xs, color="red")
    plt.title("tx")
    plt.xlabel("t axis")
    plt.ylabel("x axis")

    plt.subplot(2, 2, 4)
    plt.plot(ts, ys, color="red")
    plt.title("ty")
    plt.xlabel("t axis")
    plt.ylabel("y axis")

    if show is True:
        plt.show()

    if save is True and save_file_path is not None:
        plt.savefig(save_file_path)
