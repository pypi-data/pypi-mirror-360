from dataclasses import dataclass, asdict

@dataclass
class GenerationMetrics:
    model: str
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def cost(self) -> int:
        return self.input_tokens + self.output_tokens if self.input_tokens + self.output_tokens else 0

    def to_dict(self):
        return asdict(self)

    def __repr__(self):
        return f"{self.model} — Tokens: {self.cost} (In: {self.input_tokens}, Out: {self.output_tokens})"
