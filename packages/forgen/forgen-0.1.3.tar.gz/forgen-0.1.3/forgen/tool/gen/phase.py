import os
from dotenv import load_dotenv

from forgen.tool.gen.metrics import GenerationMetrics
from forgen.tool.node import OperativePhase


load_dotenv()


class GenerativePhase(OperativePhase):

    def __init__(self, generative_function, max_tries=3, start_tokens=None, end_tokens=None, input_data=None, input_schema=None, output_schema=None, forced_interface=False, _model: str = os.getenv("DEFAULT_MODEL_NAME")):
        """
        Handles the AI generation phase.
        :param generative_function: A callable function that takes input_data and returns generated output.
        :param max_tries: Number of attempts for generation before failing."""
        self.name = "GenerativePhase"
        super().__init__(input_data, input_schema, output_schema, generative_function, forced_interface)
        if not callable(generative_function):
            raise TypeError("generative_function must be a callable function.")
        self.generation_function = generative_function
        self.max_tries = max_tries
        self.cost = None if not (start_tokens and end_tokens) else end_tokens - start_tokens
        self.start_tokens = start_tokens
        self.end_tokens = end_tokens
        self.metrics: GenerationMetrics = None
        self.model = _model

    def execute(self, input_data: dict = None, output_key="output") -> dict:
        """Try multiple times to get a valid output with token tracking."""
        num_tries = 0
        while num_tries < self.max_tries:
            num_tries += 1
            try:
                result = super().execute(input_data, output_key=output_key)

                if not isinstance(result, dict):
                    raise ValueError("Expected dict result from generative_function.")

                # Normalize output extraction
                generated_output = result.get("output") or result.get("text") or result
                input_tokens = result.get("input_tokens", 0)
                output_tokens = result.get("output_tokens", 0)

                self.metrics = GenerationMetrics(
                    model=self.model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens
                )

                self.cost = self.metrics.cost

                return generated_output

            except Exception as e:
                print(f"❌ Generation failed (attempt {num_tries}/{self.max_tries}): {str(e)}")
                if num_tries >= self.max_tries:
                    raise ValueError("Max generation attempts reached.")
        return {}
