import sys

sys.path.append("../src")

from calciumlang.runtime import Runtime, RuntimeResult

from calciumlang.tools.converter import convert

import json

s = """
t = input('test: ')
print(t)
print(len(input(len(input(input(t))))))
"""

if len(sys.argv) > 1:
    with open(sys.argv[1]) as fin:
        s = fin.read()

code = convert(s)
print(code)
r = Runtime(json.loads(code))
try:
    result = r.run()
except:
    print(r.env.code[r.env.addr.line])

while True:
    if result == RuntimeResult.PAUSED:
        result = r.resume("test:")
        continue
    elif result == RuntimeResult.EXECUTED:
        result = r.run()
    else:
        break
