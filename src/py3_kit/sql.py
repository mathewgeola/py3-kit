from typing import Any

import sqlparse


def format(sql: str, **kwargs: Any) -> str:  # noqa
    if not kwargs:
        kwargs = dict(
            reindent=True,
            keyword_case="upper",
            identifier_case="lower",
            strip_comments=True
        )
    sql = sqlparse.format(sql, **kwargs)
    return sql
