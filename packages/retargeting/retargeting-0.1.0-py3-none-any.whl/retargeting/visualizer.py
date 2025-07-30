from itertools import product
from pathlib import Path
from typing import Literal

import numpy as np
import viser
import viser.transforms as tf
import yourdfpy
from loguru import logger
from numba import njit
from viser.extras import ViserUrdf

from fourier_robot_descriptions.fourier import PACKAGE_PATH


def create_robot_control_sliders(
    server: viser.ViserServer, viser_urdf: ViserUrdf
) -> tuple[list[viser.GuiInputHandle[float]], list[float]]:
    slider_handles: list[viser.GuiInputHandle[float]] = []
    initial_config: list[float] = []
    for joint_name, (
        lower,
        upper,
    ) in viser_urdf.get_actuated_joint_limits().items():
        # if "knee" in joint_name or "hip" in joint_name or "ankle" in joint_name:
        #     continue
        lower = lower if lower is not None else -np.pi
        upper = upper if upper is not None else np.pi
        # initial_pos = 0.0 if lower < -0.1 and upper > 0.1 else (lower + upper) / 2.0
        initial_pos = 0.0
        slider = server.gui.add_slider(
            label=joint_name,
            min=lower,
            max=upper,
            step=1e-3,
            initial_value=initial_pos,
        )

        slider.on_update(  # When sliders move, we update the URDF configuration.
            lambda _: viser_urdf.update_cfg(np.array([slider.value for slider in slider_handles]))
        )
        slider_handles.append(slider)
        initial_config.append(initial_pos)

    return slider_handles, initial_config


@njit
def xyzquat_to_viser(xyzquat: np.ndarray) -> tf.SE3:
    return tf.SE3.from_rotation_and_translation(tf.SO3.from_quaternion_xyzw(xyzquat[3:]), xyzquat[:3])


