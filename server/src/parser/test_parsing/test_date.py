import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from date import Date

class TestDate(unittest.TestCase):
    
    def test_basic_date(self):
        date = Date("25/11/1728")
        self.assertEqual(date.date_str, "25/11/1728")
        self.assertIsNone(date.modifier)
        self.assertEqual(date.calendar, 'G')
    
    def test_date_with_modifier(self):
        date = Date("~10/5/1990")
        self.assertEqual(date.date_str, "10/5/1990")
        self.assertEqual(date.modifier, "about")
        
        date = Date("<10/5/1990")
        self.assertEqual(date.modifier, "before")
    
    def test_date_with_calendar(self):
        date = Date("10/9/5750H")
        self.assertEqual(date.date_str, "10/9/5750")
        self.assertEqual(date.calendar, 'H')
    
    def test_text_date(self):
        date = Date("0(5_Mai_1990)")
        self.assertEqual(date.text_date, "5_Mai_1990")
        self.assertIsNone(date.date_str)
    
    def test_complex_date(self):
        date = Date("~10/5/1990J")
        self.assertEqual(date.date_str, "10/5/1990")
        self.assertEqual(date.modifier, "about")
        self.assertEqual(date.calendar, 'J')
    
    def test_str_representation(self):
        date = Date("25/11/1728")
        self.assertEqual(str(date), "25/11/1728")
        
        date = Date("0(5_Mai_1990)")
        self.assertEqual(str(date), "5_Mai_1990")

if __name__ == '__main__':
    unittest.main()