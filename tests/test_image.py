import base64

import py3_kit


def test_image():
    downloader = py3_kit.py3_downloader.downloader.Downloader()

    string = "aHR0cHM6Ly93d3cuY25uY21hbGwuY29tL3Bob3Rvcy9zdGQtY29tbW9kaXR5LzIwMjUxMi8xNDM5Y2ZjMzgyMTUzNzIzYjUxYjA1MGUyOTRiODQ2Ny5wbmc="
    url = base64.b64decode(string.encode()).decode()
    file_path = downloader.download(url)
    print(file_path)

    file_path = py3_kit.image.to_jpg(file_path, keep_original=True)
    print(file_path)


if __name__ == '__main__':
    test_image()
