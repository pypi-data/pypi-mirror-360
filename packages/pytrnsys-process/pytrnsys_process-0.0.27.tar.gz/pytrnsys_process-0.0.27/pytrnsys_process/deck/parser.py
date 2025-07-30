import pkgutil as _pu

import lark as _lark


def _create_parser() -> _lark.Lark:
    data = _pu.get_data("pytrnsys_process.deck", "ddck.lark")
    assert data, "Could not find ddck Lark grammar file."
    grammar = data.decode()
    parser = _lark.Lark(grammar, parser="earley", propagate_positions=True)
    return parser


def parse_dck(ddck_content: str) -> _lark.Tree:
    """
    Parse the provided dck content string and generate a tree structure using the Lark parser.

    The function utilizes an internal parser to interpret the given dck_content and produce
    a parsed tree object. It requires the content to be in a format understood by the parser.

    Args:
        ddck_content (str): The string content of the dck file to be parsed.

    Returns:
        _lark.Tree: The parsed tree representation of the provided dck content.

    Raises:
        Any exceptions raised by the underlying parser.
    """
    tree = _create_parser().parse(ddck_content)
    return tree
