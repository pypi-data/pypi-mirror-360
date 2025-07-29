# Cannot define as enum because of the duplicate values
class Index:
    # command
    INDENT = 0
    OPTION = 1
    KEYWORD = 2

    # statement
    ASSIGN_LEFT = 3
    ASSIGN_RIGHT = 4

    CONDITION = 3

    FOR_VARIABLES = 3
    FOR_ITERABLE = 4

    DEF_NAME = 3
    DEF_PARAMETERS = 4

    RETURN_VALUE = 3

    CLASS_NAME = 3
    CLASS_SUPERCLASS = 4

    IMPORT_PATH = 3

    EXPR_STMT = 3

    # expression
    EXPRESSION_KEYWORD = 0

    VAR_NAME = 1

    ATTR_OBJECT = 1
    ATTR_NAME = 2

    SUBSCRIPT_OBJECT = 1
    SUBSCRIPT_INDEX = 2
    SUBSCRIPT_SLICE_START = 2
    SUBSCRIPT_SLICE_STOP = 3

    CALL_CALLEE = 1
    CALL_ARGS = 2

    KWARG_NAME = 1
    KWARG_VALUE = 2

    LEFT_OPERAND = 1
    RIGHT_OPERAND = 2

    UNARY_OPERAND = 1
