import sys
sys.path.insert(0, '../../src')
import validator, non_critical_checks, builder

class E2ETestFailError(Exception):
    pass


def build_html(cert_data_file: str, svg_data_file: str, header_data_file: str, base_html):
    validator.main(cert_data_file, svg_data_file, header_data_file)
    non_critical_checks.main(cert_data_file, header_data_file)
    html_content = builder.main(cert_data_file, svg_data_file, header_data_file, base_html)

    return html_content


def compare_results(out_file: str, out_file_expected: str):
     with open(out_file_expected, "r") as expected_result, open(out_file, "r") as result:
        line_num = 1

        while True:
            result_line = result.readline()
            expected_line = expected_result.readline()

            if result_line != expected_line:
                error_message = f"E2E test failed at line {line_num}\n\n{out_file_expected}, line {line_num}:\n{expected_line}\n{out_file}, line {line_num}:\n{result_line}"
                raise E2ETestFailError(error_message)

            if not expected_line:
                break

            line_num += 1




def main(cert_data_file: str, svg_data_file: str, header_data_file: str, test_cases: list):
    
    for test_case in test_cases:
        html_content = build_html(cert_data_file, svg_data_file, header_data_file, test_case["base_html"])
        builder.write_file(test_case["out_file"], html_content)

        try:
            compare_results(test_case["out_file"], test_case["out_file_expected"])
        except E2ETestFailError as e:
            print(f"::error::{e}")
            sys.exit(1)


if __name__ == "__main__":
    cert_data_file = "test_data/cert_data.json"
    svg_data_file = "test_data/svg_data.json"
    header_data_file = "test_data/header_data.json"

    base_html_templates = [
        "test_templates/indent_2.html",
        "test_templates/indent_4.html",
        "test_templates/no_indent.html",
        "test_templates/compact.html"
    ]
    out_files_expected = [
        "expected_results/indent_2.html",
        "expected_results/indent_4.html",
        "expected_results/no_indent.html",
        "expected_results/compact.html"
    ]
    out_files = [
        "output/test_result_indent_2.html",
        "output/test_result_indent_4.html",
        "output/test_result_no_indent.html",
        "output/test_result_compact.html"
    ]

    number_of_test_cases = min(len(base_html_templates), len(out_files_expected), len(out_files))
    test_cases = []
    for i in range(number_of_test_cases):
        test_cases.append({
            "base_html": base_html_templates[i],
            "out_file_expected": out_files_expected[i],
            "out_file": out_files[i]
        })

    main(cert_data_file, svg_data_file, header_data_file, test_cases)
