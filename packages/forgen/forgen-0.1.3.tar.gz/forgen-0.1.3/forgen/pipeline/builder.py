from forgen.tool.gen.tool import GenerativeTool
from forgen.tool.gen.phase import GenerativePhase
from forgen.tool.node import OutputPhase, InputPhase, OperativePhase
from forgen.pipeline.item import PipelineItem
from forgen.tool.module import BaseModule
from forgen.pipeline.pipeline import SerialPipeline, MultiPathPipeline
from forgen.tool.tool import Tool


class SerialPipelineBuilder:
    def __init__(self, tool_name: str, ai_client=None):
        """
        Initialize the PipelineBuilder.
        :param tool_name: Name of the pipeline.
        :param ai_client: Optional LLM client instance for the generation phase.
        """
        self.tool_name = tool_name
        self.tool_nodes = []
        self.global_input_schema = None
        self.global_output_schema = None
        self.description = None
        self.ai_client = ai_client
        self.forced_interface = False

    def set_input_schema(self, input_schema: dict):
        """
        Set the input schema for the entire pipeline.
        :param input_schema: Schema defining the pipeline's overall input structure.
        """
        self.global_input_schema = input_schema

    def set_global_output_schema(self, output_schema: dict):
        """
        Set the output schema for the entire pipeline.
        :param output_schema: Schema defining the pipeline's overall output structure.
        """
        self.global_output_schema = output_schema

    def add_node(self, node: BaseModule):
        self.tool_nodes.append(node)

    def create_and_add_node(self,
                                operative_fn: callable,
                                code_input: callable = None,
                                code_output: callable = None,
                                input_data: dict = None,
                                operative_input_schema: dict = None,
                                operative_output_schema: dict = None,
                                max_tries: int = 1,
                                wrap_operative_phase: bool = True,
                                is_generative_node: bool = True):
        """
        Add an GenerativeNode to the pipeline.
        :param operative_fn: The callable function for the GenerativePhase.
        :param code_input: The preprocessing callable for the InputPhase.
        :param code_output: The postprocessing callable for the OutputPhase.
        :param input_data: Initial data for the InputPhase.
        :param operative_input_schema: Schema for GenerativePhase input.
        :param operative_output_schema: Schema for GenerativePhase output.
        :param max_tries: Max tries for generation during GenerativePhase.
        :param wrap_operative_phase: Boolean of whether to wrap GenerativePhase in max-retry-like wrapper.
        :param is_generative_node: Boolean of whether to make a GenerativeTool (true) or not (false).
        """
        if not self.global_input_schema or not self.global_output_schema:
            raise ValueError("Global input and output schemas must be set before adding nodes.")

        # Determine InputPhase schema
        if not self.tool_nodes:  # First node
            input_phase_schema = self.global_input_schema
            initial_input_data = input_data or {}
        else:  # Intermediate nodes
            input_phase_schema = self.tool_nodes[-1].output_schema
            initial_input_data = {}

        # Determine OutputPhase schema
        output_phase_output_schema = operative_output_schema or self.global_output_schema

