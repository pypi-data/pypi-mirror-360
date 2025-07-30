import inspect
import textwrap

from forgen.util.type import validate_data


class BasePhase:
    def __init__(self, phase_name: str = None, input_data=None, input_schema=None, output_schema=None, code=None,
                 forced_interface=False):
        """
        A base class for processing different phases (Input, Generation, Output).

        :param phase_name: The name of the phase (e.g., "InputPhase", "GenerativePhase").
        :param input_data: Data received for this phase.
        :param input_schema: Schema defining the expected structure of input_data.
        :param output_schema: Schema defining the expected structure of processed output.
        :param code: Optional function or string to process the input.
        :param forced_interface: Whether to enforce schema constraints on errors.
        """
        self.phase_name = phase_name
        self.input_data = input_data
        self.input_schema = input_schema
        self.output_schema = input_schema if output_schema is None else output_schema
        self.code = code
        self.forced_interface = forced_interface
        self.output_data = None

    def __str__(self):
        return str(self.to_dict())

    def _convert_schema(self, schema: dict) -> dict:
        return {
            k: (v.__name__ if isinstance(v, type) else str(v))
            for k, v in schema.items()
        }

    def to_dict(self):
        code_str = None

        if callable(self.code):
            try:
                # Try to get the actual source
                code_str = inspect.getsource(self.code)
                code_str = textwrap.dedent(code_str).strip()
                if "<lambda>" in code_str or code_str.startswith("("):
                    # Avoid serializing lambdas or inline callables
                    code_str = None
            except Exception:
                code_str = None
        elif isinstance(self.code, str):
            code_str = self.code.strip()

        return {
            "phase_name": self.phase_name,
            "input_data": self.input_data,
            "input_schema": self._convert_schema(self.input_schema),
            "output_schema": self._convert_schema(self.output_schema),
            "code": code_str,
            "forced_interface": self.forced_interface,
            "output_data": self.output_data,
        }

    @property
    def input(self):
        """
        Return full input_data with any missing schema fields filled in using defaults.
        """
        default_map = {str: "", int: 0, float: 0.0, bool: False, list: [], dict: {}}
        result = dict(self.input_data) if isinstance(self.input_data, dict) else {}

        for key, expected_type in (self.input_schema or {}).items():
            if key not in result:
                result[key] = default_map.get(expected_type, None)

        return result

    @property
    def output(self):
        """
        Return full output_data with any missing schema fields filled in using defaults.
        """
        default_map = {str: "", int: 0, float: 0.0, bool: False, list: [], dict: {}}
        result = dict(self.output_data) if isinstance(self.output_data, dict) else {}

        for key, expected_type in (self.output_schema or {}).items():
            if key not in result:
                result[key] = default_map.get(expected_type, None)

        return result

    def validate_schema(self, data, schema, label):
        """Validate the data against a schema."""
        if not schema:
            return
        try:
            for field, expected_type in schema.items():
                if field not in data:
                    raise ValueError(f"Missing required field in {label}: '{field}'")
                if not isinstance(data[field], expected_type):
                    raise ValueError(f"Field '{field}' in {label} must be of type '{expected_type.__name__}', "
                                     f"but got '{type(data[field]).__name__}'.")
        except ValueError as validation_error:
            raise validation_error

    def execute_code(self, input_data):
        """Executes optional processing code, either as a function or dynamically evaluated string."""
        if callable(self.code):
            return self.code(input_data)
        elif isinstance(self.code, str):
            local_scope = {"input_data": input_data.copy() if isinstance(input_data, dict) else input_data}
            try:
                exec(self.code, {}, local_scope)
                fn = next((v for v in local_scope.values() if callable(v)), None)
                if fn:
                    return fn(input_data)
            except Exception as e:
                raise RuntimeError(f"Error executing dynamic code: {e}")
        return input_data

    def extract_first_matching_key(self, input_data, target_key):
        if isinstance(input_data, dict):
            for key, value in input_data.items():
                if key == target_key:
                    return {key: value}
                elif isinstance(value, dict):
                    result = self.extract_first_matching_key(value, target_key)
                    if result:
                        return result
                elif isinstance(value, list):
                    for item in value:
                        result = self.extract_first_matching_key(item, target_key)
                        if result:
                            return result
        elif isinstance(input_data, list):
            for item in input_data:
                result = self.extract_first_matching_key(item, target_key)
                if result:
                    return result
        return input_data

    def extract_and_cast_from_input(self):
        """
        Extracts data from nested input_data using the input_schema.
        - Attempts to cast values to expected types if forced_interface is True.
        - If a schema key is missing and forced_interface is True,
          finds a nested value of the correct type or uses the entire input_data as fallback.
        :return: A dictionary with extracted and type-conformed data.
        """
        if not self.input_schema or not self.input_data:
            return self.input_data

        result = dict(self.input_data) if isinstance(self.input_data, dict) else {}

        def find_first_value_by_type(data, _expected_type):
            if isinstance(data, dict):
                for _key, _value in data.items():
                    if isinstance(_value, _expected_type):
                        return _value
                    elif isinstance(_value, (dict, list)):
                        _match = find_first_value_by_type(_value, _expected_type)
                        if _match is not None:
                            return _match
            elif isinstance(data, list):
                for item in data:
                    _match = find_first_value_by_type(item, _expected_type)
                    if _match is not None:
                        return _match
            return None

        for key, expected_type in self.input_schema.items():
            match = self.extract_first_matching_key(self.input_data, key)
            if match and key in match:
                value = match[key]
                if isinstance(value, expected_type):
                    result[key] = value
                elif self.forced_interface:
                    try:
                        result[key] = expected_type(value)
                    except (ValueError, TypeError):
                        raise TypeError(
                            f"Cannot cast field '{key}' to {expected_type.__name__}; got value: {value} ({type(value).__name__})"
                        )
            elif self.forced_interface:
                fallback_value = find_first_value_by_type(self.input_data, expected_type)
                if fallback_value is not None:
                    result[key] = fallback_value
                else:
                    try:
                        result[key] = expected_type(self.input_data)
                    except (ValueError, TypeError):
                        raise ValueError(
                            f"Missing key '{key}' and could not find or convert input_data to {expected_type.__name__}"
                        )
        return result

    def execute(self, input_data="", output_key=None):
        """
        Validate input, process data, and validate output.
        :return: Processed and validated data conforming to the output schema.
        """
        if not input_data:
            input_data = self.extract_and_cast_from_input() if self.forced_interface else self.input_data
            self.input_data = input_data if input_data else self.input_data
        else:
            self.input_data = input_data
        validated_input = validate_data(self.input_data, self.validate_schema, self.input_schema,
                                        f"{self.phase_name} input", self.forced_interface, allow_partial=self.forced_interface)
        self.output_data = self.execute_code(validated_input)
        data_to_verify = self.output_data
        if output_key is not None and output_key in self.output_data:
            data_to_verify = self.output_data[output_key]
        validated_data = validate_data(data_to_verify, self.validate_schema, self.output_schema, f"{self.phase_name} output",
                             self.forced_interface, allow_partial=self.forced_interface)
        if output_key is not None:
            self.output_data[output_key] = validated_data
        return self.output_data
