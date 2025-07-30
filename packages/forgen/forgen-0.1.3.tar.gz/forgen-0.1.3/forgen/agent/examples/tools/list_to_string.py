from forgen.tool.builder import ToolBuilder


# Function to format a list to a string
def list_to_string(lst):
    return f"OUTPUT: {str(lst)}"


# Create a Tool to format lists
list_to_string_tool = ToolBuilder(
    "ListToString",
    tool_fn=list_to_string,
    input_schema={"list": list},
    output_schema={"output": str},
    description="Converts a list of elements to a string."
)
list_to_string_tool = list_to_string_tool.build()
