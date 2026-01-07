"""
rar
    https://www.rarlab.com/download.htm

7z
    Windows: https://www.7-zip.org/a/7zr.exe
    Darwin: https://www.7-zip.org/a/7z2501-mac.tar.xz
    Linux: https://www.7-zip.org/a/7z2501-linux-x64.tar.xz
"""
import os
import platform
import subprocess
import sys
import zipfile
from typing import Literal, cast

import py3_kit

COMPRESS_TYPE = Literal["zip", "rar", "7z"]
DECOMPRESS_TYPE = Literal["zip", "rar", "7z"]


def compress(
        path: str,
        compress_type: COMPRESS_TYPE | None = None,
        compress_file_path: str | None = None
) -> str | None:
    path = os.path.abspath(path)

    if compress_file_path is not None:
        compress_file_path = os.path.abspath(compress_file_path)
        if compress_type is None:
            compress_type = os.path.splitext(compress_file_path)[-1][1:]
    else:
        if compress_type is None:
            compress_type = "zip"
        compress_file_path = os.path.join(
            os.path.dirname(path), os.path.basename(path) + os.extsep + compress_type
        )

    if compress_type == "zip":
        with zipfile.ZipFile(compress_file_path, "w", zipfile.ZIP_DEFLATED) as zf:
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if (file_path := os.path.join(root, file)) == compress_file_path:
                            continue
                        rel_file_path = os.path.relpath(file_path, path)
                        zf.write(file_path, arcname=rel_file_path)
            else:
                rel_file_path = os.path.basename(path)
                zf.write(path, arcname=rel_file_path)
        return compress_file_path

    if compress_type == "rar":
        if sys.platform.startswith("win"):
            x = py3_kit.assets.get_assets_file_path(f"win{os.sep}Rar.exe")
        elif sys.platform == "darwin":
            x = py3_kit.assets.get_assets_file_path(f"mac{os.sep}rar")
        elif sys.platform.startswith("linux"):
            x = py3_kit.assets.get_assets_file_path(f"linux{os.sep}rar")
        else:
            return None
        args = [
            x,
            "a",
            "-r",
            "-inul",
            "-ep1",
            compress_file_path
        ]
        if os.path.isdir(path):
            args.append(f"{path}{os.sep}*")
        else:
            args.append(path)
        if subprocess.run(args).returncode == 0:
            return compress_file_path

    if compress_type == "7z":
        if sys.platform.startswith("win"):
            x = py3_kit.assets.get_assets_file_path(f"win{os.sep}7zr.exe")
        elif sys.platform == "darwin":
            x = py3_kit.assets.get_assets_file_path(f"mac{os.sep}7zz")
        elif sys.platform.startswith("linux"):
            x = py3_kit.assets.get_assets_file_path(f"linux{os.sep}7zz")
        else:
            return None
        args = [
            x,
            "a",
            compress_file_path
        ]
        if os.path.isdir(path):
            args.append(f"{path}{os.sep}*")
        else:
            args.append(path)
        args.extend("-bb0 -bso0 -bsp0 -bse0".split())
        if subprocess.run(args).returncode == 0:
            return compress_file_path

    return None


def decompress(
        compress_file_path: str,
        path: str | None = None
) -> str | None:
    compress_file_path = os.path.abspath(compress_file_path)
    if not os.path.isfile(compress_file_path):
        return None

    if path is not None:
        path = os.path.abspath(path)
    else:
        path = os.path.dirname(compress_file_path)
    os.makedirs(path, exist_ok=True)

    with open(compress_file_path, "rb") as file:
        data = file.read(8)
    text = data.hex()
    if text in ("504b030414000000",):
        decompress_type = "zip"
    elif text in ("526172211a070100", "526172211a0700cf"):
        decompress_type = "rar"
    elif text in ('377abcaf271c0004',):
        decompress_type = "7z"
    else:
        return None

    if decompress_type == "zip":
        with zipfile.ZipFile(compress_file_path, "r") as zf:
            zf.extractall(path)
        return path

    if decompress_type == "rar":
        if sys.platform.startswith("win"):
            x = py3_kit.assets.get_assets_file_path(f"win{os.sep}UnRAR.exe")
        elif sys.platform == "darwin":
            x = py3_kit.assets.get_assets_file_path(f"mac{os.sep}unrar")
        elif sys.platform.startswith("linux"):
            x = py3_kit.assets.get_assets_file_path(f"linux{os.sep}unrar")
        else:
            return None
        args = [
            x,
            "x",
            "-o+",
            "-inul",
            compress_file_path,
            path
        ]
        if subprocess.run(args).returncode == 0:
            return path

    if decompress_type == "7z":
        if sys.platform.startswith("win"):
            x = py3_kit.assets.get_assets_file_path(f"win{os.sep}7zr.exe")
        elif sys.platform == "darwin":
            x = py3_kit.assets.get_assets_file_path(f"mac{os.sep}7zz")
        elif sys.platform.startswith("linux"):
            x = py3_kit.assets.get_assets_file_path(f"linux{os.sep}7zz")
        else:
            return None
        args = [
            x,
            "x",
            compress_file_path,
            f"-o{path}",
            "-y"
        ]
        args.extend("-bb0 -bso0 -bsp0 -bse0".split())
        if subprocess.run(args).returncode == 0:
            return path

    return None


def get_file_paths_and_dir_paths(path: str) -> tuple[list[str], list[str]]:
    file_paths = []
    dir_paths = []

    path = os.path.abspath(path)
    with os.scandir(path) as entries:
        for entry in entries:
            System = Literal["Windows", "Linux", "Darwin"]
            system: System = cast(System, platform.system())
            if system == "Windows":
                from nt import DirEntry
            elif system == "Linux":
                from posix import DirEntry
            elif system == "Darwin":
                from posix import DirEntry
            else:
                raise TypeError(
                    f"Invalid type for 'system': "
                    f"Expected `Literal[\"Windows\",\"Linux\",\"Darwin\"]`, "
                    f"but got {type(system).__name__!r} (value: {system!r})"
                )

            entry: DirEntry
            if entry.is_file():
                file_paths.append(entry.path)
            elif entry.is_dir():
                dir_paths.append(entry.path)
                sub_file_paths, sub_dir_paths = get_file_paths_and_dir_paths(entry.path)
                file_paths.extend(sub_file_paths)
                dir_paths.extend(sub_dir_paths)

    return file_paths, dir_paths
