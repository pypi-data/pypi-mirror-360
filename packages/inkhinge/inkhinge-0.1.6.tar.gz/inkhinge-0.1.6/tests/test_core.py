"""inkhinge包的测试模块"""

import unittest
from inkhinge.core import add_numbers, multiply_numbers


class TestCoreFunctions(unittest.TestCase):
    """测试inkhinge包中的核心函数"""

    def test_add_numbers(self):
        """测试add_numbers函数"""
        self.assertEqual(add_numbers(1, 2), 3)
        self.assertEqual(add_numbers(-1, 1), 0)
        self.assertEqual(add_numbers(1.5, 2.5), 4.0)

    def test_multiply_numbers(self):
        """测试multiply_numbers函数"""
        self.assertEqual(multiply_numbers(2, 3), 6)
        self.assertEqual(multiply_numbers(-2, 3), -6)
        self.assertEqual(multiply_numbers(2.5, 3), 7.5)


if __name__ == '__main__':
    unittest.main()