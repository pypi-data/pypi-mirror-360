import base64
import hashlib
import hmac
import json
import re
import secrets
import string
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

def calculate_secret_hash(client_id, client_secret, username):
    msg = username + client_id
    dig = hmac.new(str(client_secret).encode('utf-8'),
                 msg=str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
    return base64.b64encode(dig).decode()


def extract_string_values(data):
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = value
    return result


def remove_attributes(arr, attributes_to_remove):
    """
    Removes specified attributes from each item in a list of DynamoDB items.

    Parameters:
        documents (list): List of dictionaries representing DynamoDB items.
        attributes_to_remove (list): List of attribute names (keys) to remove.

    Returns:
        list: The list of dictionaries with specified attributes removed.
    """
    # Iterate over each document in the list
    for doc in arr:
        # Remove specified attributes if they exist in the document
        for attr in attributes_to_remove:
            doc.pop(attr, None)  # 'pop' ensures no error if the key doesn't exist

    return arr


def clean_response(response_text):
    print(f"clean_response response_text: {response_text}")
    cleaned_text = response_text
    if response_text.strip().startswith("```json"):
        cleaned_text = response_text.replace("```json", "", 1)
    if response_text.strip().endswith("```"):
        cleaned_text = cleaned_text.rsplit("```", 1)[0]
    print(f"clean_response cleaned_text: {cleaned_text}")
    return cleaned_text


def clean_markup_string(input_string):
    input_string = input_string.replace("```json ", "").replace("```", "")
    return input_string


def find_complete_json_objects(input_string):
    open_braces = close_braces = 0
    start_index = None
    complete_json_objects = []
    for index, char in enumerate(input_string):
        if char == '{':
            open_braces += 1
            if start_index is None:
                start_index = index
        elif char == '}':
            close_braces += 1
        if open_braces == close_braces and open_braces > 0:
            complete_json_objects.append(input_string[start_index:index+1])
            open_braces = close_braces = 0
            start_index = None
    return complete_json_objects


def find_and_parse_json(input_string):
    input_string = clean_response(input_string)
    input_string = clean_markup_string(input_string)
    try:
        parsed_json = json.loads(input_string)
        return parsed_json
    except json.JSONDecodeError:
        potential_jsons = find_complete_json_objects(input_string)
        valid_json_objects = []
        for json_string in potential_jsons:
            try:
                parsed_json = json.loads(json_string)
                valid_json_objects.append(parsed_json)
            except json.JSONDecodeError:
                continue
    if valid_json_objects:
        return valid_json_objects[0]
    raise ValueError("No valid JSON object found.")


def get_current_month_time_period():
    return datetime.now().strftime('%Y-%m')


def single_to_double_quotes(s):
    # Pattern to match all instances of single quotes that are not within a word
    # or are not part of contractions like "it's", "don't", etc.
    pattern = re.compile(r"(?<!\w)'([^']*)'(?!\w)")

    # Replace single quotes with double quotes using the pattern
    result = pattern.sub(r'"\1"', s)

    return result


# A function to extract the numeric value from a string, removing leading zeros and brackets
def extract_numeric(para_id):
    match = re.search(r'\d+', para_id)
    if match:
        return int(match.group())
    return float('inf')


def find_and_parse_json_array(input_string):
    input_string = clean_response(input_string)
    regex = r'\{.*?\}'
    potential_jsons = re.findall(regex, input_string, re.DOTALL)
    valid_json_objects = []
    print(f"find_and_parse_json potential_jsons: {potential_jsons}")
    for json_string in potential_jsons:
        try:
            parsed_json = json.loads(json_string)
            print(f"find_and_parse_json parsed_json: {parsed_json}")
            valid_json_objects.append(parsed_json)
        except Exception as e:
            try:
                parsed_json = json.loads(single_to_double_quotes(json_string))
                print(f"find_and_parse_json parsed_json 2: {parsed_json}")
                valid_json_objects.append(parsed_json)
            except json.JSONDecodeError:
                continue
    if len(valid_json_objects) > 0:
        return valid_json_objects
    raise Exception(input_string)

def convert_floats_to_decimals(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimals(v) for v in obj]
    else:
        return obj

def extract_digits(s):
    return ''.join([char for char in s if char.isdigit()])


def extract_number(text):
    # Remove commas and slashes from the text
    clean_text = text.replace(',', '').replace('/', '')

    # Extract numbers with more than 6 digits
    numbers = re.findall(r"\b\d{7,}\b", clean_text)

    # Return the first found number if any
    return numbers[0] if numbers else ""


def extract_string_values_from_array(data_array):
    """
    Extracts string values from an array of dictionaries and concatenates them.

    Parameters:
    - data_array (list): A list of dictionaries.

    Returns:
    - A concatenated string of all string values.
    """

    concatenated_strings = []

    for data in data_array:
        for key, value in data.items():
            if isinstance(value, str):
                concatenated_strings.append("{" + key + ": " + value + "},")

    return ' '.join(concatenated_strings)


def remove_duplicates(array1, array2):
    """
    Removes duplicates from array1 that exist in array2.

    Parameters:
    - array1: The main array from which duplicates will be removed.
    - array2: The array containing values that, if found in array1, will be removed from array1.

    Returns:
    - A new list containing the unique values of array1 after removing duplicates.
    """

    # Use a set comprehension to efficiently identify duplicates
    duplicates = {item for item in array2}

    # Return a list without the duplicates
    return [item for item in array1 if item not in duplicates]

def camel_to_snake_case(s):
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    return s.lower()

def random_string(length=10):
    """Generate a random string of letters and digits."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for i in range(length))

def remove_substrings(query_string, substrings_to_remove):
    if not query_string:
        return ""
    for substring in substrings_to_remove:
        query_string = query_string.replace(substring, '')
    return query_string


def parse_characterizations(characterizations_str):
    # Split by comma and then remove leading/trailing spaces
    items = [item.strip() for item in characterizations_str[1:-1].split(',')]

    # Group claim numbers and descriptions
    parsed_items = []
    for item in items:
        print(f"item: {item}")
        match = re.match(r'([\d, ]+):\s?_(.*)', item)
        if match:
            claim_nums, description = match.groups()
            parsed_items.append(f"{claim_nums.strip()} (stating: {description.strip()})")
            print(f"match for item: {item}, with claim_nums: {claim_nums}, and description: {description}")

    return parsed_items


def transform_dict_to_array(d):
    def format_key(key):
        # Replace underscores with spaces and capitalize the first letter of each word
        return ' '.join(word.capitalize() for word in key.split('_'))

    return [{"name": format_key(key), "value": value, "code": key} for key, value in d.items()]


def deep_transform_dict_to_array(d):
    def format_key(key):
        # Replace underscores with spaces and capitalize the first letter of each word
        return ' '.join(word.capitalize() for word in key.split('_'))

    result = []
    for key, value in d.items():
        if isinstance(value, dict):
            # If the value is a dict, recurse
            result.append({
                "name": format_key(key),
                "value": transform_dict_to_array(value),
                "code": key
            })
        else:
            result.append({
                "name": format_key(key),
                "value": value,
                "code": key
            })
    return result

def transform_mpep_vdb_result_to_string(contents):
    print(f"data to be transformed: {str(contents)[:50]}")
    results = []

    for item in contents:
        section_name = item["section_name"]
        section_id = item["section_id"]
        mpep_contents = item["content"]
        mpep_summary = item["summary"]

        results.append(f"MPEP section {section_name} has contents: {mpep_contents}")
        print(f"section {section_name} has contents: {mpep_contents}")

    return ' '.join(results)


def transform_to_prompt_string(terms):
    print(f"data to be transformed: {str(terms)[:50]}")
    results = []

    for term in terms:
        term_name = term['term_name']
        characterizations_list = parse_characterizations(term['characterizations'])

        char_desc = ', '.join(characterizations_list)
        results.append(f'Term "{term_name}" is used in claim {char_desc}')
        print(f"Term '{term_name}' is used in claim {char_desc}")

    return ' '.join(results)

def convert_from_vdb_to_key_val(data_dict):
    print(f"data to be transformed: {str(data_dict)[:50]}")
    if data_dict == "no results":
        return ""
    transformed_data = {}
    for key, value in data_dict.items():
        if key:
            transformed_data[key] = value["knowledge"]
        else:
            key = value["resource_name"]
            transformed_data[key] = value["knowledge"]
    return transformed_data


def transform_json_to_plain_text(data):
    json_str = json.dumps(data)
    # Remove backslashes
    json_str = json_str.replace("\\", "")
    # Remove double quotes around keys and string values
    json_str = json_str.replace('"', '')
    return json_str


def process_data_to_remove_quotes(data):
    if isinstance(data, str):
        # Remove single and double quotes from the string
        return data.replace("'", "").replace('"', '')
    elif isinstance(data, list):
        # Process each item in the list
        return [process_data_to_remove_quotes(item) for item in data]
    elif isinstance(data, dict):
        # Process each key-value pair in the dictionary
        return {key: process_data_to_remove_quotes(value) for key, value in data.items()}
    else:
        return data


def load_json(json_string):
    print(f"load_json for\njson_string: {json_string}")
    try:
        loaded_json = json.loads(json_string)
        new_json = {}
        for key, value in loaded_json.items():
            new_json[key.replace(" ", "_")] = value
        return new_json
    except:
        print(f"unloadable json found, {json_string}")
        return {}


def count_pattern_occurrences(input_text, pattern):
    matches = re.findall(pattern, input_text)
    return len(matches)


def is_list_of_strings(input_list):
    return isinstance(input_list, list) and all(isinstance(item, str) for item in input_list)


def is_list_of_integers(input_list):
    return isinstance(input_list, list) and all(isinstance(item, int) for item in input_list)


def alphanumeric_sort_key(key):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', key)]


def summarize_token_usage(generation_metrics):
    summary = defaultdict(lambda: {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})
    for m in generation_metrics.values():
        if not m or not hasattr(m, "model"):
            continue
        summary[m.model]["input_tokens"] += m.input_tokens
        summary[m.model]["output_tokens"] += m.output_tokens
        summary[m.model]["total_tokens"] += m.input_tokens + m.output_tokens
    return dict(summary)
