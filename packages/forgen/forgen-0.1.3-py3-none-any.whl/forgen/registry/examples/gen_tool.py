from forgen.tool.builder import GenToolBuilder
from forgen.ddb.tooling import get_tool_registry_items_by_id
from forgen.registry.deserialize import deserialize_operand
from forgen.registry.store import store_pipeline_operand_to_registry

# Step 1: Define a standard framework-based generative tool using GenToolBuilder
builder = GenToolBuilder(
    name="ComplimentTool",
    input_schema={"name": str},
    output_schema={"compliment": str},
    system_prompt="You are a kind assistant. Only return a JSON object that includes a compliment.",
    user_prompt_template="Give a kind compliment to {name}.",
    description="Gives a compliment"
)

tool = builder.build()

# Step 2: Execute the tool BEFORE storing (simulate test mode)
input_payload = {"name": "James"}
original_output = tool.execute(input_payload)
print("🔹 Original tool output:", original_output)

# Step 3: Store to ToolRegistry (DynamoDB)
store_pipeline_operand_to_registry(tool, username="demo_user")

# Step 4: Retrieve tool from registry and deserialize
item = get_tool_registry_items_by_id("demo_user", "ComplimentTool:0.0.1")
rehydrated_tool = deserialize_operand(item)

# Step 5: Execute the rehydrated tool
rehydrated_output = rehydrated_tool.execute(input_payload)
print("🔸 Rehydrated tool output:", rehydrated_output)

