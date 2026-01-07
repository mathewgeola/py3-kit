import py3_kit


def test_list():
    print(py3_kit.list.split(list(range(8)), 3))
    print(py3_kit.list.flatten([1, 2, [3, 4], [5, 6, 7]]))


if __name__ == '__main__':
    test_list()
