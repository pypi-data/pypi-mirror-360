from forgen.tool.builder import ToolBuilder


# Create an AgentBuilder instance
builder = ToolBuilder(name="MapMerger")

# Define input and output schemas
dict_merger_input_schema = {
    'dict1': dict,
    'dict2': dict
}
dict_merger_output_schema = {
    'merged_dict': dict
}


# Function to merge two dictionaries by ID
def merge_dictionaries(input_data):
    dict1 = input_data.get("dict1", {})
    dict2 = input_data.get("dict2", {})

    merged_dict = {}

    # Merge both dictionaries based on IDs
    for key, value in dict1.items():
        if key in dict2:
            # Merge values if both dictionaries have the same key
            if isinstance(value, dict) and isinstance(dict2[key], dict):
                merged_dict[key] = {**value, **dict2[key]}
            else:
                merged_dict[key] = [value, dict2[key]]
        else:
            merged_dict[key] = value

    for key, value in dict2.items():
        if key not in merged_dict:
            merged_dict[key] = value

    return {"merged_dict": merged_dict}


# Add nodes to the agent
builder = ToolBuilder(
    name="MapMerger",
    tool_fn=merge_dictionaries,
    input_schema=dict_merger_input_schema,
    output_schema=dict_merger_output_schema,
    description="Merges two dictionaries based on matching IDs, combining values intelligently when both dictionaries "
                "contain the same key. Supports nested dictionary merging and handles conflicts gracefully."
)

# Build the agent
dict_merger_agent = builder.build()

# Example execution of the agent
if __name__ == "__main__":
    user_input = {
        "dict1": {"1": {"name": "Alice", "age": 30}, "2": {"name": "Bob", "age": 25}},
        "dict2": {"1": {"city": "New York"}, "3": {"name": "Charlie", "age": 35}}
    }

    # Execute the agent
    merged_output = dict_merger_agent.execute(user_input)
    print(f"OUTPUT: {str(merged_output)}")
