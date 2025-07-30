import collections.abc as _cabc
import logging as _logging
import math as _math

import lark as _lark

from pytrnsys_process import log
from pytrnsys_process.deck import parser
from pytrnsys_process.deck import visitor_helpers as vh


def parse_deck_for_constant_expressions(
    deck_as_string: str, logger: _logging.Logger = log.default_console_logger
) -> dict[str, float | int]:
    """Evaluate constant expressions in a TRNSYS deck file and return their values.

    This function parses a TRNSYS deck file string, identifies constant expressions,
    and evaluates them to their numerical values. It handles mathematical operations,
    functions, and variable references.

    Parameters
    __________
        deck_as_string: str
            A string containing the contents of a TRNSYS deck file.
        logger: Logger
            provide your own logger. to for example log per simulation

    Returns
    _______
        variable_values: dict
            A dictionary mapping variable names to their evaluated values (float or int).
            The original case of variable names is preserved in the returned dictionary.
            Expressions that could not be evaluated are not included in the returned dictionary.


    """

    equations = _get_equation_trees(deck_as_string)
    sub_trees_to_process = _get_expression_sub_trees_by_variable_name(
        equations
    )

    evaluated_variables: dict[str, float | int] = {}
    original_variable_names: list[str] = []
    new_constants_found = True

    while new_constants_found:
        sub_trees_before_processing = sub_trees_to_process.copy()
        # Needs to be converted into list, so items can be deleted while iteration over
        # Described in this answer:
        # https://stackoverflow.com/questions/5384914/how-to-delete-items-from-a-dictionary-while-iterating-over-it
        for var, tree in list(sub_trees_to_process.items()):
            try:

                maybe_evaluated_value = (
                    _evaluate_or_none_if_variable_could_not_be_found(
                        tree, evaluated_variables
                    )
                )

                if maybe_evaluated_value is not None:
                    var_lower = var.casefold()
                    original_variable_names.append(var)
                    evaluated_variables[var_lower] = maybe_evaluated_value
                    del sub_trees_to_process[var]

            except MathFuncNotFoundError as e:
                failed_equation = deck_as_string[
                    e.meta.start_pos : e.meta.end_pos
                ]
                func_name, _ = failed_equation.split("(")
                logger.warning(
                    "On line %s, %s is not supported in %s=%s",
                    e.meta.line,
                    func_name,
                    var,
                    failed_equation,
                )
                del sub_trees_to_process[var]

            except _lark.exceptions.VisitError as e:
                failed_equation = deck_as_string[
                    e.obj.meta.start_pos : e.obj.meta.end_pos  # type: ignore
                ]
                logger.error(
                    "On line %s, unable to compute equation %s=%s because: %s",
                    e.obj.meta.line,  # type: ignore
                    var,
                    failed_equation,
                    str(e),
                    exc_info=True,
                )

        if sub_trees_before_processing == sub_trees_to_process:
            new_constants_found = False

    return _rename_dict_keys_to_original_format(
        evaluated_variables, original_variable_names
    )


class EquationsCollectorVisitor(_lark.Visitor):
    """This visitor is given the whole deck as a tree.
    For each equation the equation() method is called and it appends it to a list of equations
    """

    def __init__(self):
        self.equations_to_transform = []

    def equation(self, tree):
        output_detector = self.OutputOfTrnsysTypeDetector()
        output_detector.visit(tree)

        if not output_detector.is_output:
            self.equations_to_transform.append(tree)

    class OutputOfTrnsysTypeDetector(_lark.visitors.Visitor_Recursive):
        """Detects if equation is an output: equation_name = [15,1]"""

        def __init__(self):
            self.is_output = False

        def output(self, _):
            self.is_output = True


