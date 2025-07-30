from forgen.tool.tool import Tool
from forgen.tool.node import InputPhase, OperativePhase, OutputPhase
from forgen.agent.agent import GenerativeAgent
from forgen.registry.deserialize import deserialize_operand
from pprint import pprint

# Mock generation strategy (normally this would be LLM-backed)
def mock_generation_function(user_request, gen_input, current_data):
    if "compliment" in user_request.lower():
        return {
            "steps": [
                {"tool_name": "ComplimentTool", "input": {"name": gen_input["input_data"].get("name")}},
                {"tool_name": "ExclaimTool", "input": {}}
            ]
        }
    return {"steps": []}

# Tool 1: create compliment

def compliment_fn(data):
    name = data.get("name", "you")
    return {"text": f"{name}, you're doing amazing!"}

compliment_tool = Tool(
    input_phase=InputPhase(input_schema={"name": str}),
    operative_phase=OperativePhase(code=compliment_fn, input_schema={"name": str}, output_schema={"text": str}),
    output_phase=OutputPhase(input_schema={"text": str}),
    name="ComplimentTool"
)

# Tool 2: add exclamation

def exclaim_tool_fn(data):
    return {"final": data.get("text", "") + " 🤩"}

exclaim_tool = Tool(
    input_phase=InputPhase(input_schema={"text": str}),
    operative_phase=OperativePhase(code=exclaim_tool_fn, input_schema={"text": str}, output_schema={"final": str}),
    output_phase=OutputPhase(input_schema={"final": str}),
    name="ExclaimTool"
)


# Build the GenerativeAgent
agent = GenerativeAgent(
    agent_name="Encourager",
    agent_id="encourager-001",
    description="Give people compliments in an exciting way",
    prompt="Generate praise using available modules",
    modules=[compliment_tool, exclaim_tool],
    user_input_schema={"name": str},
    user_output_schema={"final": str}
)

# Execute the agent
input_data = {"user_request": "Compliment someone!", "name": "Jamie"}
output = agent.execute(input_data)

print("\n🔹 Agent Output:")
pprint(output)

# Serialize and Deserialize
serialized = agent.serialize()
rehydrated = deserialize_operand(serialized)


rehydrated_output = rehydrated.execute(input_data)

print("\n🔁 Rehydrated Output:")
pprint(rehydrated_output)
print("\n✅ Agent serialization/deserialization test passed.")

