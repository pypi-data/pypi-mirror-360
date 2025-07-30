from forgen.tool.tool import Tool
from forgen.tool.node import InputPhase, OperativePhase, OutputPhase
from forgen.pipeline.item import PipelineItem
from forgen.pipeline.builder import MultiPathPipelineBuilder
from forgen.registry.deserialize import deserialize_operand
from pprint import pprint


# Tool A: greet with name
def greet_fn(data):
    name = data.get("name", "")
    return {"greeting": f"Hi {name}"}

# Tool B: compute future age
def age_fn(data):
    age = data.get("age", 0)
    return {"age_plus_five": age + 5}

# Tool C: combine outputs
def merge_fn(data):
    g = data.get("greeting", "")
    a = data.get("age_plus_five", 0)
    return {"final": f"{g}, you'll be {a} soon!"}


tool_a = Tool(
    input_phase=InputPhase(input_schema={"name": str}),
    operative_phase=OperativePhase(code=greet_fn, input_schema={"name": str}, output_schema={"greeting": str}),
    output_phase=OutputPhase(input_schema={"greeting": str}),
    input_schema={"name": str},
    output_schema={"greeting": str},
    name="GreetTool"
)

tool_b = Tool(
    input_phase=InputPhase(input_schema={"age": int}),
    operative_phase=OperativePhase(code=age_fn, input_schema={"age": int}, output_schema={"age_plus_five": int}),
    output_phase=OutputPhase(input_schema={"age_plus_five": int}),
    input_schema={"age": int},
    output_schema={"age_plus_five": int},
    name="AgeTool"
)

tool_c = Tool(
    input_phase=InputPhase(input_schema={"greeting": str, "age_plus_five": int}),
    operative_phase=OperativePhase(code=merge_fn, input_schema={"greeting": str, "age_plus_five": int}, output_schema={"final": str}),
    output_phase=OutputPhase(input_schema={"final": str}),
    input_schema={"greeting": str, "age_plus_five": int},
    output_schema={"final": str},
    name="MergeTool"
)

# Wrap as PipelineItems
item_a = PipelineItem(module=tool_a, _id="tool_a")
item_b = PipelineItem(module=tool_b, _id="tool_b")
item_c = PipelineItem(module=tool_c, _id="tool_c")

# Build pipeline
builder = MultiPathPipelineBuilder()
builder.set_name("DualInputMergePipeline")
builder.set_description("Starts with name & age, ends with message")
builder.add_item(item_a).add_item(item_b).add_item(item_c)

builder.add_engine_tuple("tool_a", "tool_c")
builder.add_engine_tuple("tool_b", "tool_c")

pipeline = builder.build()

input_data = {"name": "Jamie", "age": 27}
output = pipeline.execute(input_data)

print("🔹 Final Pipeline Output:")
pprint(output)

# ✅ Serialize
serialized = pipeline.serialize()
rehydrated = deserialize_operand(serialized)
rehydrated_output = rehydrated.execute(input_data)

print("\n🔁 Rehydrated Output:")
pprint(rehydrated_output)

assert output == rehydrated_output, "Mismatch after deserialization"
print("\n✅ Multi-input MultiPathPipeline test passed.")
