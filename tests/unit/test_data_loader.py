import sys
sys.path.insert(0, '../../src')

import unittest

from data_loader import load_json_data, LoadDataError

class DataLoaderTest(unittest.TestCase):

    def test_file_not_found(self):
        testfile = "test_data/0000.json"
        with self.assertRaises(LoadDataError) as context:
            load_json_data(testfile)
        self.assertEqual(str(context.exception), f'File "{testfile}" not found.')

    def test_decode_error(self):
        testfile = "test_data/invalid.json"
        with self.assertRaises(LoadDataError) as context:
            load_json_data(testfile)
        
        exception_message = str(context.exception)
        self.assertIn(f'Failed to decode "{testfile}".', exception_message)
        self.assertIn("Expecting ',' delimiter", exception_message)

    def test_successfully_loaded(self):
        testfile = "test_data/valid.json"
        self.assertEqual(load_json_data(testfile), {"name": "testfile", "test": "unittest"})



if __name__ == "__main__":
    unittest.main()