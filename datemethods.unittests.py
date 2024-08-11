import unittest
from datetime import date
from datemethods import DateRange  # Replace 'your_module_name' with the actual module name
from datemethods import create_date_range  # Replace 'your_module_name' with the actual module name


class TestDateRange(unittest.TestCase):

    def test_create_date_range_valid(self):
        date_dict = {'start_date': '2010-03-20', 'end_date': '2010-03-20'}
        date_range = create_date_range(date_dict)
        self.assertFalse(date_range.is_empty())
        self.assertEqual(date_range.start_date, date(2010, 3, 20))
        self.assertEqual(date_range.end_date, date(2010, 3, 20))

    def test_create_date_range_missing_keys(self):
        date_dict = {'start_date': '2010-03-20'}
        date_range = create_date_range(date_dict)
        self.assertTrue(date_range.is_empty())

        date_dict = {'end_date': '2010-03-20'}
        date_range = create_date_range(date_dict)
        self.assertTrue(date_range.is_empty())

    def test_create_date_range_invalid_format(self):
        date_dict = {'start_date': '2010-03-20', 'end_date': 'invalid-date'}
        date_range = create_date_range(date_dict)
        self.assertTrue(date_range.is_empty())

    def test_contains(self):
        date_range = DateRange(date(2020, 1, 1), date(2020, 1, 10))
        self.assertTrue(date_range.contains(date(2020, 1, 5)))
        self.assertFalse(date_range.contains(date(2020, 1, 11)))

    def test_overlaps(self):
        range1 = DateRange(date(2020, 1, 1), date(2020, 1, 10))
        range2 = DateRange(date(2020, 1, 5), date(2020, 1, 15))
        self.assertTrue(range1.overlaps(range2))

        range3 = DateRange(date(2020, 1, 11), date(2020, 1, 20))
        self.assertFalse(range1.overlaps(range3))

    def test_merge(self):
        range1 = DateRange(date(2020, 1, 1), date(2020, 1, 10))
        range2 = DateRange(date(2020, 1, 5), date(2020, 1, 15))
        merged_range = range1.merge(range2)
        self.assertEqual(merged_range.start_date, date(2020, 1, 1))
        self.assertEqual(merged_range.end_date, date(2020, 1, 15))

        range3 = DateRange(date(2020, 1, 11), date(2020, 1, 20))
        merged_range = range1.merge(range3)
        self.assertTrue(merged_range.is_empty())

    def test_intersection(self):
        range1 = DateRange(date(2020, 1, 1), date(2020, 1, 10))
        range2 = DateRange(date(2020, 1, 5), date(2020, 1, 15))
        intersection_range = range1.intersection(range2)
        self.assertEqual(intersection_range.start_date, date(2020, 1, 5))
        self.assertEqual(intersection_range.end_date, date(2020, 1, 10))

        range3 = DateRange(date(2020, 1, 11), date(2020, 1, 20))
        intersection_range = range1.intersection(range3)
        self.assertTrue(intersection_range.is_empty())
        print("testing intersection")

    def test_subtract(self):
        range1 = DateRange(date(2020, 1, 1), date(2020, 1, 10))
        range2 = DateRange(date(2020, 1, 5), date(2020, 1, 15))
        result = range1.subtract(range2)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].start_date, date(2020, 1, 1))
        self.assertEqual(result[0].end_date, date(2020, 1, 4))

        range3 = DateRange(date(2020, 1, 1), date(2020, 1, 10))
        result = range1.subtract(range3)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].is_empty())

if __name__ == '__main__':
    print("calling main")
    unittest.main()
#TestDateRange.test_intersection()
