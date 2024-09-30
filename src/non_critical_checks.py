from data_loader import load_json_data
import sys


def check_cert_subjects(subject_list: list, cert_data: dict):
    warnings = []
    for item_id, item in cert_data.items():
        if len(item["subjects"]) == 0:
            warnings.append(f"The item with ID \"{item_id}\" won't be included in the table because it has no subjects assigned.")
        for subject in item["subjects"]:
            if subject not in subject_list:
                warnings.append(f"The item with ID \"{item_id}\" won't be included in the table because the subject \"{subject}\" is not included in the header list.")
    return warnings



def main(cert_data_filename, header_data_filename):
    cert_data = load_json_data(cert_data_filename)
    header_data = load_json_data(header_data_filename)


    cert_data = {item_id:item for item_id,item in cert_data.items() if item["display"]}
    subject_list = [header_subject_pair[1] for header_subject_pair in header_data["order"]]


    warnings = check_cert_subjects(subject_list, cert_data)
    if warnings:
        for warning in warnings:
            print(f"::warning::{warning}")
        sys.exit(1)


if __name__ == "__main__":
    cert_data_file = "../data/cert_data.json"
    header_data_file = "../data/header_data.json"

    main(cert_data_file, header_data_file)
