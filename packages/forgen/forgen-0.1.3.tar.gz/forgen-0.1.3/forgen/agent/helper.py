from typing import Dict, Any

from forgen.llm.openai_interface.interface import get_chat_completions_response


def openai_generation_function(user_request, input_data: Dict[str, Any], current_data, execution_log=None):
    """
    Calls OpenAI to generate a structured execution plan.
    """
    # Extract available modules
    available_modules = input_data.get("available_modules", [])

    # Print all available tools and agents for debugging
    print("\n🔹 Available Tools:")
    for module in available_modules:
        print(f"  - {module}")

    # Construct system content including available tools & agents
    system_content = (
        "You are a helpful assistant that determines which steps to be used to obtain the appropriate info"
        "in order to suitably and completely answer the user's REQUEST, and through specifying an array call "
        "'steps' where each element is indicates which tools and agents should be used to complete this task.\n"
        "IF THE TASK IS DEFINITELY COMPLETE BASED ON THE CURRENT_DATA BELOW, THEN RETURN AN EMPTY ARRAY."
        "WHEN DECIDING WHETHER THE TASK IS ALREADY COMPLETE, CONSIDER IT COMPLETE IF THE STRATEGY IN EXECUTION LOG MATCHES PROPOSED STRATEGY."
        "THE OUTPUT FROM THE PREVIOUS STEP IS INPUT INTO THE PRESENT STEP SO LEAVE ENTIRELY BLANK UNLESS NEED TO "
        "ALSO ADD STATIC INPUTS."
        "Here are the available tools:\n"
        + "\n".join(f"- {module}" for module in available_modules) +
        "\n\nRETURN A JSON REQUESTING A TOOL AND ITS INPUT BASED ON THE FOLLOWING WHERE YOUR"
        "JSON RESPONSE IS THE VAR 'execution_plan': " + """
            for step in execution_plan["steps"]:
                tool_name = step.get("tool_name")
                step_input = step.get("input", {})
                if isinstance(current_data, dict):
                    for key, value in current_data.items():
                        step_input.setdefault(key, value)
                else:
                    step_input.setdefault("current_data", current_data)
                # Find the matching tool
                executor = next((t for t in self.tools if t.name == tool_name), None)
                if not executor:
                    raise ValueError(f"Tool/Agent '{tool_name}' not found in available resources.")
                print(f"Executing: {tool_name} with input: {step_input}")
                try:
                    # Execute the tool or agent
                    current_data = executor.execute(step_input)
                except Exception as e:
                    print(f"Execution failed for '{tool_or_agent_name}': {str(e)}")
                    return {"error": f"Execution failed at step: {tool_name}"}

        THE JSON RETURNED MUST HAVE AT LEAST THE FOLLOWING ATTRIBUTES:
            - 'steps': an array of one or more STEP where each STEP has 
                - 'tool_name' specifying the exact name of the tool or agent from the list(s) above
                - 'input' specifying static input (suited properly for the tool), but THIS ATTR SHOULD BE EXCLUDED UNLESS STATIC INPUT NEEDED.
        """

    )
    user_content ="REQUEST: " + user_request + "\n\nINPUT: " + str(input_data) + "\n\nCURRENT_DATA: " + str(current_data)
    if execution_log:
        user_content += "\n\nEXECUTION_LOG: " + str(execution_log)
    return get_chat_completions_response(
        system_content=system_content,
        user_content=user_content,
        load_json=True
    )