class ViserVisualizer:
    def __init__(
        self, server: viser.ViserServer, urdf_path: Path, load_meshes: bool = True, load_collision_meshes: bool = False
    ):
        self.server = server

        # self.create_targets()

        # urdf = yourdfpy.URDF.load(
        #     urdf_path,
        #     load_meshes=load_meshes,
        #     build_scene_graph=load_meshes,
        #     load_collision_meshes=load_collision_meshes,
        #     build_collision_scene_graph=load_collision_meshes,
        # )
        self.viser_urdf = ViserUrdf(
            server,
            urdf_or_path=urdf_path,
            mesh_color_override=(0.0, 0.0, 1.0, 0.5),
            root_node_name="/target",
            load_meshes=True,
            load_collision_meshes=False,
        )

        trimesh_scene = self.viser_urdf._urdf.scene or self.viser_urdf._urdf.collision_scene
        self.server.scene.add_grid(
            "/ground",
            width=2,
            height=2,
            position=(
                0.0,
                0.0,
                # Get the minimum z value of the trimesh scene.
                trimesh_scene.bounds[0, 2] if trimesh_scene is not None else 0.0,
            ),
        )

        self.viser_urdf_state = ViserUrdf(
            server,
            urdf_or_path=urdf_path,
            root_node_name="/states",
            load_meshes=True,
            load_collision_meshes=False,
        )

        # Add visibility checkboxes.
        with self.server.gui.add_folder("Target Visibility"):
            show_meshes_cb = self.server.gui.add_checkbox(
                "Show meshes",
                self.viser_urdf.show_visual,
            )
            show_collision_meshes_cb = self.server.gui.add_checkbox(
                "Show collision meshes", self.viser_urdf.show_collision
            )
        with self.server.gui.add_folder("State Visibility"):
            show_state_meshes_cb = self.server.gui.add_checkbox(
                "Show meshes",
                self.viser_urdf_state.show_visual,
            )
            show_state_collision_meshes_cb = self.server.gui.add_checkbox(
                "Show collision meshes", self.viser_urdf_state.show_collision
            )

        @show_meshes_cb.on_update
        def _(_):
            self.viser_urdf.show_visual = show_meshes_cb.value

        @show_collision_meshes_cb.on_update
        def _(_):
            self.viser_urdf.show_collision = show_collision_meshes_cb.value

        @show_state_meshes_cb.on_update
        def _(_):
            self.viser_urdf_state.show_visual = show_state_meshes_cb.value

        @show_state_collision_meshes_cb.on_update
        def _(_):
            self.viser_urdf_state.show_collision = show_state_collision_meshes_cb.value

        # Hide checkboxes if meshes are not loaded.
        show_meshes_cb.visible = load_meshes
        show_collision_meshes_cb.visible = load_collision_meshes

        show_state_meshes_cb.visible = load_meshes
        show_state_collision_meshes_cb.visible = load_collision_meshes

        logger.info("Visualizer initialized")

    def set_limits(self, joint_names: list[str], lowers: np.ndarray, uppers: np.ndarray):
        for joint_name, lower, upper in zip(joint_names, lowers, uppers):
            self.viser_urdf._urdf.joint_map[joint_name].limit.lower = lower
            self.viser_urdf._urdf.joint_map[joint_name].limit.upper = upper

            self.viser_urdf_state._urdf.joint_map[joint_name].limit.lower = lower
            self.viser_urdf_state._urdf.joint_map[joint_name].limit.upper = upper

    def _display(self, q_dict: dict[str, float], urdf: ViserUrdf):
        urdf._urdf.update_cfg(q_dict)
        for joint, frame_handle in zip(urdf._joint_map_values, urdf._joint_frames):
            assert isinstance(joint, yourdfpy.Joint)
            T_parent_child = urdf._urdf.get_transform(
                joint.child, joint.parent, collision_geometry=not urdf._load_meshes
            )
            frame_handle.wxyz = tf.SO3.from_matrix(T_parent_child[:3, :3]).wxyz
            frame_handle.position = T_parent_child[:3, 3] * urdf._scale

    def display(self, q_dict: dict[str, float]):
        self._display(q_dict, self.viser_urdf)

    def display_state(self, q_dict: dict[str, float]):
        self._display(q_dict, self.viser_urdf_state)

    def create_joint_sliders(self, urdf: ViserUrdf):
        # Create sliders in GUI that help us move the robot joints.
        with self.server.gui.add_folder("Joint position control", expand_by_default=False):
            (slider_handles, initial_config) = create_robot_control_sliders(self.server, urdf)

        urdf.update_cfg(np.array(initial_config))

        # Create joint reset button.
        reset_button = self.server.gui.add_button("Reset")

        @reset_button.on_click
        def _(_):
            for s, init_q in zip(slider_handles, initial_config):
                s.value = init_q

        return slider_handles, initial_config

    def create_targets(self):
        self.left_target = self.server.scene.add_transform_controls(
            "/target/left", scale=0.2, position=(0.45, 0.2, 0.0), wxyz=(0.7, 0, -0.7, 0)
        )
        self.right_target = self.server.scene.add_transform_controls(
            "/target/right", scale=0.2, position=(0.45, -0.2, 0.0), wxyz=(0.7, 0, -0.7, 0)
        )
        self.head_target = self.server.scene.add_transform_controls(
            "/target/head", scale=0.2, position=(0.0, 0.0, 0.7), wxyz=(1, 0, 0, 0)
        )

        # @self.left_target.on_update
        # def _(_):
        #     print(self.left_target.position, self.left_target.wxyz)

    def show_frame(self, frame_name: str):
        joint_frame_names = [j.name.split("/")[-1] for j in self.viser_urdf._joint_frames]
        if frame_name not in joint_frame_names:
            logger.warning(f"Frame {frame_name} not found for visualization")
            return
        frame_idx = joint_frame_names.index(frame_name)
        self.viser_urdf._joint_frames[frame_idx].axes_length = 0.15
        self.viser_urdf._joint_frames[frame_idx].axes_radius = 0.01
        self.viser_urdf._joint_frames[frame_idx].origin_radius = 0.02
        self.viser_urdf._joint_frames[frame_idx].show_axes = True

    def create_hand_landmarks(self):
        self.hand_landmarks = {"left": [], "right": []}
        for side, finger in product(["left", "right"], range(26)):
            self.hand_landmarks[side].append(
                self.server.scene.add_box(
                    f"/target/hands/{side}/{finger}",
                    dimensions=(0.01, 0.01, 0.01),
                    opacity=0.5,
                    position=(0.0, 0.0, 0.0),
                    wxyz=(1, 0, 0, 0),
                    cast_shadow=False,
                    receive_shadow=False,
                )
            )

    def update_hand_landmarks(
        self,
        hand_landmarks: np.ndarray,
        side: Literal["left", "right"],
        body_scaling_factor: float,
        hand_scaling_factor: float,
    ):
        wrist_xyzquat = hand_landmarks[0, :]
        wrist_xyzquat[:3] *= body_scaling_factor
        wrist_tf = xyzquat_to_viser(wrist_xyzquat)
        hand_landmarks_tf = []

        for i in range(hand_landmarks.shape[0]):
            hand_xyzquat = hand_landmarks[i, :]
            hand_xyzquat[:3] *= hand_scaling_factor
            hand_landmarks_tf.append(wrist_tf @ xyzquat_to_viser(hand_xyzquat))

        self.hand_landmarks[side][0].position = wrist_tf.wxyz_xyz[-3:]
        self.hand_landmarks[side][0].wxyz = wrist_tf.wxyz_xyz[:4]
        for i, landmark in enumerate(hand_landmarks_tf):
            self.hand_landmarks[side][i + 1].position = landmark.wxyz_xyz[-3:]
            self.hand_landmarks[side][i + 1].wxyz = landmark.wxyz_xyz[:4]
