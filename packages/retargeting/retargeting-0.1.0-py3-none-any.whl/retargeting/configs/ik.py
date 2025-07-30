from __future__ import annotations

from dataclasses import dataclass, field

from retargeting.configs.filter import OneEuroFilterConfig, OrientationFilterConfig
from retargeting.typing import RobotType


@dataclass
class NamedLinks:
    root_link: str = "base_link"
    left_end_effector_link: str = "left_end_effector_link"
    right_end_effector_link: str = "right_end_effector_link"
    head_link: str = "head_pitch_link"
    left_elbow_pitch_joint: str = "left_elbow_pitch_joint"
    right_elbow_pitch_joint: str = "right_elbow_pitch_joint"


@dataclass
class IKConfig:
    named_links: NamedLinks = field(default_factory=NamedLinks)
    body_scaling_factor: float = 1.0
    position_filter: OneEuroFilterConfig = field(
        default_factory=lambda: OneEuroFilterConfig(
            min_cutoff=0.01,
            beta=1.0,
        )
    )
    orientation_filter: OrientationFilterConfig = field(
        default_factory=lambda: OrientationFilterConfig(
            alpha=0.6,
        )
    )

    joint_action_filter: OneEuroFilterConfig = field(
        default_factory=lambda: OneEuroFilterConfig(
            min_cutoff=0.01,
            beta=10.0,
        )
    )

    head_action_filter: OrientationFilterConfig = field(
        default_factory=lambda: OrientationFilterConfig(
            alpha=0.7,
        )
    )

    @classmethod
    def from_dict(cls, config: dict) -> IKConfig:
        named_links = NamedLinks(**config.pop("named_links"))
        position_filter = OneEuroFilterConfig(**config.pop("position_filter"))
        orientation_filter = OrientationFilterConfig(**config.pop("orientation_filter"))
        joint_action_filter = OneEuroFilterConfig(**config.pop("joint_action_filter"))
        head_action_filter = OrientationFilterConfig(**config.pop("head_action_filter"))
        return cls(
            **config,
            named_links=named_links,
            position_filter=position_filter,
            orientation_filter=orientation_filter,
            joint_action_filter=joint_action_filter,
            head_action_filter=head_action_filter,
        )


GR1T1_BASE_IK_CONFIG = IKConfig(
    body_scaling_factor=1.15,
    position_filter=OneEuroFilterConfig(
        min_cutoff=0.01,
        beta=1.0,
    ),
    orientation_filter=OrientationFilterConfig(
        alpha=0.6,
    ),
    named_links=NamedLinks(
        root_link="base_link",
        left_end_effector_link="left_end_effector_link",
        right_end_effector_link="right_end_effector_link",
        head_link="head_pitch_link",
        left_elbow_pitch_joint="left_elbow_pitch_joint",
        right_elbow_pitch_joint="right_elbow_pitch_joint",
    ),
)

GR2_BASE_IK_CONFIG = IKConfig(
    body_scaling_factor=1.15,
    position_filter=OneEuroFilterConfig(
        min_cutoff=0.01,
        beta=1.0,
    ),
    orientation_filter=OrientationFilterConfig(
        alpha=0.6,
    ),
    named_links=NamedLinks(
        root_link="base_link",
        left_end_effector_link="left_end_effector_link",
        right_end_effector_link="right_end_effector_link",
        head_link="head_pitch_link",
        left_elbow_pitch_joint="left_elbow_pitch_joint",
        right_elbow_pitch_joint="right_elbow_pitch_joint",
    ),
)


GR2T2D_BASE_IK_CONFIG = IKConfig(
    body_scaling_factor=1.3,
    position_filter=OneEuroFilterConfig(
        min_cutoff=0.01,
        beta=1.0,
    ),
    orientation_filter=OrientationFilterConfig(
        alpha=0.6,
    ),
    named_links=NamedLinks(
        root_link="base_link",
        left_end_effector_link="left_end_effector_link",
        right_end_effector_link="right_end_effector_link",
        head_link="head_pitch_link",
        left_elbow_pitch_joint="left_elbow_pitch_joint",
        right_elbow_pitch_joint="right_elbow_pitch_joint",
    ),
)


IK_BASE_CONFIGS = {
    RobotType.GR1T1: GR1T1_BASE_IK_CONFIG,
    RobotType.GR2T2: GR2_BASE_IK_CONFIG,
    RobotType.GR2T2D: GR2T2D_BASE_IK_CONFIG,
}
