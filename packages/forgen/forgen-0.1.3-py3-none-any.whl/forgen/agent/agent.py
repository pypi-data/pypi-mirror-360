import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable

from dotenv import load_dotenv

from forgen.agent.helper import openai_generation_function
from forgen.tool.gen.metrics import GenerationMetrics
from forgen.tool.module import BaseModule
from forgen.util.type import enforce_schema

load_dotenv()


@dataclass
class GenerativeAgent(BaseModule):

    def validate_schema(self):
        pass

    prompt: str  # Instructions on how the cognitive agent should behave
    agent_name: str # Friendly name for the agent
    agent_id: str = "" # Unique identifier for the agent
    description: str = "" # Description of what the agent does and is for
    modules: List[BaseModule] = field(default_factory=list)  # Modules available for use
    user_input_schema: Optional[Dict[str, type]] = None  # Set at runtime
    user_output_schema: Optional[Dict[str, type]] = None  # Set at runtime
    forced_interface: bool = True  # Allow type-based matching
    max_iterations: int = 3  # Maximum iterations before stopping
    max_tokens: int = None  # Maximum tokens before stopping
    generation_function: Optional[Callable[[str, Dict[str, Any], Any], Dict[str, Any]]] = None  # Strategy generator
    model: str = os.getenv("DEFAULT_MODEL_NAME")

    @property
    def id(self):
        return self.agent_id

    @id.setter
    def id(self, val):
        self.agent_id = val

    @property
    def thread(self):
        return None

    @property
    def name(self):
        return self.agent_name

    @name.setter
    def name(self, name):
        self.agent_name = name

    @property
    def input_schema(self):
        return self.user_input_schema

    @input_schema.setter
    def input_schema(self, input_schema):
        self.user_input_schema = input_schema

    @property
    def output_schema(self):
        return self.user_output_schema

    @output_schema.setter
    def output_schema(self, output_schema):
        self.user_output_schema = output_schema

    def __post_init__(self):
        self._step_metrics = {}

    @property
    def metrics(self):
        """Return metrics from last run."""
        return self._step_metrics

    @property
    def cost(self):
        """Total tokens consumed by all generative steps."""
        return sum(m.cost for m in self._step_metrics.values())

    @property
    def cost_breakdown(self):
        return {step: m.cost for step, m in self._step_metrics.items()}

    @property
    def generation_metrics(self):
        return self._step_metrics

    def reset_metrics(self):
        self._step_metrics = {}

    def set_forced_interface(self, forced_interface):
        self.forced_interface = forced_interface

    def initialize(self):
        """Ensure all modules respect the forced interface setting."""
        if self.forced_interface:
            for module in self.modules:
                module.set_forced_interface(self.forced_interface)

    def strategize(self, user_request: str, input_data: Dict[str, Any], current_data, execution_log) -> Dict[str, Any]:
        """
        Uses the cognitive agent's prompt and user request to generate:
        - Which modules to use
        - What inputs are required
        - The execution plan
        """
        if not self.generation_function:
            self.generation_function = openai_generation_function
        gen_input = {
            "prompt": self.prompt,
            "available_modules": [(module.name, module.description) for module in self.modules],
            "input_data": input_data,
            "execution_log": execution_log,
        }

        result = self.generation_function(user_request, gen_input, current_data)
        execution_plan, metrics = self.get_metrics_and_result(result)
        self._step_metrics["strategy"] = metrics
        return execution_plan

    def get_metrics_and_result(self, result):
        if not isinstance(result, dict):
            raise ValueError("Expected dict result from generative_function.")
        gen_output = result.get("output") or result.get("text") or result
        input_tokens = result.get("input_tokens") or result.get("input_tokens")
        output_tokens = result.get("output_tokens") or result.get("output_tokens")
        metrics = GenerationMetrics(
            model=self.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
        return gen_output, metrics

    def execute_fn(self, user_request: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the dynamically constructed pipeline iteratively until completion.

        Args:
            user_request (str): The request describing the desired automation.
            input_data (dict): The input data provided at runtime.
            self (the object)

        Returns:
            dict: The final output after executing the pipeline.
        """
        self.initialize()
        if not self.user_input_schema or not self.user_output_schema:
            raise ValueError("Input and output schemas must be provided at runtime.")
        current_data = enforce_schema(input_data, self.user_input_schema)
        if not self.generation_function:
            self.generation_function = openai_generation_function
        execution_log = []
        for iteration in range(1, self.max_iterations + 1):
            print(f"\n[EXECUTING] - Iteration {iteration}: Strategizing next steps...\n")
            execution_plan = self.strategize(user_request, input_data, current_data, execution_log)
            print(f"\n - Execution Plan for iteration {iteration}: [{execution_plan}]]\n")
            module_inputs = execution_plan.get("input", {})
            if not module_inputs and not execution_plan.get("steps"):
                print("No further steps needed. Returning final result.")
                break  # Stop iteration if no further steps are needed
            for step in execution_plan["steps"]:
                module_name = step.get("tool_name")
                step_input = step.get("input", {})
                if isinstance(current_data, dict):
                    for key, value in current_data.items():
                        step_input.setdefault(key, value)
                else:
                    step_input.setdefault("current_data", current_data)
                executor = next((t for t in self.modules if t.name == module_name or (hasattr(t, "module") and t.module.name == module_name)), None)
                if not executor:
                    raise ValueError(f"[ERROR] Module '{module_name}' not found in available modules.")
                print(f" - Executing: {module_name} with input: {step_input}")
                try:
                    current_data = executor.execute(step_input)
                    if hasattr(executor, "metrics") and getattr(executor, "metrics", None):
                        self._step_metrics[module_name] = executor.metrics
                    execution_log += execution_plan
                except Exception as e:
                    print(f"[ERROR] Execution failed for '{module_name}': {str(e)}")
                    return {"error": f"Execution failed at step: {module_name}"}
        final_output = enforce_schema(current_data, self.user_output_schema)
        print("\n[SUCCESS] Execution Complete. Returning final structured output.")
        return final_output

    def serialize(self):
        return {
            "type": "GenerativeAgent",
            "name": self.name,
            "id": self.id,
            "description": self.description,
            "agent_prompt": self.prompt,
            "modules": [m.serialize() for m in self.modules],
            "input_schema": self._convert_schema(self.input_schema),
            "output_schema": self._convert_schema(self.output_schema),
        }

    def execute(self, input_data: dict = None) -> dict[str, Any]:
        agent_input = {}
        if "user_request" in input_data:
            user_request = input_data["user_request"]
            if isinstance(input_data, dict):
                for key, value in input_data.items():
                    if "user_request" in key:
                        continue
                    agent_input.setdefault(key, value)
            agent_input = input_data
        else:
            user_request = self.description
            agent_input = input_data
        return self.execute_fn(user_request, agent_input)
