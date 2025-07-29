from dataclasses import dataclass, field


@dataclass
class InputOutput:
    name: str
    datatype: str
    shape: list[int]


@dataclass
class ModelConfig:
    name: str
    versions: list[str]
    platform: str
    ready: bool
    inputs: list[InputOutput] = field(default_factory=list)
    outputs: list[InputOutput] = field(default_factory=list)
