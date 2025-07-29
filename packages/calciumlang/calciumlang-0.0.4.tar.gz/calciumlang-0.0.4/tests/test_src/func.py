def f(x, y):
    print(x, y)
    return x + y


z = f(1, 2) + f(3, 4)
print(z)

print(f(f(5, 6), 7))

l = f([0, 1], [2])
print(f(f(f(len(l), 1), f(-1, -2)), f(8, 9)))
