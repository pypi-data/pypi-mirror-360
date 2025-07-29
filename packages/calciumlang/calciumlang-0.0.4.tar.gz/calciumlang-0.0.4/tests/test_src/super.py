class C:
    def m(self, x):
        print(x + 7)


class D(C):
    def m(self, x):
        s = super()
        s.m(x)


d = D()
d.m(3)
