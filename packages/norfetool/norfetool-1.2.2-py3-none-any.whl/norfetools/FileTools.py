import os
import re

class Sl:
    @staticmethod
    def ensure_directory_exists(file_path):
        directory = os.path.dirname(file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    @staticmethod
    def replace_strings_in_file(file_name, replace_dict, new_file_path):
        Sl.ensure_directory_exists(new_file_path)
        with open(file_name, 'r', encoding='utf-8') as file:
            file_contents = file.read()
        new_contents = file_contents
        for old_string, new_string in replace_dict.items():
            new_contents = re.sub(re.escape(old_string), new_string, new_contents)
        with open(new_file_path, 'w', encoding='utf-8') as new_file:
            new_file.write(new_contents)
        print(f"File has been saved to {new_file_path} with the updated content.")