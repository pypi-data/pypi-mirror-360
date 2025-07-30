from typing import Literal, Any

EnvironmentActionType = Literal["discrete", "continuous"]
EnvironmentStandardType = Literal[
    "gymnasium", "gym-v26", "gym-v21", "pettingzoo", "pufferlib"
]

ModelType = Any
ModelLibraryType = Literal["pytorch", "tensorflow", "keras", "stable_baselines3", "onnx"]
