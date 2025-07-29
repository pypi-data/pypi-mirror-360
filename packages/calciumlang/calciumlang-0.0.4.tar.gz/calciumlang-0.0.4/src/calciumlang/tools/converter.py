import sys
import ast
import json
import traceback

VERSION = "0.0.3"

KEYWORD_COMMENT = "#"

# expressions
KEYWORD_ATTR = "attr"
KEYWORD_CALL = "call"
KEYWORD_COMMA = ","
KEYWORD_KWARG = "kwarg"
KEYWORD_SUBSCRIPT = "sub"
KEYWORD_TUPLE = "tuple"
KEYWORD_VAR = "var"

# commands
KEYWORD_ASSIGN = "="
KEYWORD_BREAK = "break"
KEYWORD_CLASS_DEF = "class"
KEYWORD_CONTINUE = "continue"
KEYWORD_ELIF = "elif"
KEYWORD_ELSE = "else"
KEYWORD_END = "end"
KEYWORD_EXPR_STMT = "expr"
KEYWORD_FOR = "for"
KEYWORD_FUNC_DEF = "def"
KEYWORD_IF = "if"
KEYWORD_IFS = "ifs"
KEYWORD_IMPORT = "import"
KEYWORD_PASS = "pass"
KEYWORD_RETURN = "return"
KEYWORD_WHILE = "while"