class EquationsTransformer(_lark.Transformer):

    def __init__(self, evaluated_variables: _cabc.Mapping[str, float | int]):
        super().__init__()
        self.evaluated_variables = evaluated_variables

    def number(self, items):
        number_as_str = items[0].value
        as_int = int(float(number_as_str))
        as_float = float(number_as_str)
        return as_int if as_int == as_float else as_float

    def negate(self, items):
        return -items[0]

    def plus(self, items):
        return items[0] + items[1]

    def minus(self, items):
        return items[0] - items[1]

    def divided_by(self, items):
        return items[0] / items[1]

    def times(self, items):
        return items[0] * items[1]

    def to_power_of(self, items):
        return items[0] ** items[1]

    def default_visibility_var(self, items) -> float:
        try:
            variable_name = items[0].value.casefold()
            return self.evaluated_variables[variable_name]
        except KeyError as exc:
            raise ReferencedVariableNotEvaluatedError() from exc

    @_lark.v_args(meta=True)
    # pylint: disable=too-many-return-statements,too-many-branches
    def func_call(self, meta, items):
        """Mathematical function behaviour is described in pages 20 and 21 of trnsys doc 6 TRNedit"""

        math_func = vh.get_child_token_value("NAME", items[0], str).casefold()
        args = items[1].children

        if math_func == "int":
            return int(args[0])
        if math_func == "ae":
            return 1 if abs(args[0] - args[1]) < args[2] else 0
        if math_func == "abs":
            return abs(args[0])
        if math_func == "acos":
            return _math.acos(args[0])
        if math_func == "and":
            return args[0] and args[1]
        if math_func == "or":
            return args[0] or args[1]
        if math_func == "not":
            return int(not args[0])
        if math_func == "asin":
            return _math.asin(args[0])
        if math_func == "atan":
            return _math.atan(args[0])
        if math_func == "cos":
            return _math.cos(args[0])
        if math_func == "eql":
            return 1 if args[0] == args[1] else 0
        if math_func == "exp":
            return _math.exp(args[0])
        if math_func == "ge":
            return 1 if args[0] >= args[1] else 0
        if math_func == "gt":
            return 1 if args[0] > args[1] else 0
        if math_func == "le":
            return 1 if args[0] <= args[1] else 0
        if math_func == "lt":
            return 1 if args[0] < args[1] else 0
        if math_func == "ln":
            return _math.log(args[0])
        if math_func == "log":
            return _math.log10(args[0])
        if math_func == "max":
            return max(args[0], args[1])
        if math_func == "min":
            return min(args[0], args[1])
        if math_func == "mod":
            return _math.fmod(args[0], args[1])
        if math_func == "sin":
            return _math.sin(args[0])
        if math_func == "tan":
            return _math.tan(args[0])
        raise MathFuncNotFoundError(
            f"Function {math_func} can not be computed", meta
        )

    def explicit_var(self, items):
        return items[0]


class MathFuncNotFoundError(Exception):
    """This error is raised if the parsed 'func_call' is not supported."""

    def __init__(self, message, meta):
        super().__init__(message)

        self.meta = meta


class ReferencedVariableNotEvaluatedError(Exception):
    """Raised if an equation could not be found in the dictionary of resolved equations."""


def _get_equation_trees(deck_as_string):
    whole_tree = parser.parse_dck(deck_as_string)
    equations_collector_visitor = EquationsCollectorVisitor()
    equations_collector_visitor.visit(whole_tree)
    equations = equations_collector_visitor.equations_to_transform
    return equations


def _rename_dict_keys_to_original_format(
    evaluated_variables, original_variable_names
) -> dict[str, float | int]:
    for original_name in original_variable_names:
        evaluated_variables[original_name] = evaluated_variables.pop(
            original_name.casefold()
        )
    return evaluated_variables


def _get_expression_sub_trees_by_variable_name(
    list_of_equation_trees: list[_lark.Tree],
) -> dict[str, _lark.Tree]:
    equations_dict = {}
    for equation_tree in list_of_equation_trees:
        equations_dict[
            vh.get_child_token_value(
                "NAME", equation_tree.children[0].children[0], str
            )
        ] = equation_tree.children[
            1
        ]  # right hand side of the equation as a tree

    return equations_dict


def _evaluate_or_none_if_variable_could_not_be_found(
    tree: _lark.Tree, evaluated_variables: _cabc.Mapping[str, float]
):
    # Exceptions raised in callback need to be caught here
    try:
        value = EquationsTransformer(evaluated_variables).transform(tree)
        return value
    except _lark.exceptions.VisitError as e:
        if isinstance(e.orig_exc, ReferencedVariableNotEvaluatedError):
            return None
        if isinstance(e.orig_exc, MathFuncNotFoundError):
            raise e.orig_exc
        raise
