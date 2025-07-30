from __future__ import annotations

import time
from typing import Literal

import numpy as np
import pink
import pinocchio as pin
import qpsolvers

from retargeting.configs import RobotConfig
from retargeting.filters import LPRotationFilter, OneEuroFilter
from retargeting.hand import HandRetarget
from retargeting.robot_wrapper import RobotWrapper
from retargeting.typing import XYZQuat
from retargeting.utils import xyzw_to_wxyz


class IKRobot:
    def __init__(self, robot_config: RobotConfig):
        self.robot = RobotWrapper.from_config(robot_config)
        self.ik_config = robot_config.inverse_kinematics

        if self.ik_config is None:
            raise ValueError("Inverse kinematics config is not provided")

        self.joint_action_filter = OneEuroFilter(
            min_cutoff=self.ik_config.joint_action_filter.min_cutoff, beta=self.ik_config.joint_action_filter.beta
        )

        self.head_action_filter = LPRotationFilter(
            alpha=self.ik_config.head_action_filter.alpha,
        )

        self.tasks = {}
        self.barriers = {}

        self.left_positiion_filter = OneEuroFilter(
            min_cutoff=self.ik_config.position_filter.min_cutoff,
            beta=self.ik_config.position_filter.beta,
        )
        self.left_orientation_filter = LPRotationFilter(self.ik_config.orientation_filter.alpha)
        self.right_positiion_filter = OneEuroFilter(
            min_cutoff=self.ik_config.position_filter.min_cutoff,
            beta=self.ik_config.position_filter.beta,
        )
        self.right_orientation_filter = LPRotationFilter(self.ik_config.orientation_filter.alpha)

        if robot_config.visualize and self.viz is not None:
            # from itertools import product

            # import meshcat.geometry as g

            # if self.config.debug:
            #     self.viz.viewer["left_ee_target"].set_object(g.Box([0.1, 0.1, 0.1]))
            #     self.viz.viewer["right_ee_target"].set_object(g.Box([0.1, 0.1, 0.1]))
            #     self.viz.viewer["head"].set_object(g.Box([0.1, 0.1, 0.1]))

            # if self.config.get("debug_hand", False):
            #     for side, finger in product(["left", "right"], range(26)):
            #         if finger == 0:
            #             self.viz.viewer[f"{side}_hand/{finger}"].set_object(g.Box([0.02, 0.02, 0.02]))
            #         else:
            #             self.viz.viewer[f"{side}_hand/{finger}"].set_object(g.Sphere(0.01))
            #         if side == "left":
            #             self.viz.viewer[f"{side}_hand/{finger}"].set_property("color", [1, 0, 0, 1])
            # self.viz.display(self.configuration.q)
            self.viz.create_targets()

        self.build_tasks()

    @property
    def configuration(self):
        return self.robot.configuration

    @property
    def viz(self):
        return self.robot.viz

    def filter_pose(self, pose: pin.SE3, side: Literal["left", "right"]):
        xyzquat: XYZQuat = pin.SE3ToXYZQUAT(pose)
        t = time.time()
        if side == "left":
            xyzquat[:3] = self.left_positiion_filter.next(t, xyzquat[:3])
            xyzquat[3:] = self.left_orientation_filter.next(xyzquat[3:])
        else:
            xyzquat[:3] = self.right_positiion_filter.next(t, xyzquat[:3])
            xyzquat[3:] = self.right_orientation_filter.next(xyzquat[3:])

        return pin.XYZQUATToSE3(xyzquat)

    def build_tasks(self):
        if self.ik_config is None:
            raise ValueError("Inverse kinematics config is not provided")
        r_hand_task = pink.tasks.RelativeFrameTask(
            self.ik_config.named_links.right_end_effector_link,
            self.ik_config.named_links.root_link,
            position_cost=50.0,
            orientation_cost=10.0,
            gain=0.7,
            lm_damping=1e-3,
        )

        l_hand_task = pink.tasks.RelativeFrameTask(
            self.ik_config.named_links.left_end_effector_link,
            self.ik_config.named_links.root_link,
            position_cost=50.0,
            orientation_cost=10.0,
            gain=0.7,
            lm_damping=1e-3,
        )

        head_task = pink.tasks.RelativeFrameTask(
            self.ik_config.named_links.head_link,
            self.ik_config.named_links.root_link,
            position_cost=0.0,
            orientation_cost=1.0,
            gain=0.5,
            lm_damping=1e-1,
        )

        posture_task = pink.tasks.PostureTask(cost=1e-2)
        self.tasks = {
            "r_hand_task": r_hand_task,
            "l_hand_task": l_hand_task,
            "head_task": head_task,
            "posture_task": posture_task,
        }

        if self.robot.config.self_collision.enable:
            collision_barrier = pink.barriers.SelfCollisionBarrier(
                n_collision_pairs=len(self.robot.collision_model.collisionPairs),
                gain=20.0,
                safe_displacement_gain=1.0,
                d_min=self.robot.config.self_collision.min_distance,
            )

            self.barriers = {
                "collision_barrier": collision_barrier,
            }

    def set_posture_target_from_current_configuration(self):
        self.tasks["posture_task"].set_target_from_configuration(self.configuration)

    def solve(
        self,
        left_target_np: np.ndarray,
        right_target_np: np.ndarray,
        head_target_np: np.ndarray | None,
        dt: float,
        update_viz: bool = True,
        **kwargs,
    ):
        if self.ik_config is None:
            raise ValueError("Inverse kinematics config is not provided")
        # right_target = pin.XYZQUATToSE3(right_target)
        # left_target = pin.XYZQUATToSE3(left_target)

        right_target: pin.SE3 = pin.SE3(translation=right_target_np[:3, 3], rotation=right_target_np[:3, :3])
        left_target: pin.SE3 = pin.SE3(translation=left_target_np[:3, 3], rotation=left_target_np[:3, :3])

        left_target.translation = left_target.translation * self.ik_config.body_scaling_factor
        right_target.translation = right_target.translation * self.ik_config.body_scaling_factor

        left_target = self.filter_pose(left_target, "left")
        right_target = self.filter_pose(right_target, "right")

        if update_viz and self.viz:
            # self.viz.viewer["left_ee_target"].set_transform(left_target.homogeneous)
            # self.viz.viewer["right_ee_target"].set_transform(right_target.homogeneous)
            left_xyzquat: XYZQuat = pin.SE3ToXYZQUAT(left_target)
            right_xyzquat: XYZQuat = pin.SE3ToXYZQUAT(right_target)
            self.viz.left_target.position = left_xyzquat[:3]
            self.viz.left_target.wxyz = xyzw_to_wxyz(left_xyzquat[3:])
            self.viz.right_target.position = right_xyzquat[:3]
            self.viz.right_target.wxyz = xyzw_to_wxyz(right_xyzquat[3:])

        self.tasks["r_hand_task"].set_target(right_target)
        self.tasks["l_hand_task"].set_target(left_target)

        if head_target_np is not None:
            head_target = pin.SE3(rotation=head_target_np[:3, :3], translation=np.array([0.0, 0.0, 0.0]))
            self.tasks["head_task"].set_target(head_target)

        solver = qpsolvers.available_solvers[0]

        if "daqp" in qpsolvers.available_solvers:
            solver = "daqp"
        else:
            raise ValueError("DAQP solver is not available. Please install it.")

        velocity = pink.solve_ik(
            self.configuration,
            self.tasks.values(),
            dt,
            solver=solver,
            barriers=self.barriers.values(),
            safety_break=False,
            **kwargs,
        )
        self.configuration.integrate_inplace(velocity, dt)


