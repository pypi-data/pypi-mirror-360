import inspect
import re
import ast
from ioproc.logger import mainlogger as log

__author__ = [
    "Benjamin Fuchs",
]
__copyright__ = "Copyright 2024, German Aerospace Center (DLR)"
__credits__ = []

__license__ = "MIT"
__maintainer__ = "Benjamin Fuchs"
__email__ = "ioProc@dlr.de"
__status__ = "Production"


SNAKE_CASE_PATTERN_1 = re.compile("(.)([A-Z][a-z]+)")
SNAKE_CASE_PATTERN_2 = re.compile("__([A-Z])")
SNAKE_CASE_PATTERN_3 = re.compile("([a-z0-9])([A-Z])")


def to_snake_case(name):
    name = SNAKE_CASE_PATTERN_1.sub(r"\1_\2", name)
    name = SNAKE_CASE_PATTERN_2.sub(r"_\1", name)
    name = SNAKE_CASE_PATTERN_3.sub(r"\1_\2", name)
    return name.lower()


class IdentifyVariables(ast.NodeVisitor):
    """Implements a visitor for the ast of the action to collect information of used variables."""

    def __init__(self, start_line, params):
        self.start_line = start_line
        self.locals = []
        self.params = params

        self.covered = set()
        self.used_params = set()

    def visit_Name(self, node: ast.Name):
        n = node.id

        snake_case_format = to_snake_case(node.id)

        is_mal_formatted = n != snake_case_format

        if isinstance(node.ctx, ast.Store) and node.id not in self.covered:
            self.locals.append(
                (
                    node.lineno + self.start_line,
                    node.id,
                    snake_case_format,
                    is_mal_formatted,
                )
            )
            self.covered.add(node.id)

        if n in self.params:
            self.used_params.add(n)

        self.generic_visit(node)


def check_action(fn):
    """checks the given action for smells, indicating reduced readability, maintainability and reuseability.

    Args:
        fn (function): the action to be checked
    """
    signature = inspect.signature(fn)

    start_line = inspect.getsourcelines(fn)[1] - 1

    n_params = len(signature.parameters)
    lloc = 0
    in_comment = False
    longest_line = 0
    for iline in inspect.getsource(fn).split("\n"):
        iline = iline.strip()
        if len(iline) == 0:
            continue
        if iline[-1] == "#":
            continue
        if "'''" in iline:
            in_comment = not in_comment
        if in_comment or "'''" in iline:
            continue
        lloc += 1
        longest_line = max(longest_line, len(iline))

    v = IdentifyVariables(start_line, signature.parameters)
    r = ast.parse(inspect.getsource(fn))
    v.visit(r)
    local_vars_with_issues = [i for i in v.locals if i[-1]]
    # local_vars_okay = [i for i in v.locals if not i[-1]]
    # external_vars = inspect.getclosurevars(fn)

    log.info(f"health report for action {fn.__name__}:")
    if 5 < n_params < 9:
        log.info(
            "more than 5 parameters to this action. Consider reducing to less parameters (recommended are no more than 5)"
        )
    elif n_params >= 8:
        log.info(
            "more than 8 parameters to this action. Strong recommendation to reduce the parameters to at least 8."
        )

    if len(v.used_params) != n_params:
        log.info("there are unused parameter(s) to this action that can be removed:")
        log.info(
            "    " + ", ".join(i for i in (set(signature.parameters) - v.used_params))
        )

    if 30 < lloc < 51:
        log.info(
            f"the action is rather long ({lloc} lines of code). It is recommended to aim for no more than 30 loc."
        )
    elif lloc > 50:
        log.info(
            f"the action is too long ({lloc} lines of code). It is recommended to aim for no more than 30 loc."
        )

    if longest_line > 100:
        log.info(
            "the source code of this action indicates that it can benefit from a formatter like black or ruff to improve readability."
        )

    if local_vars_with_issues:
        log.info(
            "there are some variables which do not follow the snake_case convention. It is recommended to apply snake case. The following variable names were detected:"
        )
        for i in local_vars_with_issues:
            log.info(f"    l.{i[0]}: {i[1]} -> {i[2]}")
