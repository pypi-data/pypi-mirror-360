from __future__ import annotations

from dataclasses import dataclass, field
from functools import reduce
from typing import cast

from omegaconf import DictConfig, OmegaConf

from retargeting.configs.common import ROBOT_JOINT_GROUPS
from retargeting.configs.hand import HAND_BASE_CONFIGS, HandConfig
from retargeting.configs.ik import IK_BASE_CONFIGS, IKConfig
from retargeting.typing import HandType, RobotType, XYZQuat


@dataclass
class FrameConfig:
    name: str
    parent: str
    transform: list[float]  # XYZQuat


@dataclass
class SelfCollisionConfig:
    enable: bool = False
    min_distance: float = 0.02
    enabled_links: list[str] = field(default_factory=list)


@dataclass
class RobotConfig:
    robot_name: RobotType
    hand_type: HandType
    group_order: list[str]
    hands: HandConfig
    inverse_kinematics: IKConfig

    joint_names: list[str]
    joint_groups: dict[str, list[str]]
    joints_to_lock: list[str] = field(default_factory=list)
    joint_limits: dict[str, list[float]] = field(default_factory=dict)
    velocity_limits: dict[str, float] = field(default_factory=dict)
    self_collision: SelfCollisionConfig = field(default_factory=SelfCollisionConfig)
    frames: list[FrameConfig] = field(default_factory=list)
    displayed_frames: list[str] = field(default_factory=list)
    display_collisions: bool = False
    visualize: bool = False
    debug: bool = False
    debug_hand: bool = False

    @classmethod
    def new(cls, robot_name: str | RobotType, hand_type: str | HandType, group_order: list[str]):
        if isinstance(robot_name, str):
            robot_name = RobotType.from_str(robot_name)
        if isinstance(hand_type, str):
            hand_type = HandType.from_str(hand_type)

        hands = HAND_BASE_CONFIGS[hand_type]
        inverse_kinematics = IK_BASE_CONFIGS[robot_name]

        joint_groups = {}
        joint_groups.update(ROBOT_JOINT_GROUPS[robot_name])

        if "left_hand" in group_order:
            left_hand_group = {"left_hand": hands.left.target_joint_names}
            joint_groups.update(left_hand_group)

        if "right_hand" in group_order:
            right_hand_group = {"right_hand": hands.right.target_joint_names}
            joint_groups.update(right_hand_group)

        joint_names = reduce(list.__add__, joint_groups.values())
        return cls(
            robot_name=robot_name,
            hand_type=hand_type,
            group_order=group_order,
            hands=hands,
            inverse_kinematics=inverse_kinematics,
            joint_names=joint_names,
            joint_groups=joint_groups,
        )

    @classmethod
    def from_dict(cls, config: dict) -> RobotConfig:
        robot_name = RobotType.from_str(config.pop("robot_name"))
        hand_type = HandType.from_str(config.pop("hand_type"))
        hands_config = HandConfig.from_dict(config.pop("hands"))
        ik_config = IKConfig.from_dict(config.pop("inverse_kinematics"))
        frames_config = [FrameConfig(**frame) for frame in config.pop("frames")]
        self_collision_config = SelfCollisionConfig(**config.pop("self_collision"))
        return cls(
            robot_name=robot_name,
            hand_type=hand_type,
            **config,
            hands=hands_config,
            inverse_kinematics=ik_config,
            frames=frames_config,
            self_collision=self_collision_config,
        )

    def save(self, path: str):
        schema_conf = OmegaConf.structured(self)
        with open(path, "w") as f:
            f.write(OmegaConf.to_yaml(schema_conf))


GR1T1_BASE_CONFIG = RobotConfig.new(
    robot_name=RobotType.GR1T1,
    hand_type=HandType.FOURIER_12DOF,
    group_order=[
        "left_leg",
        "right_leg",
        "waist",
        "head",
        "left_arm",
        "right_arm",
        "left_hand",
        "right_hand",
    ],
)


GR2_BASE_CONFIG = RobotConfig.new(
    robot_name=RobotType.GR2T2,
    hand_type=HandType.FOURIER_6DOF,
    group_order=[
        "left_leg",
        "right_leg",
        "waist",
        "head",
        "left_arm",
        "right_arm",
        "left_hand",
        "right_hand",
    ],
)

GR2T2D_BASE_CONFIG = RobotConfig.new(
    robot_name=RobotType.GR2T2D,
    hand_type=HandType.FOURIER_6DOF,
    group_order=[
        "left_leg",
        "right_leg",
        "waist",
        "head",
        "left_arm",
        "right_arm",
        "left_hand",
        "right_hand",
    ],
)

BASE_CONFIGS = {
    RobotType.GR1T1: GR1T1_BASE_CONFIG,
    RobotType.GR2T2: GR2_BASE_CONFIG,
    RobotType.GR2T2D: GR2T2D_BASE_CONFIG,
}
