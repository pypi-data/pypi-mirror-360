import itertools


def f(x, y):
    return 2 * x + y


answer = itertools.accumulate([1, 2, 4, 8], f)

print(list(answer))
