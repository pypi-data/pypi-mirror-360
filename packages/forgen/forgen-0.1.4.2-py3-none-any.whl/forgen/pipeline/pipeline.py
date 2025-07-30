from collections import defaultdict
from typing import Tuple, List

from forgen.tool.module import BaseModule
from forgen.util.type import safe_merge, list_to_dict


class BasePipeline(BaseModule):
    def __init__(self, name: str = None, _id: str = None, description: str = None, nodes: list = [],
                 input_schema: dict = None, output_schema: dict = None, forced_interface: bool = False, thread=None,
                 _output_data: dict = None, _input_data: dict = None, _version: str = "0.0.1"):
        self._version = _version
        self._name = name or "BasePipeline"
        self._id = _id
        self._description = description
        self.nodes = nodes
        self._input_schema = input_schema or {}
        self._output_schema = output_schema or {}
        self._forced_interface = forced_interface
        self._thread = thread
        self._output_data = _output_data or {}
        self._input_data = _input_data or {}
        self.node_outputs = {}
        for node in self.nodes:
            if not hasattr(node, 'input_data'):
                setattr(node, 'input_data', {})
            elif node.input_data is None:
                node.input_data = {}

    def __str__(self):
        return f"{self._name}: {self._description}"

    def __call__(self, input_data):
        return self.execute(input_data)

    @property
    def cost(self):
        return sum(getattr(node, "cost", 0) or 0 for node in self.nodes)

    @property
    def cost_breakdown(self):
        return {node.name: node.cost for node in self.nodes}

    @property
    def generation_metrics(self):
        return {
            node.name: getattr(node, "metrics", None)
            for node in self.nodes
            if getattr(node, "metrics", None)
        }

    def serialize(self) -> dict:
        spec = super().serialize()
        spec.update({
            "pipeline_nodes": [n.serialize() for n in self.nodes]
        })
        return spec

    def to_dict(self):
        return {
            "pipeline_name": self._name,
            "id": self._id,
            "description": self.description,
            "nodes": self.nodes,
            "input_schema": self._input_schema,
            "output_schema": self._output_schema,
            "forced_interface": self.forced_interface,
            "output_data": self.output_data,
        }

    def execute(self, input_data) -> dict:
        raise NotImplementedError("BasePipeline is Abstract. Please use SerialPipeline or MultiPathPipeline.")

    def validate_schema(self):
        raise NotImplementedError("BasePipeline is Abstract. Please use SerialPipeline or MultiPathPipeline.")

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, val):
        self._version = val

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    @property
    def id(self):
        """Abstract property for the input schema."""
        return self._id

    @id.setter
    def id(self, val):
        self._id = val

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, val):
        self._description = val

    @property
    def input_schema(self):
        return self._input_schema

    @input_schema.setter
    def input_schema(self, val):
        self._input_schema = val

    @property
    def output_schema(self):
        return self._output_schema

    @output_schema.setter
    def output_schema(self, val):
        self._output_schema = val

    @property
    def input_data(self):
        return self._input_data

    @input_data.setter
    def input_data(self, val):
        self._input_data = val

    @property
    def output_data(self):
        return self._output_data

    @output_data.setter
    def output_data(self, val):
        self._output_data = val

    @property
    def forced_interface(self):
        return self._forced_interface

    def set_forced_interface(self, forced_interface: bool):
        self._forced_interface = forced_interface
        for _node in self.nodes:
            _node.set_forced_interface(forced_interface)

    @property
    def thread(self):
        return self._thread


