from forgen.tool.builder import ToolBuilder
from forgen.tool.module import BaseModule


# Tool: Process a list by calling an agent on each element
def batch_process(input_data):
    """
    Takes a list of inputs and applies a given agent to each element.
    :param input_data: Dictionary with keys {"items": list, "agent": callable}
    :return: List of results
    """
    items = input_data.get("items", [])
    agent = input_data.get("agent", None)
    if not agent:
        raise Exception(f"No agent found. Please set 'agent' field of input: {str(input_data)}")

    # if not callable(agent):
    #     raise ValueError("Provided agent is not callable.")

    return [agent.execute(item) for item in items]


# Create a tool that applies an agent to a list input
batch_processor_tool_builder = ToolBuilder(
    name="BatchProcessor",
    tool_fn=batch_process,
    input_schema={"items": list, "agent": BaseModule},
    output_schema={"output": list},
    forced_interface=True,
    description="For using other tools or agents in batch: " + """
    def batch_process(input_data):
        #Takes a list of inputs and applies a given agent to each element.
        :param input_data: Dictionary with keys {"items": list, "agent": callable}
        :return: List of results
    
        items = input_data.get("items", [])
        agent = input_data.get("tool_name", None)
        if not agent:
            raise Exception(f"No agent found. Please set 'agent' field of input: {str(input_data)}")
        return [agent.execute({"input": item}) for item in items]
    """
)


# Tool to batch-process items.
#: input_schema={"items": list, "agent": BaseModule}, output_schema={"output": list}
batch_processor_tool = batch_processor_tool_builder.build()
batch_processor_tool.__doc__ = """
       Batch Tool
    
        Description:
            {self.description or 'No description provided.'}
    
        Input ➝ Output:
            {list(self.input_schema.keys())} ➝ {list(self.output_schema.keys())}
    
        Full Input Schema:
            {self.input_schema}
    
        Full Output Schema:
            {self.output_schema}
    """