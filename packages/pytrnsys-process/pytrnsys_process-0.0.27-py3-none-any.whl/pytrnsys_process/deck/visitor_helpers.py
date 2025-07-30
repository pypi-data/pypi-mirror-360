import collections.abc as _cabc
import typing as _tp

import lark as _lark

_T = _tp.TypeVar("_T")


def get_child_token_value(
    token_type: str,
    tree: _lark.Tree,
    conversion_function: _cabc.Callable[[str], _T],
) -> _T:
    token = get_child_token_value_or_none(
        token_type, tree, conversion_function
    )

    if not token:
        raise ValueError(
            f"`{tree.data}` doesn't contain a direct child token of type `{token_type}`."
        )
    token_value = token

    return token_value


def get_child_token_value_or_none(
    token_type: str,
    tree: _lark.Tree,
    conversion_function: _tp.Callable[[str], _T],
) -> _T | None:
    token_or_none = get_child_token_or_none(token_type, tree)

    if not token_or_none:
        return None

    converted_value = conversion_function(token_or_none.value)

    return converted_value


def get_child_token_or_none(
    token_type: str, tree: _lark.Tree
) -> _lark.Token | None:
    tokens = get_child_tokens_or_empty_sequence(token_type, tree)

    n_tokens = len(tokens)
    if n_tokens == 0:
        return None

    if n_tokens > 1:
        raise ValueError(f"More than one token of type `{token_type}` found.")

    token = tokens[0]

    return token


def get_child_token_values_or_empty_sequence(
    token_type: str, tree: _lark.Tree
) -> _cabc.Sequence[str]:
    return [
        t.value for t in get_child_tokens_or_empty_sequence(token_type, tree)
    ]


def get_child_token(token_type: str, tree: _lark.Tree) -> _lark.Token:
    token_or_none = get_child_token_or_none(token_type, tree)

    if not token_or_none:
        raise ValueError(
            f"`{tree.data}` doesn't contain a direct child token of type `{token_type}`."
        )
    token = token_or_none

    return token


def get_child_tokens_or_empty_sequence(
    token_type: str, tree: _lark.Tree
) -> _cabc.Sequence[_lark.Token]:
    return [
        c
        for c in tree.children
        if isinstance(c, _lark.Token) and c.type == token_type
    ]
