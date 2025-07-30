import inspect


def safe_merge(output: dict, new_data):
    """
    Safely merges new_data into output, ensuring new_data is a dictionary.
    If new_data is a list of dicts, it merges all dicts into one.
    """
    if isinstance(new_data, list):
        merged_dict = {}
        for item in new_data:
            if isinstance(item, dict):
                merged_dict.update(item)  # Merge dictionaries inside the list
        new_data = merged_dict  # Use the flattened version

    elif not isinstance(new_data, dict):
        raise TypeError(f"Unexpected type for new_data: {type(new_data)}")

    return {**output, **new_data}


def list_to_dict(lst):
    """
    Converts a list into a dictionary where indices are keys.

    :param lst: The input list
    :return: Dictionary with index as key and list elements as values
    """
    if not isinstance(lst, list):
        raise TypeError("Input must be a list.")

    return {i: value for i, value in enumerate(lst)}


def convert_to_expected_type(value, expected_type):
    """ Converts the value to the expected type if possible. """
    try:
        if expected_type == str:
            return str(value)
        elif expected_type == int:
            return int(value) if isinstance(value, (float, str)) and value.isdigit() else None
        elif expected_type == float:
            return float(value) if isinstance(value, (int, str, float)) else None
        elif expected_type == list:
            return list(value) if isinstance(value, (tuple, set)) else [value]
        elif expected_type == dict:
            return dict(value) if isinstance(value, dict) else {"converted_value": value}
        else:
            return value  # If it's already the expected type
    except ValueError:
        return None


def enforce_schema(raw_output, output_schema):
    """Attempts to enforce the output schema by converting raw_output to match the expected type.

    Args:
        raw_output: The generated output that needs validation.
        output_schema: A dictionary mapping expected keys to expected types.

    Returns:
        A dictionary with the expected key and the converted value, if conversion is successful.

    Raises:
        ValueError: If conversion is not possible.
    """
    if len(output_schema) == 1:  # Ensure only one expected type
        expected_key, expected_type = next(iter(output_schema.items()))

        # Try converting raw_output to the expected type
        converted_output = convert_to_expected_type(raw_output, expected_type)

        if converted_output is not None:
            return {expected_key: converted_output}  # Store as a properly formatted dictionary
        else:
            raise ValueError(f"Could not convert raw_output {raw_output} to {expected_type}")

    return raw_output  # Return raw_output unchanged if schema does not enforce a single type


def validate_data(data, validate_schema_fn, schema, label, forced_interface, allow_partial=False):
    """
    Validates data against a schema and applies conversion if forced_interface is enabled.

    Args:
        data: The input/output data to validate.
        validate_schema_fn (function): Function that validates schema.
        schema (dict): The expected schema (dict of {key: type}).
        label (str): Label for validation phase.
        forced_interface (bool): Whether to enforce schema conversion on failure.
        allow_partial (bool): Whether to allow partial matches to pass during forced_interface

    Returns:
        Validated or converted data.

    Raises:
        ValueError: If validation fails and conversion is not possible.
    """
    try:
        validate_schema_fn(data, schema, label)  # Call the provided validation function
    except ValueError as validation_error:
        if forced_interface:
            try:
                return enforce_schema(data, schema)
            except Exception as conversion_error:
                print(f"[WARN] {label} had missing or invalid fields but proceeding due to partial match: {conversion_error}")
                if allow_partial:
                    non_empty_keys = [k for k in schema if k in data and data[k]]
                    if non_empty_keys:
                        print(f"[WARN] {label} had missing or invalid fields but proceeding due to partial match: {non_empty_keys}")
                        return data
                raise ValueError(f"Schema validation failed: {validation_error} "
                                 f"and conversion failed: {conversion_error}")
        else:
            raise validation_error  # Re-raise original validation error if conversion is not allowed
    return data  # Return unchanged if validation succeeds


def get_batch_input(input_data):
    """
    Extracts batch input from `input_data`, ensuring it is always returned as a list.

    Args:
        input_data (any): The input data to normalize.

    Returns:
        list: A list of items to process in batch mode.
    """
    if isinstance(input_data, list):
        return input_data  # Already a list
    elif isinstance(input_data, dict):
        if len(input_data) == 1:
            # Single-key dictionary: Extract its value
            single_key = next(iter(input_data))
            value = input_data[single_key]
            return value if isinstance(value, list) else [value]  # Ensure list format
        # Multi-key dictionary: Collect all values into a single list
        batch_data = []
        for value in input_data.values():
            if isinstance(value, list):
                batch_data.extend(value)  # Merge lists
            else:
                batch_data.append(value)  # Convert single values to list items
        return batch_data
    # If it's a single value (not list or dict), wrap it in a list
    return [input_data]


def validate_function_signature(func, required_params):
    if not callable(func):
        raise ValueError(f"The provided function {func} is not callable.")

    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())
    missing = [p for p in required_params if p not in param_names]
    if missing:
        raise ValueError(f"The function {func.__name__} is missing required parameters: {missing}.")


def convert_def_to_callable(code_str: str, fn_name: str) -> callable:
    """
    Convert a full function definition string into a callable.
    `fn_name` is the name of the function defined in the code_str.
    """
    try:
        loc = {}
        exec(code_str, {}, loc)
        if fn_name not in loc or not callable(loc[fn_name]):
            raise ValueError(f"No callable named '{fn_name}' was found.")
        return loc[fn_name]
    except Exception as e:
        raise ValueError(f"Error executing function string: {e}")