class Python2CalciumVisitor(ast.NodeVisitor):
    def __init__(self, indent_spaces="    "):
        super().__init__()
        self.lines = []
        self.indents = []
        self.keyword = KEYWORD_COMMENT
        self.count_of_nested_if = 0
        self.indent_spaces = indent_spaces
        self.indent_offset = len(indent_spaces)

    def get_indent(self, node):
        return node.col_offset // self.indent_offset + 1 + self.count_of_nested_if

    def output_command(self, indent, keyword, elements=[]):
        self.indents.append(indent)
        comment = []
        line = [indent, comment, keyword]
        line.extend(elements)
        self.lines.append(json.JSONEncoder(ensure_ascii=False).encode(line))

    def output_first_line(self):
        self.output_command(1, KEYWORD_COMMENT, [VERSION])

    def output_end_of_code(self):
        self.output_command(1, KEYWORD_END)

    def output_node(self, node, keyword, elements=[]):
        indent = self.get_indent(node)
        self.output_command(indent, keyword, elements)

    def get_call(self, node):
        return self.visit(node.func), self.get_arguments(node.args)

    def get_arguments(self, args):
        return [self.visit(arg) for arg in args]

    def output_elif_or_else(self, node, indent):
        if (
            hasattr(node.orelse[0], "test")
            and node.orelse[0].col_offset == node.col_offset + self.indent_offset
        ):
            # eg.
            # else:
            #     if condition:
            self.output_command(indent, KEYWORD_ELSE)
            for stmt in node.orelse:
                self.visit(stmt)
        elif hasattr(node.orelse[0], "test"):
            self.output_elif(node.orelse[0], indent)
        else:
            self.output_command(indent, KEYWORD_ELSE)
            for stmt in node.orelse:
                self.visit(stmt)

    def output_elif(self, node, indent):
        # Should not call output_node()
        self.output_command(indent, KEYWORD_ELIF, [self.visit(node.test)])
        for stmt in node.body:
            self.visit(stmt)
        if len(node.orelse) != 0:
            self.output_elif_or_else(node, indent)

    def get_bin_op(self, node, op, left, right):
        return [self.get_operator(op), self.visit(left), self.visit(right)]

    def get_operator(self, op):
        if isinstance(op, ast.Add):
            return "+"
        elif isinstance(op, ast.Sub):
            return "-"
        elif isinstance(op, ast.Mult):
            return "*"
        elif isinstance(op, ast.Pow):
            return "**"
        elif isinstance(op, ast.Div):
            return "/"
        elif isinstance(op, ast.FloorDiv):
            return "//"
        elif isinstance(op, ast.Mod):
            return "%"
        elif isinstance(op, ast.BitAnd):
            return "&"
        elif isinstance(op, ast.BitOr):
            return "|"
        elif isinstance(op, ast.BitXor):
            return "^"
        elif isinstance(op, ast.LShift):
            return "<<"
        elif isinstance(op, ast.RShift):
            return ">>"
        elif isinstance(op, ast.And):
            return "and"
        elif isinstance(op, ast.Or):
            return "or"
        elif isinstance(op, ast.Eq):
            return "=="
        elif isinstance(op, ast.NotEq):
            return "!="
        elif isinstance(op, ast.Lt):
            return "<"
        elif isinstance(op, ast.LtE):
            return "<="
        elif isinstance(op, ast.Gt):
            return ">"
        elif isinstance(op, ast.GtE):
            return ">="
        elif isinstance(op, ast.Is):
            return "is"
        elif isinstance(op, ast.IsNot):
            return "is not"
        elif isinstance(op, ast.In):
            return "in"
        elif isinstance(op, ast.NotIn):
            return "not in"

    # Visit
    def visit_Module(self, node):
        self.output_first_line()
        for stmt in node.body:
            self.visit(stmt)
        self.output_end_of_code()

    def visit_Import(self, node):
        self.output_node(node, KEYWORD_IMPORT, [node.names[0].name])

    def visit_FunctionDef(self, node):
        elems = [node.name, [arg.arg for arg in node.args.args]]
        self.output_node(node, KEYWORD_FUNC_DEF, elems)
        for stmt in node.body:
            self.visit(stmt)

    def visit_ClassDef(self, node):
        elems: list[str | None] = [node.name]
        if len(node.bases) > 0:
            elems.append(self.visit(node.bases[0]))
        else:
            elems.append(None)
        self.output_node(node, KEYWORD_CLASS_DEF, elems)
        for stmt in node.body:
            self.visit(stmt)

    def visit_Assign(self, node):
        elems = []
        if not isinstance(node.targets[0], ast.Tuple):
            elems.append(self.visit(node.targets[0]))
        else:
            lhs = [KEYWORD_COMMA]
            lhs.extend([self.visit(n) for n in node.targets[0].elts])
            elems.append(lhs)
        elems.append(self.visit(node.value))
        self.output_node(node, KEYWORD_ASSIGN, elems)

    def visit_AugAssign(self, node):
        if isinstance(node.op, ast.Add):
            keyword = "+="
        elif isinstance(node.op, ast.Sub):
            keyword = "-="
        elif isinstance(node.op, ast.Mult):
            keyword = "*="
        elems = [self.visit(node.target), self.visit(node.value)]
        self.output_node(node, keyword, elems)

    def visit_Tuple(self, node):
        elems = [KEYWORD_TUPLE]
        elems.extend([self.visit(e) for e in node.elts])
        return elems

    def visit_For(self, node):
        elems = []
        var_elem = self.visit(node.target)
        if isinstance(var_elem, list) and var_elem[0] == KEYWORD_TUPLE:
            var_elem[0] = KEYWORD_COMMA  # convert to reference in Calcium
        elems.append(var_elem)
        elems.append(self.visit(node.iter))
        self.output_node(node, KEYWORD_FOR, elems)
        for stmt in node.body:
            self.visit(stmt)

    def visit_While(self, node):
        elems = [self.visit(node.test)]
        self.output_node(node, KEYWORD_WHILE, elems)
        for stmt in node.body:
            self.visit(stmt)

    def visit_If(self, node):
        self.output_node(node, KEYWORD_IFS)
        self.count_of_nested_if += 1
        self.output_node(node, KEYWORD_IF, [self.visit(node.test)])
        for stmt in node.body:
            self.visit(stmt)
        if len(node.orelse) != 0:
            indent = self.get_indent(node)
            self.output_elif_or_else(node, indent)
        self.count_of_nested_if -= 1

    def visit_Pass(self, node):
        self.output_command(self.get_indent(node), KEYWORD_PASS)

    def visit_Return(self, node):
        elems = []
        if hasattr(node, "value"):
            if node.value is None:
                elems.append(None)
            else:
                elems.append(self.visit(node.value))
        else:
            elems.append(None)
        self.output_command(self.get_indent(node), KEYWORD_RETURN, elems)

    def visit_Break(self, node):
        self.output_command(self.get_indent(node), KEYWORD_BREAK)

    def visit_Continue(self, node):
        self.output_command(self.get_indent(node), KEYWORD_CONTINUE)

    def visit_Compare(self, node):
        return self.get_bin_op(node, node.ops[0], node.left, node.comparators[0])

    def visit_BinOp(self, node):
        return self.get_bin_op(node, node.op, node.left, node.right)

    def visit_BoolOp(self, node):
        if isinstance(node.op, ast.And):
            op = "and"
        else:
            op = "or"
        elems = [op, self.visit(node.values[0]), self.visit(node.values[1])]
        count = len(node.values)
        i = 2
        while i < count:
            elems = [op, elems, self.visit(node.values[i])]
            i += 1
        return elems

    def visit_UnaryOp(self, node):
        elems = []
        if isinstance(node.op, ast.Not):
            keyword = "not"
        elif isinstance(node.op, ast.USub):
            keyword = "-_"
            if isinstance(node.operand, ast.Num):
                # Return by a literal with - sign
                return -node.operand.n
        elif isinstance(node.op, ast.Invert):
            keyword = "~"
        # if keyword not exist, then error will be raised
        elems.append(keyword)
        elems.append(self.visit(node.operand))
        return elems

    def visit_List(self, node):
        # List must be nested
        return [[self.visit(e) for e in node.elts]]

    def visit_Dict(self, node):
        obj = {}
        for k, v in zip(node.keys, node.values):
            if k is not None:
                obj[self.visit(k)] = self.visit(v)
        return obj

    def visit_Num(self, node):
        return node.n

    def visit_Constant(self, node):
        return node.value

    def visit_Str(self, node):
        return node.s.replace("\n", "\\n")

    def visit_Name(self, node):
        return [KEYWORD_VAR, node.id]

    def visit_NameConstant(self, node):
        return node.value

    def visit_Attribute(self, node):
        attrs: list[str | list] = [node.attr]
        childnode = node.value
        while isinstance(childnode, ast.Attribute):
            attrs.insert(0, childnode.attr)
            childnode = childnode.value
        if isinstance(childnode, ast.Name):
            attrs.insert(0, [KEYWORD_VAR, childnode.id])
        else:
            attrs.insert(0, childnode.value)  # type: ignore
        attrs.insert(0, KEYWORD_ATTR)
        return attrs

    def visit_Subscript(self, node):
        value = self.visit(node.value)
        if isinstance(node.slice, ast.Slice):
            if node.slice.lower != None:
                lower = self.visit(node.slice.lower)
            else:
                lower = None
            if node.slice.upper != None:
                upper = self.visit(node.slice.upper)
            else:
                upper = None
            return [KEYWORD_SUBSCRIPT, value, lower, upper]
        if isinstance(node.slice, ast.Name):
            sub = self.visit(node.slice)
        elif isinstance(node.slice, ast.Constant):
            sub = node.slice.value
        return [KEYWORD_SUBSCRIPT, value, sub]

    def visit_Expr(self, node):
        value = self.visit(node.value)
        return self.output_node(node, KEYWORD_EXPR_STMT, [value])

    def visit_Call(self, node):
        elems: list[str | list] = [KEYWORD_CALL]
        func_ref, args = self.get_call(node)
        elems.append(func_ref)
        elems.append(args)
        if len(node.keywords) > 0:
            for kwd in node.keywords:
                kwarg = [KEYWORD_KWARG]
                kwarg.append(kwd.arg)  # type: ignore
                kwarg.append(self.visit(kwd.value))
                # append to the list already added to elems
                args.append(kwarg)

        return elems

    def generic_visit(self, node):
        super().generic_visit(node)


def convert(src):
    try:
        module_node = ast.parse(src)
        visitor = Python2CalciumVisitor()
        visitor.visit(module_node)
        lines = []
        for indent, line in zip(visitor.indents, visitor.lines):
            lines.append("{}{}".format("  " * indent, line))
        code = (",\n").join(lines)
        return "[\n{}\n]\n".format(code)
    except Exception:
        return traceback.format_exc()


if __name__ == "__main__":
    filename = sys.argv[1]
    with open(filename, encoding="utf-8") as fin:
        json_array = convert(fin.read())
        print(json_array)
