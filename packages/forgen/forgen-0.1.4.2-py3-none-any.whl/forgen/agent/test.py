from forgen.tool.builder import GenToolBuilder
from forgen.pipeline.item import PipelineItem
from forgen.agent.agent import GenerativeAgent
from pprint import pprint

# === Define Tools ===

compliment_tool = GenToolBuilder(
    name="ComplimentTool",
    input_schema={"name": str},
    output_schema={"compliment": str},
    system_prompt="You're a kind assistant. Return only a JSON with a compliment.",
    user_prompt_template="Give a kind compliment to {name}.",
    description="Gives a compliment"
).build()

rewrite_tool = GenToolBuilder(
    name="RewriteTool",
    input_schema={"compliment": str},
    output_schema={"nicer": str},
    system_prompt="You're a refinement bot. Return only a JSON with a refined compliment.",
    user_prompt_template="Please rewrite this to sound even more elegant: {compliment}",
    description="Refines compliments"
).build()

# === Wrap Tools in PipelineItems ===

item1 = PipelineItem(module=compliment_tool, _id="compliment")
item2 = PipelineItem(module=rewrite_tool, _id="rewrite")

# === Construct Agent ===

agent = GenerativeAgent(
    prompt="You are an agent that generates and refines compliments.",
    agent_name="ComplimentAgent",
    description="Refines a compliment to make it even nicer.",
    modules=[item1, item2],
    user_input_schema={"name": str},
    user_output_schema={"nicer": str},
    max_iterations=1  # only one pass through strategy
)

# === Execute ===

input_data = {"user_request": "Make a beautiful compliment, and then rewrite it in a texas style, and then add an alliterative compliment", "name": "Jamie"}
result = agent.execute(input_data)

print("\n✅ Final Output:")
pprint(result)

print("\n📊 Total Cost:")
pprint(agent.cost)

print("\n📊 Cost Breakdown:")
pprint(agent.cost_breakdown)

print("\n📊 Generation Metrics:")
pprint(agent.generation_metrics)

from forgen.util.general import summarize_token_usage
print("\n📈 Summary by Model:")
pprint(summarize_token_usage(agent.generation_metrics))
