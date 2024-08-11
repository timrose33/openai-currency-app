from openaidialogue import ContainsStartEndDate

class TestContainsStartEndDate(unittest.TestCase):
    def test_top_level_start_end_date(self):
        data = {'start_date': '2020-03-17', 'end_date': '2020-03-17'}
        self.assertTrue(ContainsStartEndDate(data))

    def test_top_level_start_end(self):
        data = {'start': '2020-03-17', 'end': '2020-03-17'}
        self.assertTrue(ContainsStartEndDate(data))

    def test_nested_start_end_date(self):
        data = {'dates': [{'start_date': '2020-03-17', 'end_date': '2020-03-17'}]}
        self.assertTrue(ContainsStartEndDate(data))

    def test_nested_start_end(self):
        data = {'dates': [{'start': '2020-03-17', 'end': '2020-03-17'}]}
        self.assertTrue(ContainsStartEndDate(data))

    def test_top_level_missing_end_date(self):
        data = {'start_date': '2020-03-17'}
        self.assertFalse(ContainsStartEndDate(data))

    def test_nested_missing_end_date(self):
        data = {'dates': [{'start_date': '2020-03-17'}]}
        self.assertFalse(ContainsStartEndDate(data))

    def test_top_level_none_values(self):
        data = {'start_date': None, 'end_date': None}
        self.assertFalse(ContainsStartEndDate(data))

    def test_nested_none_values(self):
        data = {'dates': [{'start_date': None, 'end_date': None}]}
        self.assertFalse(ContainsStartEndDate(data))

    def test_top_level_empty_dict(self):
        data = {}
        self.assertFalse(ContainsStartEndDate(data))

    def test_non_dict_input(self):
        data = ['start_date', 'end_date']
        self.assertFalse(ContainsStartEndDate(data))

#if __name__ == '__main__':
TestContainsStartEndDate.test_non_dict_input()
    #unittest.main()