class DexRobot(IKRobot):
    def __init__(self, config: RobotConfig):
        super().__init__(config)

        hand_config = config.hands

        self.left_hand_prefix = config.hands.left.prefix
        self.right_hand_prefix = config.hands.right.prefix
        self.hand_dimension = config.hands.dimension

        self.hand_filter = OneEuroFilter(min_cutoff=hand_config.filter.min_cutoff, beta=hand_config.filter.beta)

        self.hand_retarget = HandRetarget(hand_config)

    def hand_action_convert(
        self, left_qpos: np.ndarray, right_qpos: np.ndarray, filtering=True
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Convert the hand qpos to real qpos and filter it.

        Args:
            left_qpos (np.ndarray): Left hand qpos in radians
            right_qpos (np.ndarray): Right hand qpos in radians
            filtering (bool, optional): If True, filter the hand qpos. Defaults to True.

        Returns:
            tuple[np.ndarray, np.ndarray]: Left and right hand qpos in real control values
        """
        left_qpos_real, right_qpos_real = self.hand_retarget.qpos_to_real(left_qpos, right_qpos)
        if not filtering:
            filtered_hand_qpos = np.hstack([left_qpos_real, right_qpos_real])
        else:
            if self.hand_retarget.hand_type == "inspire":
                filtered_hand_qpos = self.hand_filter.next(
                    time.time(),
                    np.hstack([left_qpos_real, right_qpos_real]),
                ).astype(int)
            elif self.hand_retarget.hand_type == "fourier":
                filtered_hand_qpos = self.hand_filter.next(
                    time.time(),
                    np.hstack([left_qpos_real, right_qpos_real]),
                )
            else:
                raise ValueError("Invalid hand type.")

        return filtered_hand_qpos[: self.hand_dimension], filtered_hand_qpos[self.hand_dimension :]

    def set_hand_joints(self, left_hand_qpos: np.ndarray, right_hand_qpos: np.ndarray):
        """Set the joint positions of the hands to pinocchio

        Args:
            left_hand_qpos (ndarray): Hand qpos in radians
            right_hand_qpos (ndarray): Hand qpos in radians
        """
        self.robot.set_joint_positions(self.hand_retarget.right_joint_names, right_hand_qpos, mimic=True)
        self.robot.set_joint_positions(self.hand_retarget.left_joint_names, left_hand_qpos, mimic=True)
