import py3_kit


def test_sql():
    print(py3_kit.sql.format("select * from table;"))  # noqa


if __name__ == '__main__':
    test_sql()
