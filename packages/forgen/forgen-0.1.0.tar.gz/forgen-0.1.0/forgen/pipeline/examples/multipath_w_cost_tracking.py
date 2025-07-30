from forgen.tool.builder import GenToolBuilder
from forgen.tool.tool import Tool
from forgen.tool.node import InputPhase, OperativePhase, OutputPhase
from forgen.pipeline.item import PipelineItem
from forgen.pipeline.builder import MultiPathPipelineBuilder
from pprint import pprint


# 🔧 Step 1: Build Generative Compliment Tool
builder = GenToolBuilder(
    name="ComplimentTool",
    input_schema={"name": str},
    output_schema={"compliment": str},
    system_prompt="You are a kind assistant. Only return a JSON object that includes a compliment.",
    user_prompt_template="Give a kind compliment to {name}.",
    description="Gives a compliment"
)
compliment_tool = builder.build()

# 🧱 Step 2: Add follow-up emphasis tool
def emphasize_fn(data):
    return {"final": data["compliment"] + " 💯"}

emphasize_tool = Tool(
    input_phase=InputPhase(input_schema={"compliment": str}),
    operative_phase=OperativePhase(code=emphasize_fn, input_schema={"compliment": str}, output_schema={"final": str}),
    output_phase=OutputPhase(input_schema={"final": str}),
    input_schema={"compliment": str},
    output_schema={"final": str},
    name="EmphasizeTool"
)

# 🎯 Step 3: Wrap in PipelineItems
item1 = PipelineItem(module=compliment_tool, _id="compliment")
item2 = PipelineItem(module=emphasize_tool, _id="emphasize")

# 🔗 Step 4: Build and wire the pipeline
builder = MultiPathPipelineBuilder()
builder.set_name("ComplimentPipeline")
builder.set_description("Generates and emphasizes a compliment")
builder.add_item(item1).add_item(item2)
builder.add_engine_tuple("compliment", "emphasize")
pipeline = builder.build()

# 🚀 Step 5: Execute
input_data = {"name": "Jamie"}
output = pipeline.execute(input_data)
print("\n🔹 Final Output:")
pprint(output)

# 📊 Step 6: Cost tracking
print("\n📊 Total Cost:")
pprint(pipeline.cost)

# 📊 Step 6: Cost tracking
print("\n📊 Cost Breakdown:")
pprint(pipeline.cost_breakdown)

# 📊 Step 6: Cost tracking
print("\n📊 Generation Metrics:")
pprint(pipeline.generation_metrics)
