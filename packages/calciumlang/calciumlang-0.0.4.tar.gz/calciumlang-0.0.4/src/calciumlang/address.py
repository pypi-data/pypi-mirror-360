class Address:
    def __init__(self, indent: int, line: int, calls=0):
        self.indent = indent
        self.line = line
        self.calls = calls

    def clone(self):
        return Address(self.indent, self.line, self.calls)

    def is_at(self, addr: "Address"):
        return (
            self.indent == addr.indent
            and self.line == addr.line
            and self.calls == addr.calls
        )

    def jump(self, addr: "Address"):
        self.indent = addr.indent
        self.line = addr.line
        # calls is not changed

    def shift(self, delta_indent: int, delta_line=0):
        self.indent += delta_indent
        self.line += delta_line
        # calls is not changed
