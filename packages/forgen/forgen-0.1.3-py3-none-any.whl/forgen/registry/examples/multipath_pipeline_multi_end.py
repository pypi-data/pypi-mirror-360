from forgen.tool.tool import Tool
from forgen.tool.node import InputPhase, OperativePhase, OutputPhase
from forgen.pipeline.item import PipelineItem
from forgen.pipeline.builder import MultiPathPipelineBuilder
from forgen.registry.deserialize import deserialize_operand
from pprint import pprint

# Tool A: adds a prefix
def prefix_fn(data):
    name = data.get("name", "")
    return {"prefixed": f"Hello {name}"}

# Tool B: converts to uppercase
def upper_fn(data):
    text = data.get("prefixed", "")
    return {"shout": text.upper()}

# Tool C: adds an exclamation mark
def exclaim_fn(data):
    text = data.get("shout", "")
    return {"final": text + "!"}

# Tool D: lowercases the original name
def lower_fn(data):
    name = data.get("name", "")
    return {"soft": name.lower()}

# Create Tool A
tool_a = Tool(
    input_phase=InputPhase(input_schema={"name": str}, output_schema={"name": str}),
    operative_phase=OperativePhase(code=prefix_fn, input_schema={"name": str}, output_schema={"prefixed": str}),
    output_phase=OutputPhase(input_schema={"prefixed": str}, output_schema={"prefixed": str}),
    input_schema={"name": str},
    output_schema={"prefixed": str},
    name="PrefixTool"
)

# Create Tool B
tool_b = Tool(
    input_phase=InputPhase(input_schema={"prefixed": str}, output_schema={"prefixed": str}),
    operative_phase=OperativePhase(code=upper_fn, input_schema={"prefixed": str}, output_schema={"shout": str}),
    output_phase=OutputPhase(input_schema={"shout": str}, output_schema={"shout": str}),
    input_schema={"prefixed": str},
    output_schema={"shout": str},
    name="UpperTool"
)

# Create Tool C
tool_c = Tool(
    input_phase=InputPhase(input_schema={"shout": str}, output_schema={"shout": str}),
    operative_phase=OperativePhase(code=exclaim_fn, input_schema={"shout": str}, output_schema={"final": str}),
    output_phase=OutputPhase(input_schema={"final": str}, output_schema={"final": str}),
    input_schema={"shout": str},
    output_schema={"final": str},
    name="ExclaimTool"
)

# Create Tool D
tool_d = Tool(
    input_phase=InputPhase(input_schema={"name": str}, output_schema={"name": str}),
    operative_phase=OperativePhase(code=lower_fn, input_schema={"name": str}, output_schema={"soft": str}),
    output_phase=OutputPhase(input_schema={"soft": str}, output_schema={"soft": str}),
    input_schema={"name": str},
    output_schema={"soft": str},
    name="LowerTool"
)

# Wrap tools as PipelineItems
item_a = PipelineItem(module=tool_a, _id="tool_a")
item_b = PipelineItem(module=tool_b, _id="tool_b")
item_c = PipelineItem(module=tool_c, _id="tool_c")
item_d = PipelineItem(module=tool_d, _id="tool_d")

# Build the pipeline
builder = MultiPathPipelineBuilder()
builder.set_name("SplitOutputGreetingPipeline")
builder.set_description("Pipeline that greets, shouts, and whispers")
builder.add_item(item_a).add_item(item_b).add_item(item_c).add_item(item_d)

# Wiring dependencies
builder.add_engine_tuple("tool_a", "tool_b")
builder.add_engine_tuple("tool_b", "tool_c")
builder.add_engine_tuple("tool_a", "tool_d")

# Build and run
pipeline = builder.build()
input_data = {"name": "James"}

output = pipeline.execute(input_data)

print("🔹 Final Pipeline Output:")
pprint(output)

# ✅ Serialize
serialized = pipeline.serialize()
print("\n🔸 Serialized Pipeline:")
pprint(serialized)

# ✅ Deserialize
rehydrated = deserialize_operand(serialized)
rehydrated_output = rehydrated.execute(input_data)

print("\n🔁 Rehydrated Output:")
pprint(rehydrated_output)

# ✅ Check
assert output == rehydrated_output, "Mismatch after deserialization"
print("\n✅ Multi-terminal MultiPathPipeline test passed.")
