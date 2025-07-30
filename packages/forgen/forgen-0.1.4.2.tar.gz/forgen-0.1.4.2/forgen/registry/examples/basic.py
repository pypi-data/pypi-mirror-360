from forgen.tool.builder import ToolBuilder
from forgen.ddb.tooling import get_tool_registry_items_by_id
from forgen.registry.deserialize import deserialize_operand
from forgen.registry.store import store_pipeline_operand_to_registry

# Step 1: Define a basic tool
def greeting_tool(input_data):
    name = input_data.get("name", "World")
    return {"message": f"Hello, {name}!"}

builder = ToolBuilder(name="GreetingTool", description="Returns a greeting.")
builder.set_input_schema({"name": str})
builder.set_output_schema({"message": str})
builder.set_operative_function(greeting_tool)

tool = builder.build()

# Step 2: Execute the tool BEFORE storing
input_payload = {"name": "James"}
original_output = tool.execute(input_payload)
print("🔹 Original tool output:", original_output)

# Step 3: Store to ToolRegistry (DynamoDB)
store_pipeline_operand_to_registry(tool, username="demo_user")

# Step 4: Retrieve tool from registry and deserialize
item = get_tool_registry_items_by_id("demo_user", "GreetingTool:0.0.1")
rehydrated_tool = deserialize_operand(item)

# Step 5: Execute the rehydrated tool
rehydrated_output = rehydrated_tool.execute(input_payload)
print("🔸 Rehydrated tool output:", rehydrated_output)

# Step 6: Compare results
assert original_output == rehydrated_output, "Mismatch in results!"
print("✅ Results match!")
