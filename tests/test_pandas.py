import pandas as pd

import py3_kit


def test_pandas():
    df = pd.DataFrame({"A": range(1, 101), "B": range(101, 201)})
    dfs = py3_kit.pandas.split(df, num_parts=4)
    for df in dfs:
        print(df)

    print()
    print()
    print()
    print()
    print()
    print()

    df = pd.DataFrame({"A": range(1, 101), "B": range(101, 201)})
    dfs = py3_kit.pandas.split(df, part_size=50)
    for df in dfs:
        print(df)


if __name__ == '__main__':
    test_pandas()
