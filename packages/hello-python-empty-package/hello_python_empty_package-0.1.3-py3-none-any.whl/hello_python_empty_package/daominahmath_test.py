import unittest

from daominahmath import add


class TestDaominahMath(unittest.TestCase):
    def test_add(self):
        print("begin TestDaominahMath.test_add")
        self.assertEqual(add(1, 2), 3)
        self.assertEqual(add(-1, 1), 0)
        self.assertEqual(add(0, 0), 0)
        self.assertEqual(add(-5, -7), -12)
        print("end TestDaominahMath.test_add")


if __name__ == '__main__':
    unittest.main()
