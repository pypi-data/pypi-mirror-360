from __future__ import annotations

from dataclasses import asdict, dataclass, field

from retargeting.configs.common import HAND_JOINT_GROUPS
from retargeting.configs.filter import OneEuroFilterConfig
from retargeting.typing import HandType


@dataclass
class DexRetargetingConfig:
    urdf_path: str
    prefix: str
    wrist_link_name: str = "hand_base_link"
    finger_tip_link_names: list[str] = field(
        default_factory=lambda: [
            "thumb_tip_link",
            "index_tip_link",
            "middle_tip_link",
            "ring_tip_link",
            "pinky_tip_link",
        ]
    )
    target_joint_names: list[str] = field(
        default_factory=lambda: [
            "pinky_proximal_joint",
            "ring_proximal_joint",
            "middle_proximal_joint",
            "index_proximal_joint",
            "thumb_proximal_pitch_joint",
            "thumb_proximal_yaw_joint",
        ]
    )
    type: str = "DexPilot"
    scaling_factor: float = 1.12
    low_pass_alpha: float = 0.5

    def __post_init__(self):
        if not self.wrist_link_name.startswith(self.prefix):
            self.wrist_link_name = self.prefix + self.wrist_link_name
        if not all(name.startswith(self.prefix) for name in self.finger_tip_link_names):
            self.finger_tip_link_names = [self.prefix + name for name in self.finger_tip_link_names]
        if not all(name.startswith(self.prefix) for name in self.target_joint_names):
            self.target_joint_names = [self.prefix + name for name in self.target_joint_names]

    def to_dict(self):
        d = asdict(self)
        del d["prefix"]  # remove prefix from dict
        return d

    @classmethod
    def from_dict(cls, config: dict) -> DexRetargetingConfig:
        return cls(**config)


@dataclass
class HandConfig:
    dimension: int

    tip_indices: list[int]
    actuated_indices: list[int]
    range_max: list[float]
    range_min: list[float]

    use_tactile: bool = False

    filter: OneEuroFilterConfig = field(
        default_factory=lambda: OneEuroFilterConfig(
            min_cutoff=0.001,
            beta=50.0,
        )
    )

    left: DexRetargetingConfig = field(
        default_factory=lambda: DexRetargetingConfig(prefix="L_", urdf_path="fourier_left_hand_6dof")
    )
    right: DexRetargetingConfig = field(
        default_factory=lambda: DexRetargetingConfig(prefix="R_", urdf_path="fourier_right_hand_6dof")
    )
    type: str = "fourier"

    def __post_init__(self):
        assert len(self.actuated_indices) == self.dimension, "actuated_indices must have the same length as dimension"
        assert len(self.range_max) == self.dimension, "range_max must have the same length as dimension"
        assert len(self.range_min) == self.dimension, "range_min must have the same length as dimension"

    @classmethod
    def from_dict(cls, config: dict) -> HandConfig:
        filter_config = OneEuroFilterConfig(**config.pop("filter"))
        left_config = DexRetargetingConfig(**config.pop("left"))
        right_config = DexRetargetingConfig(**config.pop("right"))
        return cls(**config, filter=filter_config, left=left_config, right=right_config)


FOURIER_6DOF_BASE_CONFIG = HandConfig(
    dimension=6,
    tip_indices=[4, 9, 14, 19, 24],
    actuated_indices=[0, 2, 6, 4, 9, 8],
    range_max=[0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
    range_min=[1.0, 1.0, 1.0, 1.0, 0.0, 1.0],
    use_tactile=False,
    filter=OneEuroFilterConfig(min_cutoff=0.001, beta=50.0),
    left=DexRetargetingConfig(
        prefix="L_",
        urdf_path="fourier_left_hand_6dof",
        target_joint_names=HAND_JOINT_GROUPS[HandType.FOURIER_6DOF],
        scaling_factor=1.12,
        low_pass_alpha=1.0,
    ),
    right=DexRetargetingConfig(
        prefix="R_",
        urdf_path="fourier_right_hand_6dof",
        target_joint_names=HAND_JOINT_GROUPS[HandType.FOURIER_6DOF],
        scaling_factor=1.12,
        low_pass_alpha=1.0,
    ),
)

FOURIER_12DOF_BASE_CONFIG = HandConfig(
    dimension=12,
    tip_indices=[4, 9, 14, 19, 24],
    actuated_indices=[2, 1, 0, 4, 3, 8, 7, 6, 5, 11, 10, 9],
    range_max=[1780.0, 1780.0, 0.0, 1780.0, 1780.0, 1780.0, 1780.0, 1780.0, 1780.0, 0.0, 0.0, 1700.0],
    range_min=[0.0, 0.0, 576.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1700.0, 1700.0, 0.0],
    use_tactile=False,
    filter=OneEuroFilterConfig(min_cutoff=0.001, beta=50.0),
    left=DexRetargetingConfig(
        prefix="L_",
        urdf_path="fourier_left_hand_12dof",
        target_joint_names=HAND_JOINT_GROUPS[HandType.FOURIER_12DOF],
        scaling_factor=1.1,
        low_pass_alpha=1.0,
    ),
    right=DexRetargetingConfig(
        prefix="R_",
        urdf_path="fourier_right_hand_12dof",
        target_joint_names=HAND_JOINT_GROUPS[HandType.FOURIER_12DOF],
        scaling_factor=1.1,
        low_pass_alpha=1.0,
    ),
)


HAND_BASE_CONFIGS = {
    HandType.FOURIER_6DOF: FOURIER_6DOF_BASE_CONFIG,
    HandType.FOURIER_12DOF: FOURIER_12DOF_BASE_CONFIG,
}
