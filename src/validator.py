from data_loader import load_json_data, LoadDataError
import sys

class CertDataError(Exception):
    pass

class HeaderDataError(Exception):
    pass


def validate_row_order(subject_list: list, cert_data: dict):
    error_message = ""
    for subject in subject_list:
        rowIndex_map = {}
        for item_id, item in cert_data.items():
            if subject not in item["subjects"]:
                continue
            
            row_index = item["rowIndex"]
            if row_index in rowIndex_map:
                error_message += f'The items "{item_id}" and "{rowIndex_map[row_index]}" have the same rowIndex ({row_index}) for the subject "{subject}".\n'
            
            rowIndex_map[item["rowIndex"]] = item_id
    
    if error_message:
        raise CertDataError(error_message)


def validate_column_order(subject_list: list, cert_data: dict):
    error_message = ""
    for item_id, item in cert_data.items():
        if len(item["subjects"]) <= 1:
            continue

        validator_list = [subject_list.index(subject) for subject in item["subjects"]]
        validator_list.sort()

        for i in range(1, len(validator_list)):
            if validator_list[i]-validator_list[i-1] != 1:
                error_message += f'The item with ID "{item_id}" requires the {item["subjects"]} headers to be grouped together.\n'

    if error_message:
        raise HeaderDataError(error_message)



def main(cert_data_filename, svg_data_filename, header_data_filename):
    try:
        cert_data = load_json_data(cert_data_filename)
        load_json_data(svg_data_filename)
        header_data = load_json_data(header_data_filename)
    except LoadDataError as e:
        print(f"\nData validation failed: {e}\n")
        sys.exit(1)

    cert_data = {item_id:item for item_id,item in cert_data.items() if item["display"]}
    subject_list = [header_subject_pair[1] for header_subject_pair in header_data["order"]]

    try:
        validate_row_order(subject_list, cert_data)       # checking if each (subject - row_index) combination is unique (==> each cell will have max. 1 entry)
        validate_column_order(subject_list, cert_data)    # colspan in the final table requires some colums to be grouped together
    except CertDataError as e:
        print(f'\nData validation failed:\ncert_data.json: {e}')
        sys.exit(1)
    except HeaderDataError as e:
        print(f'\nData validation failed:\nheader_data.json: {e}')
        sys.exit(1)


if __name__ == "__main__":
    cert_data_file = "../data/cert_data.json"
    svg_data_file = "../data/svg_data.json"
    header_data_file = "../data/header_data.json"

    main(cert_data_file, svg_data_file, header_data_file)
