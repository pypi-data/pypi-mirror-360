from forgen.registry.store import store_pipeline_operand_to_registry
from forgen.registry.deserialize import deserialize_operand
from forgen.pipeline.pipeline import SerialPipeline
from forgen.tool.builder import ToolBuilder
from forgen.ddb.tooling import get_tool_registry_items_by_id

# Tool 1: Converts text to uppercase
def make_upper(input_data):
    return {"text": input_data["text"].upper()}

# Tool 2: Adds a greeting prefix
def add_prefix(input_data):
    return {"text": f"Hello, {input_data['text']}"}

# ToolBuilder 1
builder1 = ToolBuilder(name="UpperTool")
builder1.set_input_schema({"text": str})
builder1.set_output_schema({"text": str})
builder1.set_operative_function(make_upper)
tool1 = builder1.build()

# ToolBuilder 2
builder2 = ToolBuilder(name="PrefixTool")
builder2.set_input_schema({"text": str})
builder2.set_output_schema({"text": str})
builder2.set_operative_function(add_prefix)
tool2 = builder2.build()

# Build serial pipeline
pipeline = SerialPipeline(name="SimplePipeline", nodes=[tool1, tool2], description="Uppercases and adds a greeting.")

# Store to registry
store_pipeline_operand_to_registry(pipeline, username="demo_user")

# Retrieve and deserialize
item = get_tool_registry_items_by_id("demo_user", "SimplePipeline:0.0.1")
rehydrated_pipeline = deserialize_operand(item)

# Run test input
input_data = {"text": "world"}
result = rehydrated_pipeline.execute(input_data)
print("✅ Final Output:", result)