class SerialPipeline(BasePipeline):

    def __init__(self, name, nodes, _id=None, description=None, forced_interface=False):
        input_schema = nodes[0].input_schema if nodes else {}
        output_schema = nodes[-1].output_schema if nodes else {}
        super().__init__(
            name=name,
            _id=_id,
            description=description,
            nodes=nodes or [],
            input_schema=input_schema,
            output_schema=output_schema,
            forced_interface=forced_interface
        )
        self.validate_schema()
        if self.forced_interface:
            self.set_forced_interface(forced_interface)

    def __str__(self):
        return f"{self.name}: {self.description}"

    def __call__(self, input_data):
        return self.execute(input_data)

    def validate_schema(self):
        """
        Validate that the tool's nodes are compatible in terms of input/output schema.
        If `forced_interface` is enabled, allow matching by type instead of exact key.
        """
        ids = []
        for i in range(len(self.nodes) - 1):
            current_node = self.nodes[i]
            next_node = self.nodes[i + 1]
            if not current_node.id or current_node.id in ids:
                current_node_id = f"node_{i}"
                suffix = 1
                while current_node_id in ids:
                    current_node_id = f"node_{i}_{suffix}"
                    suffix += 1
                current_node.id = current_node_id
            ids.append(current_node.id)
            if not current_node.output_schema or not next_node.input_schema:
                continue
            for field, field_type in next_node.input_schema.items():
                if field in current_node.output_schema:
                    if not self.forced_interface and current_node.output_schema[field] != next_node.input_schema[field]:
                        raise ValueError(
                            f"Type mismatch for field '{field}' between Node {current_node.name} and Node {next_node.name}. "
                            f"Expected {next_node.input_schema[field]}, got {field_type}."
                        )
                    continue
                if self.forced_interface:
                    compatible_field = next(
                        (k for k, v in current_node.output_schema.items() if v == field_type), None
                    )
                    if not compatible_field:
                        raise ValueError(
                            f"Forced interface mode enabled, but no compatible field found for '{field}' "
                            f"from Node {current_node.name}[{current_node.output_schema}] to match Node {next_node.name}."
                        )
                else:
                    raise ValueError(
                        f"Field '{field}' in input schema of Node {next_node.name} is missing in output schema of Node {current_node.name}."
                    )

    def execute(self, input_data: dict = None) -> dict:
        """
        Executes all nodes sequentially, passing the output of one as input to the next.
        Returns a list of outputs for each step.
        """

        print(f"[PIPELINE {self.name}] [EXEC] --> __START__")
        output = input_data
        for idx, node in enumerate(self.nodes):
            try:
                print(f"[PIPELINE {self.name}] [NODE {node.name}] [EXEC] [INPUT: {str(input_data)[:66]} . . . ]")
                node.forced_interface = self.forced_interface
                output = node.execute(output)
                print(f"[PIPELINE {self.name}] [NODE {node.name}] [EXEC] [OUTPUT: {str(output)[:66]} . . . ]")
                self.node_outputs[node.id] = output
                self.output_data = output
            except Exception as e:
                raise RuntimeError(
                    f"Error executing Node {idx} ({node.name}) in SerialPipeline: {e}"
                ) from e
        print(f"[PIPELINE {self.name}] [EXEC] __END__ <-- ")
        return self.output_data


