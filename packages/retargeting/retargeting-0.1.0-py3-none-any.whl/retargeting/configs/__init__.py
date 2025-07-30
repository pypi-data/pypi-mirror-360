from pathlib import Path
from typing import cast

from omegaconf import DictConfig, OmegaConf

from retargeting import CONF_DIR
from retargeting.configs.common import HAND_JOINT_GROUPS, ROBOT_JOINT_GROUPS
from retargeting.configs.filter import OneEuroFilterConfig, OrientationFilterConfig
from retargeting.configs.hand import HandConfig, HandType
from retargeting.configs.ik import IKConfig
from retargeting.configs.robot import BASE_CONFIGS, RobotConfig, RobotType

__all__ = [
    "HAND_JOINT_GROUPS",
    "ROBOT_JOINT_GROUPS",
    "HandConfig",
    "HandType",
    "IKConfig",
    "RobotConfig",
    "RobotType",
    "OneEuroFilterConfig",
    "OrientationFilterConfig",
]


def load_structured(scheme: RobotConfig, config: DictConfig) -> RobotConfig:
    schema_conf = OmegaConf.structured(scheme)
    merged_conf = OmegaConf.merge(schema_conf, config)
    return cast(RobotConfig, OmegaConf.to_object(merged_conf))


def save_structured(config: RobotConfig, path: str):
    schema_conf = OmegaConf.structured(config)
    with open(path, "w") as f:
        f.write(OmegaConf.to_yaml(schema_conf))


class ConfigFactory:
    group_order = [
        "left_leg",
        "right_leg",
        "waist",
        "head",
        "left_arm",
        "right_arm",
        "left_hand",
        "right_hand",
    ]

    @classmethod
    def get(cls, robot_name: str, hand_name: str) -> RobotConfig:
        """
        Load a config file from the default config directory.

        Args:
            name (Literal[&quot;gr1t1&quot;, &quot;gr2&quot;]): Name of the config to load.

        Raises:
            FileNotFoundError: If the config file does not exist.
            TypeError: If the config file is not a DictConfig.

        Returns:
            RobotConfig: The loaded config.
        """

        robot_type = RobotType.from_str(robot_name)
        hand_type = HandType.from_str(hand_name)

        return RobotConfig.new(
            robot_name=robot_type,
            hand_type=hand_type,
            group_order=cls.group_order,
        )

    @classmethod
    def load(cls, robot_name: str, hand_name: str, path: str | Path) -> RobotConfig:
        """
        Load a config file from a path.

        Args:
            name (Literal[&quot;gr1t1&quot;, &quot;gr2&quot;]): Name of the config to load.
            path (str): Path to the config file.

        Raises:
            FileNotFoundError: If the config file does not exist.
            TypeError: If the config file is not a DictConfig.

        Returns:
            RobotConfig: The loaded config.
        """
        config_path = Path(path).resolve()
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        file_config = OmegaConf.load(config_path)
        if not isinstance(file_config, DictConfig):
            raise TypeError(f"Expected DictConfig, but got {type(file_config)} from {config_path}")
        return load_structured(cls.get(robot_name, hand_name), file_config)
