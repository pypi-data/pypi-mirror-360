s = "test"
i = 0
n = len(s)
print(n)
while i < n:
    c = s[i]
    if c.startswith("e"):
        print("e")
    elif c.endswith("s"):
        print("s")
    elif "t" in c:
        if c.find("t") != -1:
            print(c)
    i += 1
