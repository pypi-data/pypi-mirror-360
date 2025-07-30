from forgen.ddb.tooling import add_tool_to_tool_registry_in_ddb

def store_pipeline_operand_to_registry(operand, username="system"):
    """
    Store a fully serialized Tool/Agent/Pipeline object into ToolRegistry.
    This supports deep structures (e.g., nested modules) and full reconstruction.
    """
    full_spec = operand.serialize()
    tool_id = f"{full_spec['name']}:{full_spec.get('version', '1.0')}"

    # Normalize for DDB schema
    full_spec['name'] = full_spec.pop('name')

    add_tool_to_tool_registry_in_ddb(
        username=username,
        tool_id=tool_id,
        **full_spec
    )

    print(f"✅ Stored full operand: {tool_id}")
