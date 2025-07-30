import types
import textwrap
from forgen.tool.builder import ToolBuilder
from forgen.pipeline.pipeline import SerialPipeline, MultiPathPipeline
from forgen.agent.agent import GenerativeAgent
from forgen.tool.tool import Tool
from forgen.tool.gen.tool import GenerativeTool
from forgen.pipeline.item import PipelineItem


TYPE_MAP = {
    "Tool": Tool,
    "GenerativeTool": GenerativeTool,
    "SerialPipeline": SerialPipeline,
    "MultiPathPipeline": MultiPathPipeline,
    "GenerativeAgent": GenerativeAgent,
    "PipelineItem": PipelineItem,
}


def _resolve_type(type_name: str):
    if type_name in TYPE_MAP:
        return TYPE_MAP[type_name]
    raise ValueError(f"Unsupported operand type: {type_name}")

def _restore_schema(schema: dict) -> dict:
    py_types = {"str": str, "int": int, "float": float, "bool": bool, "list": list, "dict": dict}
    return {k: py_types.get(v, str) for k, v in schema.items()}

def _rebuild_function(code_str: str):
    """
    Rebuild a Python function from source code string.
    """
    local_scope = {}
    exec(textwrap.dedent(code_str), {}, local_scope)
    fn = next((v for v in local_scope.values() if isinstance(v, types.FunctionType)), None)
    return fn

def deserialize_operand(spec: dict):
    """
    Rebuild a BaseModule (Tool, Agent, Pipeline, or PipelineItem) from a serialized .serialize() dict.
    Supports full restoration of phase code for Tool/GenerativeTool.
    """
    operand_type = spec.get("type")
    cls = _resolve_type(operand_type)

    if operand_type in ["Tool", "GenerativeTool"]:
        builder = ToolBuilder(name=spec["name"], description=spec.get("description", ""))
        builder.set_schema(
            _restore_schema(spec["input_schema"]),
            _restore_schema(spec["output_schema"])
        )

        # Handle prompt-based generative tools
        if spec.get("use_standard_gen_framework"):
            builder.use_standard_gen_framework = True
            builder.system_prompt = spec.get("system_prompt")
            builder.user_prompt_template = spec.get("user_prompt_template")

        # Restore each phase's function (if present and not a std prompt tool)
        if not spec.get("use_standard_gen_framework"):
            if "input_phase" in spec:
                input_code = spec["input_phase"].get("code")
                if input_code:
                    builder.set_code_input(_rebuild_function(input_code))

            if "operative_phase" in spec:
                operative_code = spec["operative_phase"].get("code")
                if operative_code:
                    builder.set_operative_function(_rebuild_function(operative_code))

            if "output_phase" in spec:
                output_code = spec["output_phase"].get("code")
                if output_code:
                    builder.set_code_output(_rebuild_function(output_code))

        return builder.build()

    elif operand_type == "PipelineItem":
        return PipelineItem(
            _id=spec["id"],
            module=deserialize_operand(spec["module"]),
            cust_input_schema=_restore_schema(spec.get("input_schema", {})),
            cust_output_schema=_restore_schema(spec.get("output_schema", {}))
        )

    elif operand_type == "SerialPipeline":
        nodes = [deserialize_operand(n) for n in spec.get("pipeline_nodes", [])]
        return SerialPipeline(name=spec.get("tool_name") or spec.get("name"), nodes=nodes)

    elif operand_type == "MultiPathPipeline":
        raw_items = {
            k: PipelineItem(
                _id=k,
                module=deserialize_operand(v),
                cust_input_schema=_restore_schema(v.get("input_schema", {})),
                cust_output_schema=_restore_schema(v.get("output_schema", {}))
            )
            for k, v in spec.get("items", {}).items()
        }
        return MultiPathPipeline({
            "name": spec.get("tool_name") or spec.get("name"),
            "id": spec.get("id", None),
            "description": spec.get("description", ""),
            "items": list(raw_items.values()),
            "dependencies": spec.get("dependencies", [])
        })

    elif operand_type == "GenerativeAgent":
        modules = [deserialize_operand(m) for m in spec.get("modules", [])]
        return GenerativeAgent(
            agent_name=spec["name"],
            agent_id=spec["id"],
            description=spec.get("description", ""),
            prompt=spec.get("agent_prompt", ""),
            modules=modules,
            user_input_schema=_restore_schema(spec["input_schema"]),
            user_output_schema=_restore_schema(spec["output_schema"]),
        )

    raise ValueError(f"Unsupported operand type: {operand_type}")
