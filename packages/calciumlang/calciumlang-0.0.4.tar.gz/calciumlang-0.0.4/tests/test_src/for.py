for i in range(5):
    print(i)

l = [0, 2, 4]
for i, elem in enumerate(l):
    print("{}: {}".format(i, elem))

s1, s2 = ["test", "jest"]
for c1, c2 in zip(s1, s2):
    print(c1, c2)
