import unittest     # see: https://docs.python.org/3/library/unittest.html
import src.HillRepeats as hr

# test the helper functions

class TestHillRepeats(unittest.TestCase):

    def test_no_filename(self):
        # ensure system exits with an invalid or missing filename
        with self.assertRaises(SystemExit):
            # this should print an error msg that the activity file was not found
            self.assertTrue(hr.load_split_lines(""))

    def test_num_str_to_float_parentheses_negative(self):
        self.assertEqual(hr.num_str_to_float("(123.456)"), float("-123.456"))
        self.assertEqual(hr.num_str_to_float(" (123.456)"), float("-123.456"))
        self.assertEqual(hr.num_str_to_float("(123.456) "), float("-123.456"))
        self.assertEqual(hr.num_str_to_float(" (123.456) "), float("-123.456"))

    def test_num_str_to_float_hyphen_to_zero(self):
        self.assertEqual(hr.num_str_to_float("-"), float(0))
        self.assertEqual(hr.num_str_to_float(" -"), float(0))
        self.assertEqual(hr.num_str_to_float("- "), float(0))
        self.assertEqual(hr.num_str_to_float(" - "), float(0))

    def test_num_str_to_float_remove_commas(self):
        # NOTE: this will not work as expected in European locales b/c 1.00 (USA) == 1,00 (EU)
        self.assertEqual(hr.num_str_to_float("1,000.00"), float(1000.00))
        self.assertEqual(hr.num_str_to_float("(1,000.99)"), float(-1000.99))

# self contained
if __name__ == '__main__':
    unittest.main()