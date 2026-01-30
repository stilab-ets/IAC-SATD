import json
from pathlib import Path

def write_to_file(new_content):
    file_path = 'terrametrics_dependency/tmp.tf'
    # Open the file in write mode, which clears the existing content
    with open(file_path, 'w') as file:
        # Write the new content to the file
        file.write(new_content)

'''
def return_pair(comment_line):
    # Read the JSON file
    with open('terrametrics_results.json', 'r') as file:
        data = json.load(file)

    # Check if "data" key exists in the JSON object and it's a list
    if 'data' in data and isinstance(data['data'], list):
        # Iterate over each element in the list
        for element in data['data']:
            # Check if "end_block" and "start_block" keys exist in the element
            if 'end_block' in element and 'start_block' and 'block' in element:
                # Print the values of "end_block" and "start_block" for the current element
                #print("start_block:", element['start_block'])
                #print("end_block:", element['end_block'])
                if comment_line <= element['end_block']:
                    return(element['start_block'], element['end_block'])
            else:
                print("'end_block' or 'start_block' key not found in the current element")
    else:
        print("'data' key not found in the JSON object or it's not a list")'''


def extract_associated_block(comment_line):
    # Read the JSON file
    # Get the project root (2 levels up from utils.py)
    PROJECT_ROOT = Path(__file__).resolve().parent

    # Build the absolute path to the JSON
    json_path = PROJECT_ROOT / "terrametrics_results.json"

    with open(json_path, 'r') as file:
        data = json.load(file)

    # Check if "data" key exists in the JSON object and it's a list
    if 'data' in data and isinstance(data['data'], list):
        # Iterate over each element in the list
        for element in data['data']:
            # Check if "end_block", "start_block", and "block" keys exist in the element
            if 'end_block' in element and 'start_block' in element and 'block' in element:
                # Check if the comment line falls within the block range
                if comment_line <= element['end_block']:
                    # Return a tuple of 'start_block', 'end_block', and 'block'
                    #return (element['start_block'], element['end_block'], element['block'])
                    return element
            else:
                print("'end_block', 'start_block', or 'block' key not found in the current element")
        return -1
    else:
        print("'data' key not found in the JSON object or it's not a list")




def extract_associated_block_from_name(block_identifiers):
    # Read the JSON file
    # Get the project root (2 levels up from utils.py)
    PROJECT_ROOT = Path(__file__).resolve().parent

    # Build the absolute path to the JSON
    json_path = PROJECT_ROOT / "terrametrics_results.json"

    with open(json_path, 'r') as file:
        data = json.load(file)

    # Check if "data" key exists in the JSON object and it's a list
    if 'data' in data and isinstance(data['data'], list):
        # Iterate over each element in the list
        for element in data['data']:
            # Check if "block_identifiers" key exists in the element
            if 'block_identifiers' in element:
                # Check if the block_identifiers match
                if element['block_identifiers'] == block_identifiers:
                    # Return the matching element
                    return element
            else:
                print("'end_block', 'start_block', or 'block' key not found in the current element")
        return -1
    else:
        print("'data' key not found in the JSON object or it's not a list")








def extract_code(start_line, end_line):
    file_name = 'terrametrics_dependency/tmp.tf'
    try:
        with open(file_name, 'r') as file:
            lines = file.readlines()
            code_lines = lines[start_line - 1:end_line]
            return ''.join(code_lines)
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
        return None
    except IndexError:
        print("Invalid start or end line numbers.")
        return None
