import itertools
from collections.abc import Sequence
from dataclasses import dataclass
from shlex import join

import numpy as np
import pink
import pinocchio as pin
import viser
from loguru import logger
from pinocchio.shortcuts import (
    createDatas,
)
from yourdfpy import urdf

from fourier_robot_descriptions.fourier import PACKAGE_PATH
from fourier_robot_descriptions.loaders.pinocchio import load_robot_description
from retargeting.configs import ConfigFactory, RobotConfig


def build_reduced_robot(model, visual_model, collision_model, list_of_joints_to_lock, reference_configuration=None):
    """
    Build a reduced robot model given a list of joints to lock.
    Parameters:
    \tlist_of_joints_to_lock: list of joint indexes/names to lock.
    \treference_configuration: reference configuration to compute the
    placement of the lock joints. If not provided, reference_configuration
    defaults to the robot's neutral configuration.

    Returns: a new robot model.
    """

    # if joint to lock is a string, try to find its index
    lockjoints_idx = []
    for jnt in list_of_joints_to_lock:
        idx = jnt
        if isinstance(jnt, str):
            idx = model.getJointId(jnt)
        lockjoints_idx.append(idx)

    if reference_configuration is None:
        reference_configuration = pin.neutral(model)

    model, geom_models = pin.buildReducedModel(
        model=model,
        list_of_geom_models=[visual_model, collision_model],
        list_of_joints_to_lock=lockjoints_idx,
        reference_configuration=reference_configuration,
    )

    return model, geom_models[0], geom_models[1]


def parse_mimic_joint(
    robot_urdf: urdf.URDF,
) -> tuple[bool, list[str], list[str], list[float], list[float]]:
    mimic_joint_names = []
    source_joint_names = []
    multipliers = []
    offsets = []
    for name, joint in robot_urdf.joint_map.items():
        if joint.mimic is not None:
            mimic_joint_names.append(name)
            source_joint_names.append(joint.mimic.joint)
            multipliers.append(joint.mimic.multiplier)
            offsets.append(joint.mimic.offset)

    return (
        len(mimic_joint_names) > 0,
        source_joint_names,
        mimic_joint_names,
        multipliers,
        offsets,
    )


@dataclass
class MimicJointAdapter:
    mimicked_joints: list[int]
    mimicking_joints: list[int]
    multipliers: np.ndarray
    offsets: np.ndarray

    @classmethod
    def from_urdf(cls, name: str):
        urdf = load_robot_description(name.lower(), root_joint=pin.JointModelFreeFlyer(), mimic=True)
        multipliers = [getattr(urdf.model.joints[i].extract(), "scaling", None) for i in urdf.model.mimicking_joints]
        offsets = [getattr(urdf.model.joints[i].extract(), "offset", None) for i in urdf.model.mimicking_joints]
        return cls(
            mimicked_joints=list(urdf.model.mimicked_joints),
            mimicking_joints=list(urdf.model.mimicking_joints),
            multipliers=np.array(multipliers),
            offsets=np.array(offsets),
        )

    @classmethod
    def from_yourdfpy(cls, name: str, model: pin.Model):
        from fourier_robot_descriptions.loaders.yourdfpy import (  # noqa: PLC0415
            load_robot_description as load_robot_description_yourdfpy,
        )

        urdf = load_robot_description_yourdfpy(
            name.lower(),
            load_meshes=False,
            build_scene_graph=False,
            load_collision_meshes=False,
            build_collision_scene_graph=False,
        )
        _has_mimic_joint, mimicked_joint_names, mimicking_joint_names, multipliers, offsets = parse_mimic_joint(urdf)
        return cls(
            mimicked_joints=[model.getJointId(name) for name in mimicked_joint_names],
            mimicking_joints=[model.getJointId(name) for name in mimicking_joint_names],
            multipliers=np.array(multipliers),
            offsets=np.array(offsets),
        )

    def forward_qpos(self, pin_qpos: np.ndarray) -> np.ndarray:
        mimic_qpos = pin_qpos[self.mimicking_joints] * self.multipliers + self.offsets
        pin_qpos[self.mimicked_joints] = mimic_qpos
        return pin_qpos

    def forward(self, mimicked_id: int, pos: float) -> tuple[int, float]:
        mimicked_idx = self.mimicked_joints.index(mimicked_id)
        mimicking_joint_id = self.mimicking_joints[mimicked_idx]
        mimic_qpos = pos * self.multipliers[mimicked_idx] + self.offsets[mimicked_idx]
        return mimicking_joint_id, mimic_qpos


