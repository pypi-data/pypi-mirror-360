import re
from typing import Any, Dict, List, Union

import uspto_data.response.bulk_dataset.ref.product_data


def generate_class_name(key: str) -> str:
    """Converts a JSON key into a properly formatted PascalCase class name."""
    # Handle both snake_case and camelCase
    parts = re.split(r'[_\s]+|(?=[A-Z])', key)
    return ''.join(word.capitalize() for word in parts if word)


def sanitize_key(key: str) -> str:
    """
    Sanitizes a JSON key to be a valid Python identifier.
    Replaces invalid characters (e.g., '/') and reserved keywords (e.g., 'class').
    """
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', key)
    # Handle reserved keywords (e.g., class -> class_)
    if sanitized in {"class", "def", "return", "lambda"}:  # Add more Python keywords as needed
        sanitized += "_"
    return sanitized


def infer_type(value: Any) -> str:
    """Infers the type of a value in the JSON."""
    if isinstance(value, str):
        return "str"
    elif isinstance(value, bool):
        return "bool"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, list):
        if len(value) > 0:
            return f"List[{infer_type(value[0])}]"
        else:
            return "List[Any]"
    elif isinstance(value, dict):
        return generate_class_name("nested")
    else:
        return "Any"


def write_to_file(json_obj: Union[Dict, List], endpoint, filename: str = "generated_classes.py") -> None:
    """Writes the generated Python dataclass definitions to a .py file."""
    class_definitions = parse_json_to_dataclass(json_obj)
    with open(filename, 'w') as file:
        # Import statements
        file.write("from dataclasses import dataclass, field\n")
        file.write("from typing import List, Optional\n\n\n")
        # Class definitions
        file.write(class_definitions)
        file.write(f"\n\nendpoint = \"{str(endpoint)}\"\n\n")
        file.write(f"#  EXAMPLE JSON RESPONSE\n\nexample_json = {json_obj}\n")
    print(f"Dataclass definitions written to {filename}")


def parse_json_to_dataclass(json_obj, class_name="Root") -> str:
    """
    Recursively parses a JSON object into Python dataclass definitions.
    Ensures fields with defaults come after fields without defaults.
    """
    if isinstance(json_obj, list):
        json_obj = json_obj[0] if json_obj else {}

    required_fields = []  # Fields without defaults
    optional_fields = []  # Fields with defaults
    nested_classes = []   # Nested dataclasses

    for key, value in json_obj.items():
        sanitized_key = sanitize_key(key)
        if isinstance(value, dict):
            # Nested dictionary becomes a new dataclass
            nested_class_name = generate_class_name(sanitized_key)
            nested_classes.append(parse_json_to_dataclass(value, nested_class_name))
            required_fields.append(f"    {sanitized_key}: {nested_class_name}")
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            # List of nested dictionaries becomes a list of dataclasses
            nested_class_name = generate_class_name(sanitized_key)
            nested_classes.append(parse_json_to_dataclass(value[0], nested_class_name))
            required_fields.append(f"    {sanitized_key}: List[{nested_class_name}]")
        else:
            # Scalar fields (Optional fields with defaults)
            field_type = infer_type(value)
            if sanitized_key != key:  # If key was sanitized, add an alias
                optional_fields.append(
                    f"    {sanitized_key}: Optional[{field_type}] = field(metadata={{'alias': '{key}'}})"
                )
            else:
                optional_fields.append(f"    {sanitized_key}: Optional[{field_type}] = None")

    # Combine required and optional fields (required fields come first)
    all_fields = required_fields + optional_fields

    # Create the dataclass definition
    class_definition = f"@dataclass\nclass {class_name}:\n" + '\n'.join(all_fields)
    nested_definitions = '\n\n'.join(nested_classes)
    return (f"{nested_definitions}\n\n{class_definition}" if nested_classes else class_definition) + '\n'



def get_endpoint_name(endpoint: str) -> str:
    """
    Converts an API endpoint string into a simplified, readable name.

    Example:
        Input: "/api/v1/patent/applications/search"
        Output: "search"
    """
    # Split the endpoint by "/" and filter out empty parts
    parts = [part for part in endpoint.split("/") if part]

    # Return the last part, which is typically the endpoint name
    if parts:
        return parts[-1]
    return "default"


if __name__ == '__main__':
    input_1 = uspto_data.uspto_response.bulk_dataset.ref.product_data.example_json
    endpoint = uspto_data.uspto_response.bulk_dataset.ref.product_data.endpoint
    class_definition_python = parse_json_to_dataclass(input_1)
    python_file_name = get_endpoint_name(endpoint) + ".py"
    write_to_file(input_1, endpoint, python_file_name)
    print(f"Python data class file generated: {python_file_name}")
