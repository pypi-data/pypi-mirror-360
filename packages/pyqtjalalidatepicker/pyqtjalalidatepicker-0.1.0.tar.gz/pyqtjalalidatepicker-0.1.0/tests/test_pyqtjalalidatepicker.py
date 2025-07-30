import unittest
from PyQt5.QtWidgets import QApplication
from qtjalalicomponent import JalaliDatePicker
import jdatetime
import sys

class TestJalaliDatePicker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def test_initial_date(self):
        picker = JalaliDatePicker()
        today = jdatetime.date.today()
        self.assertEqual(picker.get_jalali_date(), today)

    def test_set_date(self):
        picker = JalaliDatePicker()
        test_date = jdatetime.date(1404, 1, 15)
        picker.set_jalali_date(test_date)
        self.assertEqual(picker.get_jalali_date(), test_date)
        self.assertEqual(picker.text(), "1404/01/15")

if __name__ == '__main__':
    unittest.main()