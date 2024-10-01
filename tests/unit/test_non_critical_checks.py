import sys
sys.path.insert(0, '../../src')

import unittest

from non_critical_checks import check_cert_subjects
from data_loader import load_json_data

class NonCriticalChecksTest(unittest.TestCase):

    def setUp(self):
        self.test_list = ["subject1", "subject2", "subject3", "subject4", "subject5"]


    def test_warnings(self):
        test_dict = load_json_data("test_data/cert_data_nonCritical.json")
        expected_warnings = ["The item with ID \"ed0cb90bdfa4\" won't be included in the table because it has no subjects assigned."]
        expected_warnings.append("The item with ID \"60303ae22b99\" won't be included in the table because the subject \"subject6\" is not included in the header list.")

        warnings = check_cert_subjects(self.test_list, test_dict)
        
        self.assertEqual(warnings, expected_warnings)


    def test_no_warnings(self):
        test_dict = load_json_data("test_data/cert_data_valid.json")

        warnings = check_cert_subjects(self.test_list, test_dict)
        
        self.assertEqual(warnings, [])



if __name__ == "__main__":
    unittest.main()