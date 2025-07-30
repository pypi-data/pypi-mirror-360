from pprint import pprint

from forgen.tool.builder import GenToolBuilder
from forgen.tool.tool import Tool
from forgen.tool.node import InputPhase, OperativePhase, OutputPhase
from forgen.pipeline.item import PipelineItem
from forgen.pipeline.builder import MultiPathPipelineBuilder
from forgen.util.general import summarize_token_usage


# 🔧 Step 1: Compliment Tool (Generative)
compliment_builder = GenToolBuilder(
    name="ComplimentTool",
    input_schema={"name": str},
    output_schema={"compliment": str},
    system_prompt="You are a kind assistant. Only return a JSON object that includes a compliment.",
    user_prompt_template="Give a kind compliment to {name}.",
    description="Gives a compliment"
)
compliment_tool = compliment_builder.build()

# 🔧 Step 2: Rewrite Tool (Another Generative Tool)
rewrite_builder = GenToolBuilder(
    name="RewriteTool",
    input_schema={"compliment": str},
    output_schema={"improved": str},
    system_prompt="You are a poetic assistant. Improve the compliment with more creativity.",
    user_prompt_template="Rewrite this compliment more beautifully by returning a JSON that includes a single attr named 'improved': {compliment}",
    description="Improves the compliment"
)
rewrite_tool = rewrite_builder.build()

# 🔧 Step 3: Emphasize Tool (Standard non-generative)
def emphasize_fn(data):
    return {"final": data["improved"] + " 💯"}

emphasize_tool = Tool(
    input_phase=InputPhase(input_schema={"improved": str}),
    operative_phase=OperativePhase(code=emphasize_fn, input_schema={"improved": str}, output_schema={"final": str}),
    output_phase=OutputPhase(input_schema={"final": str}),
    input_schema={"improved": str},
    output_schema={"final": str},
    name="EmphasizeTool"
)

# 🧱 Wrap Tools into PipelineItems
item1 = PipelineItem(module=compliment_tool, _id="compliment")
item2 = PipelineItem(module=rewrite_tool, _id="rewrite")
item3 = PipelineItem(module=emphasize_tool, _id="emphasize")

# 🔗 Assemble MultiPath Pipeline
builder = MultiPathPipelineBuilder()
builder.set_name("GenerativeComplimentPipeline")
builder.set_description("Two generative steps and one non-generative follow-up.")
builder.add_item(item1).add_item(item2).add_item(item3)
builder.add_engine_tuple("compliment", "rewrite")
builder.add_engine_tuple("rewrite", "emphasize")
pipeline = builder.build()

# 🚀 Run Pipeline
input_data = {"name": "Jamie"}
output = pipeline.execute(input_data)

# 📤 Final Output
print("\n🔹 Final Output:")
pprint(output)

# 📊 Total Token Cost
print("\n📊 Total Cost:")
pprint(pipeline.cost)

# 📊 Cost Breakdown by Tool
print("\n📊 Cost Breakdown:")
pprint(pipeline.cost_breakdown)

# 📊 Detailed Generation Metrics
print("\n📊 Generation Metrics:")
pprint(pipeline.generation_metrics)

print("\n📈 Summary by Model:")
pprint(summarize_token_usage(pipeline.generation_metrics))
