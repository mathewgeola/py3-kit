import py3_kit


def test_file():
    print(py3_kit.file.compress(".gitignore", compress_file_path=".gitignore1.zip"))
    print(py3_kit.file.compress(".gitignore", compress_file_path=".gitignore2.rar"))
    print(py3_kit.file.compress(".gitignore", compress_file_path=".gitignore3.7z"))
    print(py3_kit.file.decompress(".gitignore1.zip", ".gitignore1"))
    print(py3_kit.file.decompress(".gitignore2.rar", ".gitignore2"))
    print(py3_kit.file.decompress(".gitignore3.7z", ".gitignore3"))

    print(py3_kit.file.compress("test_file", "zip"))
    print(py3_kit.file.compress("test_file", "rar"))
    print(py3_kit.file.compress("test_file", "7z"))
    print(py3_kit.file.decompress("test_file.rar", "test_file1"))
    print(py3_kit.file.decompress("test_file.zip", "test_file2"))
    print(py3_kit.file.decompress("test_file.7z", "test_file3"))

    print(py3_kit.file.get_file_paths_and_dir_paths("."))


if __name__ == '__main__':
    test_file()
