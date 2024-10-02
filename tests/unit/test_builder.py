import sys
sys.path.insert(0, '../../src')

import unittest
import os
import tempfile

from builder import create_table_of_IDs, find_indent, get_html_table_context, create_indent_function, build_table_header, build_table_body, build_cell_content, write_file
from data_loader import load_json_data

class BuilderTest(unittest.TestCase):

    def setUp(self):
        self.valid_test_dict = load_json_data("test_data/cert_data_valid.json")
        self.valid_test_list = ["subject1", "subject2", "subject3", "subject4", "subject5"]
        self.test_templates = [
            "../test_templates/compact.html",
            "../test_templates/indent_2.html",
            "../test_templates/indent_4.html",
            "../test_templates/no_indent.html"
        ]


    def test_create_table_of_IDs(self):
        expected_result = [
            ['1b4f0e985197', '1b4f0e985197', '60303ae22b99', 'fd61a03af4f7', 'fd61a03af4f7'],
            ['a4e624d686e0', 'a140c0c1eda2', 'a140c0c1eda2', 'a140c0c1eda2', 'ed0cb90bdfa4'],
            ['bd7c911264aa', '1f9bfeb15fee', 'b4451034d3b6', 'ec2738feb2bb', 0],
            ['744ea9ec6fa0', '744ea9ec6fa0', '744ea9ec6fa0', '744ea9ec6fa0', '744ea9ec6fa0'],
            [None, None, None, 'a98ec5c50448', None]]
        
        result = create_table_of_IDs(self.valid_test_dict, self.valid_test_list)

        self.assertEqual(result, expected_result)


    def test_find_indent(self):
        expected_results = [
            (False, 0, 0),
            (True, 2, 3),
            (True, 4, 3),
            (True, 0, 0)
        ]
        
        results = []
        for test_template in self.test_templates:
            with open(test_template, "r", encoding="utf-8") as template_file:
                html_content = template_file.read()
            results.append(find_indent(html_content))

        self.assertEqual(results, expected_results)


    def test_get_html_table_context(self):
        content_before_table_compact = '<!DOCTYPE html><html lang = "en"><head><meta charset="utf-8"><title>Test</title><link rel="stylesheet" href="assets/styles.css"></head><body><div class="table-container">'
        content_before_table_indent_2 = '<!DOCTYPE html>\n<html lang = "en">\n  <head>\n    <meta charset="utf-8">\n    <title>Test</title>\n    <link rel="stylesheet" href="assets/styles.css">\n  </head>\n  <body>\n    <div class="table-container">\n      '
        content_before_table_indent_4 = '<!DOCTYPE html>\n<html lang = "en">\n    <head>\n        <meta charset="utf-8">\n        <title>Test</title>\n        <link rel="stylesheet" href="assets/styles.css">\n    </head>\n    <body>\n        <div class="table-container">\n            '
        content_before_table_no_indent = '<!DOCTYPE html>\n<html lang = "en">\n<head>\n<meta charset="utf-8">\n<title>Test</title>\n<link rel="stylesheet" href="assets/styles.css">\n</head>\n<body>\n<div class="table-container">\n'

        content_after_table_compact = '</div><script src="assets/load.js"></script></body></html>'
        content_after_table_indent_2 = '\n    </div>\n    <script src="assets/load.js"></script>\n  </body>\n</html>'
        content_after_table_indent_4 = '\n        </div>\n        <script src="assets/load.js"></script>\n    </body>\n</html>'
        content_after_table_no_indent = '\n</div>\n<script src="assets/load.js"></script>\n</body>\n</html>'

        expected_results = [
            (False, 0, content_before_table_compact, 0, content_after_table_compact),
            (True, 2, content_before_table_indent_2, 3, content_after_table_indent_2),
            (True, 4, content_before_table_indent_4, 3, content_after_table_indent_4),
            (True, 0, content_before_table_no_indent, 0, content_after_table_no_indent)
        ]

        results = [get_html_table_context(test_template) for test_template in self.test_templates]

        self.assertEqual(results, expected_results)


    def test_create_indent_function(self):
        high_level_args_list = [
            (False, 0, 0),
            (True, 2, 3),
            (True, 0, 0)
        ]

        low_level_args = [0, 1, 3]

        expected_results = [
            ["", "", ""],
            ["\n      ", "\n        ", "\n            "],
            ["\n", "\n", "\n"]
        ]

        results = []
        for high_level_args in high_level_args_list:
            sublist = []
            for low_level_arg in low_level_args:
                get_indentation = create_indent_function(*high_level_args)
                sublist.append(get_indentation(low_level_arg))
            results.append(sublist)
        
        self.assertEqual(results, expected_results)


    def test_table_building(self):
        test_cert_data = {
            "1b4f0e985197": {
                "name": "test1",
                "imgURL": "test1_imgURL",
                "textURL": "test1_textURL",
                "subjects": ["subject1", "subject2"],
                "rowIndex": 0,
                "display": True
            },
            "60303ae22b99": {
                "name": "test2",
                "imgURL": "test2_imgURL",
                "textURL": "test2_textURL",
                "subjects": ["subject2"],
                "rowIndex": 1,
                "display": True
            }
        }

        test_svg_data = {
            "subject1": {
                "URLs": ["subject1a.svg", "subject1b.svg"]
            }
        }

        test_all_subjects_ordered = {"Subject1": "subject1", "Subject2": "subject2"}

        table_of_IDs = [["1b4f0e985197", "1b4f0e985197"], [None, "60303ae22b99"]]

        get_indentation = lambda x: ""

        expected_table_header = '<thead><tr><th><div class="svg-container"><img src="subject1a.svg"><img src="subject1b.svg"></div><div class="text-container">Subject1</div></th><th>Subject2</th></tr></thead>'
        expected_cell_content_1 = '<a href="test1_imgURL" target="_blank"><div class="image-container"><img src="assets/thumbnails/1b4f0e985197.png"></div></a><div class="text-container"><a href="test1_textURL" target="_blank">test1</a></div>'
        expected_cell_content_2 = ''
        expected_cell_content_3 = '<a href="test2_imgURL" target="_blank"><div class="image-container"><img src="assets/thumbnails/60303ae22b99.png"></div></a><div class="text-container"><a href="test2_textURL" target="_blank">test2</a></div>'
        expected_table_body = '<tbody><tr><td colspan="2">'+expected_cell_content_1+'</td></tr><tr><td class="missing">'+expected_cell_content_2+'</td><td>'+expected_cell_content_3+'</td></tr></tbody>'
        
        with self.subTest(function="build_table_header"):
            table_header = build_table_header(test_svg_data, test_all_subjects_ordered, get_indentation)
            self.assertEqual(table_header, expected_table_header)

        with self.subTest(function="build_cell_content"):
            cell_content_1 = build_cell_content(test_cert_data["1b4f0e985197"], "1b4f0e985197", get_indentation)
            cell_content_3 = build_cell_content(test_cert_data["60303ae22b99"], "60303ae22b99", get_indentation)
            self.assertEqual(cell_content_1, expected_cell_content_1)
            self.assertEqual(cell_content_3, expected_cell_content_3)

        with self.subTest(function="build_table_body"):
            table_body = build_table_body(test_cert_data, table_of_IDs, get_indentation)
            self.assertEqual(table_body, expected_table_body)


    def test_write_file(self):

        with tempfile.TemporaryDirectory() as temp_dir:
            test_out_file = "test_result.html"
            test_html_content = "<html>testing</html>"
            
            with self.subTest("with existing parent directory"):
                test_out_file_path = os.path.join(temp_dir, test_out_file)
                write_file(test_out_file_path, test_html_content)

                self.assertTrue(os.path.exists(test_out_file_path))

                with open(test_out_file_path, "r", encoding="utf-8") as file_obj:
                    content = file_obj.read()

                self.assertEqual(content, test_html_content)
            
            with self.subTest("with non-existing parent directory"):
                test_parent_dir = os.path.join(temp_dir, "parentdir")
                test_out_file_path = os.path.join(test_parent_dir, test_out_file)
                write_file(test_out_file_path, test_html_content)

                self.assertTrue(os.path.exists(test_parent_dir))
                self.assertTrue(os.path.exists(test_out_file_path))
                                
                with open(test_out_file_path, "r", encoding="utf-8") as file_obj:
                    content = file_obj.read()
                
                self.assertEqual(content, test_html_content)



if __name__ == "__main__":
    unittest.main()