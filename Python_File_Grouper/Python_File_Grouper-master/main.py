#!usr/bin/python3
# Script to group files in a folder based on the file extensions.

# Importing all required libraries.
import os
import json
import random
import string
import pickle
from tkinter import *
from tkinter import filedialog
import config as tool_config
import shutil  # For moving and copying files.
import hashlib  # For finding hash of a file.


def get_file_extension_type(_file_ext):
    global pivoted_config_dic
    return pivoted_config_dic.get(_file_ext, tool_config.OTHER_FILES_DIR)


def check_if_duplicate_file_exist(_file_name):
    global file_names_set
    if _file_name in file_names_set:
        return True
    return False


def get_base_name_and_file_ext(_file_name):
    if '.' in _file_name:
        return _file_name.rsplit('.', 1)  # Split file name based on the last occurrence of the delimiter.
    return _file_name, ''


def generate_random_string():
    # Return a string of length k.
    generated_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return generated_string


initial_run = True

# Dictionary to store the pivoted information of the extension and extension_type in the json file.
pivoted_config_dic = dict()

# Set to store file name and count.
file_names_set = set()

# Dictionary to store the input and output file full path.
input_output_filename_dic = dict()

root = Tk()
root.withdraw()  # To cancel popping out of the tkinter window.

# Read the config file.
config_content = open(tool_config.EXTENSION_CONFIG_JSON_FILE_PATH, "r")

# Store config json in a dictionary.
config_dic = json.load(config_content)

# Set to store the hash of the file.
file_hash_set = set()

# Pivot the extension and extension_type in the config dictionary.
for extension_type, extension_list in config_dic.items():
    for extension in extension_list:
        pivoted_config_dic[extension] = extension_type

# Selecting the input and output directory.
selected_input_dir = filedialog.askdirectory(initialdir=os.getcwd(), title='Select the input directory to sort')
selected_output_dir = filedialog.askdirectory(initialdir=os.getcwd(), title='Select output directory')
output_dir = os.path.join(selected_output_dir, tool_config.GROUPED_FILES_BASE_DIR)
hash_file_name = os.path.join(output_dir, tool_config.HASH_FILE_NAME)

# Check for initial run status.
if os.path.exists(output_dir) and os.path.exists(hash_file_name):
    with open(hash_file_name, "rb") as hash_file_content:
        file_hash_set = pickle.load(hash_file_content)
    initial_run = False

# Loop through the input folder and get the list of all files.
for root_dir, sub_dir, file_name_list in os.walk(selected_input_dir):
    if file_name_list:
        for file_name in file_name_list:
            input_file_full_path = os.path.join(root_dir, file_name)
            print("Reading Hash: {}".format(input_file_full_path))

            with open(input_file_full_path, 'rb') as file_content:
                file_binary_info = file_content.read()

            # Calculating the hash of file.
            file_hash = hashlib.md5(file_binary_info).hexdigest()

            if file_hash in file_hash_set:
                continue

            file_hash_set.add(file_hash)

            is_duplicate_file_exist = check_if_duplicate_file_exist(file_name)

            # Updating the file name set.
            file_names_set.add(file_name)

            base_file_name, file_extension = get_base_name_and_file_ext(file_name)

            file_extension = file_extension.lower()

            extension_type = get_file_extension_type(file_extension)

            file_extension_folder = tool_config.NO_EXTENSION_FILES_DIR if file_extension == '' else file_extension

            random_string = ''
            if is_duplicate_file_exist:
                random_string = "_" + generate_random_string()

            if file_extension == '':
                new_file_name = base_file_name + random_string
            else:
                new_file_name = base_file_name + random_string + "." + file_extension

            output_file_full_path = os.path.join(output_dir, extension_type, file_extension_folder, new_file_name)

            if not initial_run:
                output_file_full_path = os.path.join(output_dir, extension_type, file_extension_folder,
                                                     tool_config.NEW_FILE_DIR_NAME, new_file_name)

            # Add the input and output file name into the dictionary.
            input_output_filename_dic[input_file_full_path] = output_file_full_path

for input_file_name, output_file_name in input_output_filename_dic.items():
    output_dir_name = os.path.dirname(output_file_name)

    # Create required output directories.
    if not os.path.exists(output_dir_name):
        os.makedirs(output_dir_name)

    # Moving files.
    shutil.move(input_file_name, output_file_name)

# Save the hash of all files in the root folder.
with open(hash_file_name, 'wb') as out_file:
    pickle.dump(file_hash_set, out_file)

print("Files grouped successfully.")
