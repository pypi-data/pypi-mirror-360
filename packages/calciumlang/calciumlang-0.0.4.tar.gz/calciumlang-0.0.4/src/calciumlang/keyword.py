import enum


class Keyword(enum.Enum):
    # assignment
    ASSIGN = "="
    COMPOUND_ADD = "+="
    COMPOUND_SUBTRACT = "-="
    COMPOUND_MULTIPLY = "*="

    # operators
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"
    FLOOR_DIVIDE = "//"
    POWER = "**"

    EQUAL = "=="
    NOT_EQUAL = "!="
    LESS_THAN = "<"
    LESS_THAN_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_THAN_EQUAL = ">="

    AND = "and"
    OR = "or"
    NOT = "not"

    IN = "in"

    NEGATIVE = "-_"

    # statements
    IFS = "ifs"
    IF = "if"
    ELIF = "elif"
    ELSE = "else"

    FOR = "for"
    WHILE = "while"
    BREAK = "break"
    CONTINUE = "continue"

    DEF = "def"
    RETURN = "return"

    CLASS = "class"

    IMPORT = "import"

    EXPR_STMT = "expr"

    PASS = "pass"

    # expressions
    VARIABLE = "var"
    ATTRIBUTE = "attr"
    SUBSCRIPT = "sub"
    CALL = "call"

    # syntax
    COMMA = ","
    KWARG = "kwarg"
    TUPLE = "tuple"

    COMMENT = "#"
    END = "end"