#       Set default GenerativePhase schemas if not provided
        _operative_input_schema = operative_input_schema or self.global_input_schema
        _operative_output_schema = operative_output_schema or self.global_output_schema

        # InputPhase
        input_phase = InputPhase(
            input_data=initial_input_data,
            input_schema=input_phase_schema,
            output_schema=_operative_input_schema,
            code=code_input or (lambda x: x)  # Default identity function
        )

        _operative_fn = operative_fn
        _operative_phase = None
        if is_generative_node:
            _Tool = GenerativeTool
            if wrap_operative_phase:
                def wrapped_generative_function(input_data):
                    """
                    Wrap the generation function to include the client if needed.
                    """
                    if self.ai_client:
                        return operative_fn(input_data, ai_client=self.ai_client)
                    return operative_fn(input_data)
                _operative_fn = wrapped_generative_function
            _operative_phase = GenerativePhase(
                generative_function=_operative_fn,
                input_data={},
                input_schema=_operative_input_schema,
                output_schema=_operative_output_schema
            )
            if max_tries:
                _operative_phase.max_tries = max_tries
        else:
            _Tool = Tool
            _operative_phase = OperativePhase(
                code=_operative_fn,
                input_data={},
                input_schema=_operative_input_schema,
                output_schema=_operative_output_schema
            )

        # OutputPhase
        output_phase = OutputPhase(
            input_data={},
            input_schema=operative_output_schema,
            output_schema=output_phase_output_schema,
            code=code_output or (lambda x: x)
        )

        # Create and add the GenerativeNode
        tool_node = _Tool(
            input_phase=input_phase,
            operative_phase=_operative_phase,
            output_phase=output_phase,
            input_schema=input_phase_schema,
            output_schema=operative_output_schema
        ) if not is_generative_node else _Tool(
            input_phase=input_phase,
            generative_phase=_operative_phase,
            output_phase=output_phase,
            input_schema=input_phase_schema,
            output_schema=operative_output_schema
        )
        self.tool_nodes.append(tool_node)

    def build(self, forced_interface: bool = False):
        """
        Build and return the Pipeline.
        :param forced_interface: Optional boolean parameter (defaultL False) for setting forced interface for pipeline.
        :return: An instance of SerialPipeline.
        """
        if not self.tool_nodes:
            raise ValueError("No nodes have been added to the pipeline.")

        if self.tool_nodes:
            last_node = self.tool_nodes[-1]
            last_node.output_phase.output_schema = self.global_output_schema
            last_node.output_schema = self.global_output_schema

        prev_tool_output_schema = self.global_input_schema
        for i in range(len(self.tool_nodes) - 1):
            node = self.tool_nodes[i]
            next_node = self.tool_nodes[i + 1]
            if node.input_schema is None:
                node.input_schema = prev_tool_output_schema
                node.input_phase.input_schema = prev_tool_output_schema
            node.input_phase.output_schema = node.operative_phase.input_schema
            node.output_phase.input_schema = node.operative_phase.output_schema
            node.connect(next_node)
            if node.output_schema is None:
                node.output_schema = node.output_phase.output_schema
            prev_tool_output_schema = node.output_schema
        return SerialPipeline(name=self.tool_name, nodes=self.tool_nodes, description=self.description, forced_interface=self.forced_interface)

    def set_description(self, description: str):
        self.description = description

    def set_forced_interface(self, param):
        self.forced_interface = param
        for _node in self.tool_nodes:
            _node.set_forced_interface(param)


class MultiPathPipelineBuilder:
    def __init__(self):
        """
        Initialize an empty pipeline object builder.
        """
        self._engine_tuples = []  # List of tuples (source, target)
        self._items = []          # List of pipeline items (each a dict)
        self._description = None
        self._forced_interface = True
        self._name = "MultiPathPipeline"

    def set_name(self, name: str):
        self._name = name
        return self

    def set_description(self, description: str):
        self._description = description
        return self

    def set_forced_interface(self, val: bool):
        self._forced_interface = val
        return self

    def add_item(self, item: PipelineItem):
        """
        Add a pipeline item to the pipeline object.

        :param item: the PipelineItem to add.
        :return: self (for method chaining)
        """
        if any(existing.id == item.id for existing in self._items):
            raise ValueError(f"Item ID '{item.id}' already exists.")
        self._items.append(item)
        return self

    def add_engine_tuple(self, source: str, target: str):
        """
        Add an engine tuple that defines a processing link between two items.

        :param source: The source identifier (or "master_input").
        :param target: The target identifier (or "master_output").
        :return: self (for method chaining)
        """
        self._engine_tuples.append((source, target))
        return self

    def build(self) -> MultiPathPipeline:
        """
        Build and return the pipeline object.

        :return: A dict representing the pipeline object with keys:
            - "dependencies": list of (source, target) tuples.
            - "items": list of pipeline items.
            - "master_input": dict with initial inputs.
        :raises ValueError: If required elements are missing.
        """
        if not self._items:
            raise ValueError("Must add at least one node.")

        if len(self._items) > 1 and not self._engine_tuples:
            raise ValueError("Missing engine tuples for multi-node pipeline.")

        item_map = {item.id: item for item in self._items}

        # Perform graph wiring
        for src_id, tgt_id in self._engine_tuples:
            src = item_map.get(src_id)
            tgt = item_map.get(tgt_id)
            if not src or not tgt:
                raise ValueError(f"Invalid connection: '{src_id}' → '{tgt_id}'")
            src.connect(tgt)

        pipeline_data = {
            "name": self._name,
            "description": self._description,
            "dependencies": self._engine_tuples,
            "items": self._items,
            "forced_interface": self._forced_interface,
        }

        return MultiPathPipeline(pipeline_data)


# --- Example Usage of the MultiPathPipelineBuilder ---

if __name__ == "__main__":
    # Create a builder instance.
    builder = MultiPathPipelineBuilder()

    # Define engine tuples that connect the master input, items, and master output.
    builder.add_engine_tuple("master_input", "item1")
    builder.add_engine_tuple("item1", "master_output")

    # Build the pipeline object.
    pipeline_object = builder.build()

    # Print the resulting pipeline object.
    print("Constructed pipeline Object:")
    from pprint import pprint
    pprint(pipeline_object)
