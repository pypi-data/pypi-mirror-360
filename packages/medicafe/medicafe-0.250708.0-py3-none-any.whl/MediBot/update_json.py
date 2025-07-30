# update_json.py
import json
import sys
from collections import OrderedDict

def get_current_csv_path(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file, object_pairs_hook=OrderedDict)
                return data.get('CSV_FILE_PATH', None)
            except ValueError as decode_err:
                print("Error decoding JSON file '{}': {}".format(json_file, decode_err))
                sys.exit(1)
    except IOError as io_err:
        print("Error accessing file '{}': {}".format(json_file, io_err))
        sys.exit(1)
    except Exception as e:
        print("An unexpected error occurred: {}".format(e))
        sys.exit(1)
    return None

def update_csv_path(json_file, new_path):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file, object_pairs_hook=OrderedDict)
            except ValueError as decode_err:
                print("Error decoding JSON file '{}': {}".format(json_file, decode_err))
                sys.exit(1)

        # Ensure correct backslash formatting for JSON
        if "\\" in new_path and "\\\\" not in new_path:
            formatted_path = new_path.replace("\\", "\\\\")
        else:
            formatted_path = new_path

        data['CSV_FILE_PATH'] = formatted_path

        with open(json_file, 'w', encoding='utf-8') as file:
            try:
                json.dump(data, file, ensure_ascii=False, indent=4)
            except ValueError as encode_err:
                print("Error encoding JSON data to file '{}': {}".format(json_file, encode_err))
                sys.exit(1)

    except IOError as io_err:
        print("Error accessing file '{}': {}".format(json_file, io_err))
        sys.exit(1)
    except Exception as e:
        print("An unexpected error occurred: {}".format(e))
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        json_path = sys.argv[1]
        new_csv_path = sys.argv[2]
        update_csv_path(json_path, new_csv_path)
    elif len(sys.argv) == 2:
        json_path = sys.argv[1]
        current_csv_path = get_current_csv_path(json_path)
        if current_csv_path:
            print(current_csv_path)
        else:
            print("No CSV path found in config.")
    else:
        print("Usage: update_json.py <path_to_json_file> [<new_csv_path>]")
        sys.exit(1)