class RobotWrapper:
    def __init__(
        self,
        config: RobotConfig,
        model: pin.Model,
        collision_model: pin.GeometryModel,
        visual_model: pin.GeometryModel,
        verbose=False,
    ):
        self.model = model
        self.collision_model = collision_model
        self.visual_model = visual_model
        self.config = config

        self.data, self.collision_data, self.visual_data = createDatas(model, collision_model, visual_model)

        self.v0 = np.zeros(self.nv)
        self.q0 = pin.neutral(self.model)

        self.viz = None

        self.mimic_adaptor = MimicJointAdapter.from_yourdfpy(self.urdf_name, self.model)

        for name, limits in config.joint_limits.items():
            logger.info(f"Setting joint limits for {name}: {limits}")
            self.set_joint_limits(name, limits[0], limits[1])

        for name, limit in config.velocity_limits.items():
            logger.info(f"Setting velocity limits for {name}: {limit}")
            self.set_velocity_limit(name, limit)

        for frame in config.frames:
            logger.info(f"Adding dummy frame: {frame.name}")
            self.add_frame(frame.name, frame.parent, pin.XYZQUATToSE3(frame.transform))

        # robot.collision_model.addAllCollisionPairs()
        if config.self_collision.enable:
            for g1, g2 in itertools.combinations(config.self_collision.enabled_links, 2):
                logger.info(f"Adding collision pair: {g1} - {g2}")
                self.collision_model.addCollisionPair(
                    pin.CollisionPair(
                        self.collision_model.getGeometryId(g1 + "_0"),
                        self.collision_model.getGeometryId(g2 + "_0"),
                    )
                )

        self.rebuild_data()

        self.collision_data.enable_contact = True

        self.configuration = self.make_configuration()  # this is the target configuration
        self.current_configuration = self.make_configuration()  # this is the current configuration

        self.make_visualizer()

    def make_configuration(self, q: np.ndarray | None = None):
        if q is None:
            q = self.q0
        configuration = pink.Configuration(
            self.model,
            self.data,
            q,
            collision_model=self.collision_model,
            collision_data=self.collision_data,
        )
        return configuration

    @property
    def urdf_name(self):
        return (self.config.robot_name.value + "_" + self.config.hand_type.value).lower()

    @classmethod
    def from_config(cls, config: RobotConfig):
        _urdf_name = config.robot_name.value + "_" + config.hand_type.value
        urdf = load_robot_description(_urdf_name.lower(), root_joint=pin.JointModelFreeFlyer(), mimic=False)
        # urdf_full = load_robot_description(_urdf_name.lower(), root_joint=pin.JointModelFreeFlyer(), mimic=False)

        if config.joints_to_lock:
            logger.info(f"Locking joints: {config.joints_to_lock}")
            model, visual_model, collision_model = build_reduced_robot(
                urdf.model, urdf.visual_model, urdf.collision_model, config.joints_to_lock
            )
            robot = cls(config, model, collision_model, visual_model)
        else:
            robot = cls(config, urdf.model, urdf.collision_model, urdf.visual_model)

        return robot

    def __getitem__(self, key: int | str):
        if isinstance(key, int):
            return self.model.joints[key]
        elif isinstance(key, str):
            return self.get_joint_by_name(key)
        else:
            raise TypeError("Key must be an integer or a string")

    @property
    def mimicked_joints(self):
        return self.mimic_adaptor.mimicked_joints

    @property
    def mimicking_joints(self):
        return self.mimic_adaptor.mimicking_joints

    @property
    def mimic_multipliers(self):
        return self.mimic_adaptor.multipliers

    @property
    def mimic_offsets(self):
        return self.mimic_adaptor.offsets

    @property
    def num_joints(self) -> int:
        return len(self.config.joint_names)

    @property
    def dof_joint_names(self) -> list[str]:
        """
        Get the names of the degrees of freedom (DOF) joints.
        """
        nqs = self.model.nqs
        return [name for i, name in enumerate(self.model.names) if nqs[i] > 0]

    @property
    def dof(self) -> int:
        """Get the number of degrees of freedom (DOF) of the robot."""
        return self.model.nq

    @property
    def link_names(self) -> list[str]:
        """Get the names of the links."""
        link_names = []
        for i, frame in enumerate(self.model.frames):
            link_names.append(frame.name)
        return link_names

    @property
    def joint_limits(self) -> np.ndarray:
        """Get the joint limits."""
        lower = self.model.lowerPositionLimit
        upper = self.model.upperPositionLimit
        return np.stack([lower, upper], axis=1)

    @property
    def q_real(self):
        """Get q vector in the real robot convention (length is 32, order same as config.joint_names)."""
        q = []
        for name in self.config.joint_names:
            q.append(self.get_q_from_name(name))
        return np.array(q)

    @q_real.setter
    def q_real(self, q: np.ndarray):
        """Set from a q vector in the real robot convention (length is 32, order same as config.joint_names))."""
        self.set_joint_positions(self.config.joint_names, q)

    @property
    def q_dict(self):
        return dict(zip(self.config.joint_names, self.q_real, strict=True))

    @q_dict.setter
    def q_dict(self, q_dict: dict[str, float]):
        self.set_joint_positions(list(q_dict.keys()), np.array(list(q_dict.values())))

    def q_real2pink(self, q: np.ndarray, mimic=True):
        """Convert q vector from real robot convention to pink convention."""
        q_pink = self.configuration.q.copy()
        for name, value in zip(self.config.joint_names, q, strict=True):
            if name in self.config.joints_to_lock:
                continue
            joint_idx = self.get_idx_q_from_name(name)

            if mimic:
                if joint_idx in self.mimicked_joints:
                    q_mimick_idx, mimic_pos = self.mimic_adaptor.forward(joint_idx, value)
                    q_pink[q_mimick_idx] = mimic_pos
                if joint_idx in self.mimicking_joints:
                    continue

            q_pink[joint_idx] = value
        return q_pink

    def q_pink2real(self, q: np.ndarray):
        """Convert q vector from pink convention to real robot convention."""
        q_real = []
        for name in self.config.joint_names:
            if name in self.config.joints_to_lock:
                q_real.append(0.0)  # TODO: this might be locked at a different value
                continue
            q_real.append(q[self.get_idx_q_from_name(name)])
        return np.array(q_real)

    def get_joint_by_name(self, name: str):
        """Get joint object by its name."""
        try:
            joint_id = self.model.getJointId(name)
            joint = self.model.joints[joint_id]
            return joint
        except IndexError as err:
            raise IndexError(f"Joint {name} not found in robot model") from err

    def get_idx_q_from_name(self, name: str):
        """Get joint index in Pinocchio configuration vector by its name.

        Args:
            name (str): Name of the joint.
        """
        return self.get_joint_by_name(name).idx_q

    def get_q_from_name(self, name: str):
        """Get joint position in Pinocchio configuration vector by its name.

        Args:
            name (str): Name of the joint.
        """
        if name in self.config.joints_to_lock:
            return 0.0
        return self.configuration.q[self.get_idx_q_from_name(name)]

    def get_idx_v_from_name(self, name: str):
        """Get joint index in Pinocchio velocity vector by its name.

        Args:
            name (str): Name of the joint.
        """
        return self.get_joint_by_name(name).idx_v

    def get_v_from_name(self, name: str):
        """Get joint velocity in Pinocchio velocity vector by its name.

        Args:
            name (str): Name of the joint.
        """
        if name in self.config.joints_to_lock:
            return 0.0
        return self.configuration.data.dq_after[self.get_idx_v_from_name(name)]

    def add_frame(self, frame_name: str, parent: str, transform: pin.SE3 | None = None):
        """Add a dummy frame to the robot model.

        Args:
            frame_name (str): Name of the frame.
            parent (str): Name of the parent frame.
            transform (pin.SE3 | None, optional): Transform from parent frame to the new frame. Defaults to None. If None, identity transform is used.
        """
        if frame_name in self.model.names:
            logger.warning(f"Frame {frame_name} already exists in robot model")
            return
        if self.model.existFrame(parent) is not True:
            logger.warning(f"Parent frame {parent} not found in robot model")
            return

        if transform is None:
            transform = pin.SE3.Identity()
        self.model.addFrame(
            pin.Frame(
                frame_name,
                self.model.frames[self.model.getFrameId(parent)].parent,
                self.model.getFrameId(parent),
                transform,
                pin.FrameType.OP_FRAME,
            )
        )

    def set_joint_positions(
        self,
        joint_names: list[str],
        positions: np.ndarray,
        degrees: bool = False,
        clip: bool = True,
        mimic=True,
        state=False,
    ):
        """Set joint positions in the robot configuration.

        Args:
            joint_names (list[str]): Names of the joints.
            positions (np.ndarray): Joint positions, AKA `q` vector in the robot definition.
            degrees (bool, optional): If True, positions are in degrees. Defaults to False.
            clip (bool, optional): If True, clip joint limits. Defaults to True.
            mimic (bool, optional): If True, mimic joint positions. Defaults to True.
            state (bool, optional): If True, set joint positions in the state configuration. Defaults to False.
        """

        if state:
            configuration = self.current_configuration
        else:
            configuration = self.configuration

        if degrees:
            positions = np.deg2rad(positions)
        current_q = configuration.q.copy()
        for joint_name, position in zip(joint_names, positions, strict=True):
            if joint_name in self.config.joints_to_lock:
                continue

            q_idx = self.get_idx_q_from_name(joint_name)

            if mimic:
                if q_idx in self.mimicking_joints:
                    continue
                if q_idx in self.mimicked_joints:
                    q_mimick_idx, mimic_pos = self.mimic_adaptor.forward(q_idx, position)
                    if clip:
                        lower = self.model.lowerPositionLimit[q_mimick_idx]
                        upper = self.model.upperPositionLimit[q_mimick_idx]
                        mimic_pos = np.clip(mimic_pos, lower, upper)
                        current_q[q_mimick_idx] = mimic_pos
                    else:
                        current_q[q_mimick_idx] = position

            # clip joint limits
            if clip:
                lower = self.model.lowerPositionLimit[q_idx]
                upper = self.model.upperPositionLimit[q_idx]
                current_q[q_idx] = np.clip(position, lower, upper)
            else:
                current_q[q_idx] = position
        configuration.update(current_q)

    def get_joint_positions(self, joint_names: Sequence[str], state=False) -> np.ndarray:
        """Get joint positions of given joints.

        Args:
            joint_names (Sequence[str]): list of joint names
            state (bool, optional): If True, get joint positions from the state configuration. Defaults to False.

        Returns:
            q (NDArray): joint positions
        """
        if state:
            configuration = self.current_configuration
        else:
            configuration = self.configuration
        return np.array([configuration.q[self.get_idx_q_from_name(name)] for name in joint_names])

    def set_joint_limits(self, joint_name: str, lower: float, upper: float):
        """Set joint upper and lower limits. Note this does not update the robot data.

        Args:
            joint_name (str): Name of the joint.
            lower (float): Lower limit.
            upper (float): Upper limit.
        """
        if joint_name in self.config.joints_to_lock:
            logger.trace(f"Joint {joint_name} is locked, cannot set limits")
            return
        if joint_name not in self.model.names:
            logger.warning(f"Joint {joint_name} not found in robot model")
            return
        self.model.lowerPositionLimit[self.get_idx_q_from_name(joint_name)] = lower
        self.model.upperPositionLimit[self.get_idx_q_from_name(joint_name)] = upper

    def get_joint_limits(self, joint_names: list[str]) -> tuple[np.ndarray, np.ndarray]:
        """Get joint upper and lower limits.

        Args:
            joint_names (list[str]): list of joint names

        Returns:
            tuple[np.ndarray, np.ndarray]: lower and upper limits
        """
        lowers = []
        uppers = []
        for joint_name in joint_names:
            if joint_name in self.config.joints_to_lock:
                lowers.append(0.0)
                uppers.append(0.0)
                continue
            if joint_name not in self.model.names:
                logger.warning(f"Joint {joint_name} not found in robot model")
                lowers.append(0.0)
                uppers.append(0.0)
                continue
            lowers.append(self.model.lowerPositionLimit[self.get_idx_q_from_name(joint_name)])
            uppers.append(self.model.upperPositionLimit[self.get_idx_q_from_name(joint_name)])
        return np.array(lowers), np.array(uppers)

    def set_velocity_limit(self, joint_name: str, limit: float):
        """Set joint velocity limit. Note this does not update the robot data.

        Args:
            joint_name (str): Name of the joint.
            limit (float): Velocity limit.
        """
        if joint_name in self.config.joints_to_lock:
            logger.trace(f"Joint {joint_name} is locked, cannot set limits")
            return
        if joint_name not in self.model.names:
            logger.warning(f"Joint {joint_name} not found in robot model")
            return
        self.model.velocityLimit[self.get_idx_v_from_name(joint_name)] = limit

    def get_velocity_limit(self, joint_name: str) -> float:
        if joint_name not in self.model.names:
            logger.warning(f"Joint {joint_name} not found in robot model")
            return np.inf
        return self.model.velocityLimit[self.get_idx_v_from_name(joint_name)]

    def frame_placement(self, q: np.ndarray, frame_name: str, source_frame: str | None = None) -> pin.SE3:
        """Get the placement of a frame in the robot model.

        Args:
            q (np.ndarray): Joint positions.
            frame_name (str): Name of the frame.
            source_frame (str | None, optional): Name of the source frame. Defaults to None. If None, the default world frame is used.
        """
        if len(q) == self.num_joints:
            q = self.q_real2pink(q)
        elif len(q) != self.model.nq:
            raise ValueError(
                f"Invalid q vector length: {len(q)}, model num joints: {self.model.nq}; robot num joints: {self.num_joints}"
            )

        frame_idx = self.model.getFrameId(frame_name)
        frame_transform = self._frame_placement(q, frame_idx)
        if source_frame is None:
            return frame_transform
        source_frame_idx = self.model.getFrameId(source_frame)
        source_frame_transform = self._frame_placement(q, source_frame_idx)
        return source_frame_transform.inverse() * frame_transform

    def get_transforms(self, frame_names: Sequence[str]) -> list[pin.SE3]:
        return [self.configuration.get_transform_frame_to_world(frame_name).np for frame_name in frame_names]

    def update_display(self):
        """Display the current configuration in the visualizer."""
        if self.viz:
            self.viz.display(self.q_dict)

    def make_visualizer(self):
        if self.config.visualize:
            from retargeting.visualizer import ViserVisualizer

            server = viser.ViserServer(label="retargeting")

            self.viz = ViserVisualizer(
                server=server,
                urdf_path=(PACKAGE_PATH / self.urdf_name).with_suffix(".urdf"),
                load_meshes=True,
                load_collision_meshes=False,
            )

            self.viz.set_limits(self.config.joint_names, *self.get_joint_limits(self.config.joint_names))

            for frame_name in self.config.displayed_frames:
                self.viz.show_frame(frame_name)

            # self.viz.create_joint_sliders(self.viz.viser_urdf)
            self.viz.create_targets()

            self.viz.display(self.q_dict)
            self.viz.display_state(self.q_dict)

            logger.info("Visualizer created")

    # --- from pinocchio ---

    @property
    def nq(self):
        return self.model.nq

    @property
    def nv(self):
        return self.model.nv

    def com(self, q=None, v=None, a=None):
        if q is None:
            pin.centerOfMass(self.model, self.data)
            return self.data.com[0]
        if v is not None:
            if a is None:
                pin.centerOfMass(self.model, self.data, q, v)
                return self.data.com[0], self.data.vcom[0]
            pin.centerOfMass(self.model, self.data, q, v, a)
            return self.data.com[0], self.data.vcom[0], self.data.acom[0]
        return pin.centerOfMass(self.model, self.data, q)

    def vcom(self, q, v):
        pin.centerOfMass(self.model, self.data, q, v)
        return self.data.vcom[0]

    def acom(self, q, v, a):
        pin.centerOfMass(self.model, self.data, q, v, a)
        return self.data.acom[0]

    def centroidal_momentum(self, q, v):
        return pin.computeCentroidalMomentum(self.model, self.data, q, v)

    def centroidal_map(self, q):
        """
        Computes the centroidal momentum matrix which maps from the joint velocity
        vector to the centroidal momentum expressed around the center of mass.
        """
        return pin.computeCentroidalMap(self.model, self.data, q)

    def centroidal(self, q, v):
        """
        Computes all the quantities related to the centroidal dynamics (hg, Ag and Ig),
        corresponding to the centroidal momentum, the centroidal map and the centroidal
        rigid inertia.
        """
        pin.ccrba(self.model, self.data, q, v)
        return (self.data.hg, self.data.Ag, self.data.Ig)

    def centroidal_momentum_variation(self, q, v, a):
        return pin.computeCentroidalMomentumTimeVariation(self.model, self.data, q, v, a)

    def jacobian_center_of_mass(self, q):
        return pin.jacobianCenterOfMass(self.model, self.data, q)

    def mass(self, q):
        return pin.crba(self.model, self.data, q)

    def nle(self, q, v):
        return pin.nonLinearEffects(self.model, self.data, q, v)

    def gravity(self, q):
        return pin.computeGeneralizedGravity(self.model, self.data, q)

    def forward_kinematics(self, q, v=None, a=None):
        if v is not None:
            if a is not None:
                pin.forwardKinematics(self.model, self.data, q, v, a)
            else:
                pin.forwardKinematics(self.model, self.data, q, v)
        else:
            pin.forwardKinematics(self.model, self.data, q)

    def placement(self, q, index, update_kinematics=True):
        if update_kinematics:
            pin.forwardKinematics(self.model, self.data, q)
        return self.data.oMi[index]

    def velocity(
        self,
        q,
        v,
        index,
        update_kinematics=True,
        reference_frame=pin.ReferenceFrame.LOCAL,
    ):
        if update_kinematics:
            pin.forwardKinematics(self.model, self.data, q, v)
        return pin.getVelocity(self.model, self.data, index, reference_frame)

    def acceleration(
        self,
        q,
        v,
        a,
        index,
        update_kinematics=True,
        reference_frame=pin.ReferenceFrame.LOCAL,
    ):
        if update_kinematics:
            pin.forwardKinematics(self.model, self.data, q, v, a)
        return pin.getAcceleration(self.model, self.data, index, reference_frame)

    def classical_acceleration(
        self,
        q,
        v,
        a,
        index,
        update_kinematics=True,
        reference_frame=pin.ReferenceFrame.LOCAL,
    ):
        if update_kinematics:
            pin.forwardKinematics(self.model, self.data, q, v, a)
        return pin.getClassicalAcceleration(self.model, self.data, index, reference_frame)

    def _frame_placement(self, q, index, update_kinematics=True):
        if update_kinematics:
            pin.forwardKinematics(self.model, self.data, q)
        return pin.updateFramePlacement(self.model, self.data, index)

    def frame_velocity(
        self,
        q,
        v,
        index,
        update_kinematics=True,
        reference_frame=pin.ReferenceFrame.LOCAL,
    ):
        if update_kinematics:
            pin.forwardKinematics(self.model, self.data, q, v)
        return pin.getFrameVelocity(self.model, self.data, index, reference_frame)

    def frame_acceleration(
        self,
        q,
        v,
        a,
        index,
        update_kinematics=True,
        reference_frame=pin.ReferenceFrame.LOCAL,
    ):
        if update_kinematics:
            pin.forwardKinematics(self.model, self.data, q, v, a)
        return pin.getFrameAcceleration(self.model, self.data, index, reference_frame)

    def frame_classical_acceleration(
        self,
        q,
        v,
        a,
        index,
        update_kinematics=True,
        reference_frame=pin.ReferenceFrame.LOCAL,
    ):
        if update_kinematics:
            pin.forwardKinematics(self.model, self.data, q, v, a)
        return pin.getFrameClassicalAcceleration(self.model, self.data, index, reference_frame)

    def compute_joint_jacobian(self, q, index):
        return pin.computeJointJacobian(self.model, self.data, q, index)

    def get_joint_jacobian(self, index, rf_frame=pin.ReferenceFrame.LOCAL):
        return pin.getJointJacobian(self.model, self.data, index, rf_frame)

    def compute_joint_jacobians(self, q):
        return pin.computeJointJacobians(self.model, self.data, q)

    def update_geometry_placements(self, q=None, visual=False):
        if visual:
            geom_model = self.visual_model
            geom_data = self.visual_data
        else:
            geom_model = self.collision_model
            geom_data = self.collision_data

        if q is not None:
            pin.updateGeometryPlacements(self.model, self.data, geom_model, geom_data, q)
        else:
            pin.updateGeometryPlacements(self.model, self.data, geom_model, geom_data)

    def frames_forward_kinematics(self, q):
        pin.framesForwardKinematics(self.model, self.data, q)

    def get_frame_jacobian(self, frame_id, rf_frame=pin.ReferenceFrame.LOCAL):
        """
        It computes the Jacobian of frame given by its id (frame_id) either expressed in
        the local coordinate frame or in the world coordinate frame.
        """
        return pin.getFrameJacobian(self.model, self.data, frame_id, rf_frame)

    def compute_frame_jacobian(self, q, frame_id):
        """
        Similar to getFrameJacobian but does not need pin.computeJointJacobians and
        pin.updateFramePlacements to update internal value of self.data related to
        frames.
        """
        return pin.computeFrameJacobian(self.model, self.data, q, frame_id)

    def rebuild_data(self):
        """Re-build the data objects. Needed if the models were modified.
        Warning: this will delete any information stored in all data objects."""
        data, collision_data, visual_data = createDatas(self.model, self.collision_model, self.visual_model)
        # if self.viz is not None:
        #     if (
        #         id(self.data) == id(self.viz.data)
        #         and id(self.collision_data) == id(self.viz.collision_data)
        #         and id(self.visual_data) == id(self.viz.visual_data)
        #     ):
        #         self.viz.data = data
        #         self.viz.collision_data = collision_data
        #         self.viz.visual_data = visual_data
        #     else:
        #         self.viz.rebuild_data()
        self.data = data
        self.collision_data = collision_data
        self.visual_data = visual_data
