from typing import Optional, TypedDict, Literal
import numpy as np


class MatchResults(TypedDict):
    score: float
    duration: float
    videoKey: Optional[str]


class BenchmarkResults(TypedDict):
    status: Literal["success", "error", "timeout"]
    score: Optional[np.float64]
    duration: float
    matches: list[MatchResults]
    logs: Optional[str]
    error: Optional[str]
