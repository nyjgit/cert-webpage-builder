import sys
sys.path.insert(0, '../../src')

import unittest

from validator import validate_row_order, validate_column_order, CertDataError, HeaderDataError
from data_loader import load_json_data

class DataLoaderTest(unittest.TestCase):

    def setUp(self):
        self.valid_test_dict = load_json_data("test_data/cert_data_valid.json")
        self.valid_test_list = ["subject1", "subject2", "subject3", "subject4", "subject5"]


    def test_validate_row_order_same_rowIndex_for_a_subject(self):
        test_dict = load_json_data("test_data/cert_data_sameRowIndex.json")
        expected_error_message = 'The items "a4e624d686e0" and "1b4f0e985197" have the same rowIndex (0) for the subject "subject1".\n'
        expected_error_message += 'The items "a98ec5c50448" and "ec2738feb2bb" have the same rowIndex (2) for the subject "subject4".\n'

        with self.assertRaises(CertDataError) as context:
            validate_row_order(self.valid_test_list, test_dict)

        self.assertEqual(str(context.exception), expected_error_message)


    def test_validate_row_order_different_rowIndex_for_each_subject(self):
        validate_row_order(self.valid_test_list, self.valid_test_dict)


    def test_validate_column_order_wrong_order(self):
        test_list = ["subject1", "subject4", "subject3", "subject2", "subject5"]
        expected_error_message = 'The item with ID "1b4f0e985197" requires the [\'subject1\', \'subject2\'] headers to be grouped together.\n'
        expected_error_message += 'The item with ID "fd61a03af4f7" requires the [\'subject4\', \'subject5\'] headers to be grouped together.\n'

        with self.assertRaises(HeaderDataError) as context:
            validate_column_order(test_list, self.valid_test_dict)

        self.assertEqual(str(context.exception), expected_error_message)


    def test_validate_column_order_correct_order(self):
        validate_column_order(self.valid_test_list, self.valid_test_dict)



if __name__ == "__main__":
    unittest.main()