class MultiPathPipeline(BasePipeline):
    def __init__(self, pipeline_object):
        self.pipeline_object = pipeline_object
        self.dependencies = pipeline_object.get("dependencies", [])
        raw_items = pipeline_object.get("items", [])
        self.items = {item.id: item for item in raw_items}
        self._vals = {}  # <== Track all inputs and outputs here
        self.dependency_count = defaultdict(int)
        self.node_outputs = {}
        self._id = pipeline_object.get("pipeline_id", pipeline_object.get("id", None))
        input_schema, output_schema = self._infer_schemas()
        super().__init__(
            name=pipeline_object.get("name", "MultiPathPipeline"),
            _id=self._id,
            nodes=raw_items,
            description=pipeline_object.get("description", ""),
            input_schema=input_schema,
            output_schema=output_schema,
            forced_interface=pipeline_object.get("forced_interface", True)
        )
        self.validate_schema()

    def _infer_schemas(self) -> Tuple[dict, dict]:
        inputs, outputs = self.find_master_inputs_outputs()

        input_schema = {}
        for node_id in inputs:
            if node_id in self.items:
                input_schema.update(self.items[node_id].input_schema)

        output_schema = {}
        for node_id in outputs:
            if node_id in self.items:
                output_schema.update(self.items[node_id].output_schema)

        return input_schema, output_schema

    def execute(self, input_data: dict, dry_run: bool = False) -> dict:
        self.__print_plan__()
        print(f"[PIPELINE {self.name}] [EXEC] --> __START__")

        # Initialize value store
        self._vals = input_data.copy()

        # Identify starting & terminal nodes
        master_inputs, master_outputs = self.find_master_inputs_outputs()

        if dry_run:
            print("[DRY RUN] Execution Plan")
            print("  Master Inputs:", master_inputs)
            print("  Master Outputs:", master_outputs)
            print("  Dependencies:", self.dependencies)
            return {}

        for src, tgt in self.dependencies:
            self.dependency_count[tgt] += 1

        for node_id in master_inputs:
            self.execute_node(node_id, self._vals)

        # Collect final merged output
        output = {}
        for i, node_id in enumerate(master_outputs):
            data = self.node_outputs.get(node_id, {})
            output = safe_merge(output, data) if i > 0 else data
        self.output_data = output

        print(f"[PIPELINE {self.name}] [EXEC] __END__ <--")
        return self.output_data

    def execute_node(self, node_id, input_data):
        node = self.items.get(node_id)
        if not node:
            return
        try:
            print(f"[PIPELINE {self.name}] [NODE {node.name}] [EXEC] [INPUT: {str(input_data)[:66]} . . . ]")
            if node.input_data:
                input_data.update(node.input_data)
            inputs = self.validate_item_inputs(node_id, input_data)
            output = node.execute(inputs)
            print(f"[PIPELINE {self.name}] [NODE {node.name}] [EXEC] [OUTPUT: {str(output)[:66]} . . . ]")
            self.node_outputs[node_id] = output

            # Update value store
            self._vals.update(output)

            for _, target in filter(lambda t: t[0] == node_id, self.dependencies):
                self.dependency_count[target] -= 1
                if self.dependency_count[target] == 0:
                    deps = [self.node_outputs.get(dep, {}) for dep, tgt in self.dependencies if tgt == target]
                    merged = safe_merge(*deps) if len(deps) > 1 else deps[0] if deps else {}
                    if isinstance(merged, list):
                        merged = list_to_dict(merged)
                    self.execute_node(target, merged)
        except Exception as e:
            raise RuntimeError(f"Error executing Node '{node.name}' in MultiPathPipeline: {e}") from e

    def validate_item_inputs(self, item_id, available_outputs):
        item = self.items.get(item_id)
        if not item:
            raise ValueError(f"Pipeline Item '{item_id}' is not defined.")

        new_inputs = {}
        for input_key, expected_type in item.input_schema.items():
            value = available_outputs.get(input_key)

            # Fallback to _vals if value is missing
            if value is None and self._forced_interface:
                print(
                    f"[PIPELINE {self.name}] [NODE {item_id}] [FALLBACK] Trying _vals for '{input_key}' in '{item_id}'")
                value = self._vals.get(input_key)

            if value is None and not self.forced_interface:
                raise ValueError(f"Input '{input_key}' for Pipeline Item '{item_id}' is missing.")

            # Adapt if type mismatch and forced_interface is on
            if not isinstance(value, expected_type):
                if self._forced_interface:
                    print(
                        f"[PIPELINE {self.name}] [NODE {item_id}] [TYPE COERCE] Adapting '{input_key}' → {expected_type.__name__}")
                    try:
                        value = self._adapt_input(expected_type, value)
                    except Exception as e:
                        raise ValueError(
                            f"Could not adapt input '{input_key}' for '{item_id}': {e}"
                        )
                else:
                    raise ValueError(
                        f"Input '{input_key}' for '{item_id}' must be {expected_type}, got {type(value).__name__}."
                    )

            new_inputs[input_key] = value

        return new_inputs

    @staticmethod
    def _adapt_input(expected_type, val):
        if expected_type is str:
            return f"OUTPUT: {str(val)}"
        if expected_type is list:
            return list(val.values()) if isinstance(val, dict) else list(val) if not isinstance(val, list) else val
        if expected_type is dict:
            return val if isinstance(val, dict) else {i: v for i, v in enumerate(val)}
        if expected_type is int:
            return int(val[0] if isinstance(val, list) else val)
        if expected_type is float:
            return float(val[0] if isinstance(val, list) else val)
        if expected_type is bool:
            if isinstance(val, str):
                return val.lower() in {"true", "yes", "1"}
            return bool(val)
        raise ValueError(f"Cannot convert {type(val)} to {expected_type.__name__}")

    def find_master_inputs_outputs(self) -> Tuple[List[str], List[str]]:
        sources = set()
        targets = set()
        for src, tgt in self.dependencies:
            sources.add(src)
            targets.add(tgt)

        all_nodes = set(self.items.keys())

        root_nodes = sorted([node for node in all_nodes if node not in targets])
        leaf_nodes = sorted([node for node in all_nodes if node not in sources])

        return root_nodes, leaf_nodes

    def validate_schema(self):
        visited = set()
        stack = set()

        def dfs(node):
            if node in stack:
                raise ValueError(f"Circular dependency involving '{node}'.")
            if node not in visited:
                stack.add(node)
                for _, target in [t for t in self.dependencies if t[0] == node]:
                    dfs(target)
                stack.remove(node)
                visited.add(node)

        all_items = set(self.items.keys())
        connected = {a for a, _ in self.dependencies} | {b for _, b in self.dependencies}
        disconnected = all_items - connected
        if disconnected:
            raise ValueError(f"Disconnected Agent Items: {disconnected}")

    def __print_plan__(self):
        from collections import defaultdict

        adjacency = defaultdict(list)
        for src, tgt in self.dependencies:
            adjacency[src].append(tgt)

        visited = set()

        def dfs(node_id, prefix=""):
            if node_id in visited:
                return  # Avoid cycles
            visited.add(node_id)
            children = adjacency.get(node_id, [])
            if not children:
                print(f"{prefix}{node_id}")
                return

            print(f"{prefix}{node_id}")
            for i, child in enumerate(children):
                is_last = i == len(children) - 1
                connector = "└──►" if is_last else "├──►"
                child_prefix = prefix + ("   " if is_last else "│  ")
                print(f"{prefix}{connector} {child}")
                dfs(child, prefix + ("   " if is_last else "│  "))

        # Try to find entry nodes
        roots, _ = self.find_master_inputs_outputs()
        print("\n[PIPELINE STRUCTURE DIAGRAM]")
        for root in roots:
            dfs(root)
        print()  # Blank line for spacing
