for i, w in enumerate(["test", "test" * 2]):
    for c in w * (i + 1):
        print(c, end=" ")
    print()

a, b = 3, 7
d = {"test": b, "test2": a}
for k in d.keys():
    print("{}: {}".format(k, d[k]), end=" // ")
print()
