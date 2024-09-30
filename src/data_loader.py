import json


class LoadDataError(Exception):
    pass


def load_json_data(filename):
    try:
        with open(filename, "r", encoding="utf-8") as input_file:
            return json.load(input_file)
    except FileNotFoundError:
        raise LoadDataError(f'File "{filename}" not found.')
    except json.JSONDecodeError as e:
        raise LoadDataError(f'Failed to decode "{filename}".\n{e}')
