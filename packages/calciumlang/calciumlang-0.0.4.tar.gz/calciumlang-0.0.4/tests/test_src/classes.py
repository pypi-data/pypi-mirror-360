class A:
    def __init__(self, n):
        self.n = n


class B(A):
    def __init__(self, n, m):
        s = super(B, self)
        s.__init__(n)
        self.m = m * n


class C:
    class D:
        x = 7


a = A(1)
b = B(3, 7)
print(isinstance(b, A))

a.n += 10
print(a.n)
print(b.m)

a.d = C.D
d = a.d()
d.m = C()
d.m.x = a.d.x
print(d.m.x)
