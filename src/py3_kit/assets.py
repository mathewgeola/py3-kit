import inspect
import os


def get_assets_file_path(path: str) -> str:
    assets_dir_path = os.path.splitext(os.path.abspath(__file__))[0]
    caller_dir_path = os.path.splitext([str(frame_info.filename) for frame_info in inspect.stack()][1])[0]
    mid_dir_path = os.path.relpath(caller_dir_path, assets_dir_path).lstrip(os.path.pardir + os.path.sep)
    assets_file_path = os.path.join(assets_dir_path, mid_dir_path, path)
    return assets_file_path
