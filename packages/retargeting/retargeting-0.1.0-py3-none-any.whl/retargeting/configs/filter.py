from dataclasses import dataclass


@dataclass
class OneEuroFilterConfig:
    min_cutoff: float = 0.1
    beta: float = 0.5


@dataclass
class OrientationFilterConfig:
    alpha: float = 0.1
