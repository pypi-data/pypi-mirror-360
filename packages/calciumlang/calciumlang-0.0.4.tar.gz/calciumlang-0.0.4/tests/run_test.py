import unittest
from contextlib import redirect_stdout
import io
import os

import sys
import json
import sys

sys.path.append("../src")

from calciumlang.runtime import Runtime

from calciumlang.tools.converter import convert

dir_name = None
file_names = None
if len(sys.argv) > 1:  # sys.argv[0] is the name of this file
    file_names = sys.argv[1:]
else:
    dir_name = "test_src"


def run_calcium(filepath):
    with open(filepath) as fin:
        text = fin.read()
        json_text = convert(text)
        code = json.loads(json_text)
        runtime = Runtime(code)
        runtime.run()


if __name__ == "__main__":
    suite = unittest.TestSuite()
    files = []
    if dir_name is not None:
        files = os.listdir(dir_name)
    if file_names is not None:
        files = file_names
    for filename in files:
        if not filename.endswith(".py"):
            continue

        def make_test(filepath):
            def test_file(self):
                with io.StringIO() as raw_out, io.StringIO() as calcium_out:
                    with redirect_stdout(raw_out):
                        with open(filepath) as fin:
                            exec(fin.read(), {})
                    with redirect_stdout(calcium_out):
                        run_calcium(filepath)
                    self.assertEqual(raw_out.getvalue(), calcium_out.getvalue())

            return test_file

        testname = filename[:-3]
        if dir_name is not None:
            filepath = os.path.join(os.getcwd(), dir_name, filename)
        else:
            filepath = os.path.join(os.getcwd(), filename)
        methodname = "test_{}".format(filename)
        testcase = type(
            testname, (unittest.TestCase,), {methodname: make_test(filepath)}
        )
        suite.addTest(testcase(methodName=methodname))
    unittest.TextTestRunner().run(suite)
