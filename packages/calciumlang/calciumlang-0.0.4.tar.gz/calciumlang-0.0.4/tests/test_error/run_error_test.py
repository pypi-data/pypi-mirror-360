import sys
import unittest

sys.path.append("..")
sys.path.append("../../src")

from calciumlang.error import (
    OutOfRangeError,
    NameNotFoundError,
    ObjectNotIterableError,
    ObjectNotCallableError,
)

from run_test import run_calcium


class TestErrors(unittest.TestCase):
    def test_out_of_range(self):
        with self.assertRaises(OutOfRangeError) as context:
            run_calcium("out_of_range.py")
        self.append_message(context)

    def test_name_not_found(self):
        with self.assertRaises(NameNotFoundError) as context:
            run_calcium("name_not_found.py")
        self.append_message(context)

    def test_object_not_iterable(self):
        with self.assertRaises(ObjectNotIterableError) as context:
            run_calcium("object_not_iterable.py")
        self.append_message(context)

    def test_object_not_callable(self):
        with self.assertRaises(ObjectNotCallableError) as context:
            run_calcium("object_not_callable.py")
        self.append_message(context)

    def append_message(self, context):
        TestErrors.message += str(context.exception) + "\n"

    @classmethod
    def tearDownClass(cls):
        print(cls.message)

    message = "\n"


unittest.main()
