#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 Stéphane Caron
# Copyright 2023 Inria

"""Load a robot description in Pinocchio."""

import os
from importlib import import_module  # type: ignore
from pathlib import Path
from typing import Optional, Union, assert_never

import pinocchio as pin

from fourier_robot_descriptions import list_descriptions
from fourier_robot_descriptions.loaders import parse_urdf_name


def get_package_dirs(package_path: str, repository_path: str, urdf_path: str) -> list[str]:
    """Get package directories

    Args:
        package_path: Path to the package directory.
        repository_path: Path to the repository directory.
        URDF_PATH: Path to the URDF file.

    Returns:
        Package directories.
    """
    return [
        package_path,
        repository_path,
        os.path.dirname(package_path),
        os.path.dirname(repository_path),
        os.path.dirname(urdf_path),
    ]


PinocchioJoint = Union[  # noqa: UP007
    pin.JointModelRX,
    pin.JointModelRY,
    pin.JointModelRZ,
    pin.JointModelPX,
    pin.JointModelPY,
    pin.JointModelPZ,
    pin.JointModelFreeFlyer,
    pin.JointModelSpherical,
    pin.JointModelSphericalZYX,
    pin.JointModelPlanar,
    pin.JointModelTranslation,
]


def load_robot_description(
    description_name: str | tuple[str, str, str] | tuple[str, str] | Path,
    root_joint: PinocchioJoint | None = None,
    **kwargs,
) -> pin.RobotWrapper:
    """Load a robot description in Pinocchio.

    Args:
        description_name: Name of the robot description.
        root_joint (optional): First joint of the kinematic chain, for example
            a free flyer between the floating base of a mobile robot and an
            inertial frame. Defaults to no joint, i.e., a fixed base.
        commit: If specified, check out that commit from the cloned robot
            description repository.

    Returns:
        Robot model for Pinocchio.
    """
    urdf_path, package_path = parse_urdf_name(description_name)
    try:
        robot = pin.RobotWrapper.BuildFromURDF(
            filename=str(urdf_path),
            package_dirs=get_package_dirs(str(package_path), str(package_path.parent), str(urdf_path)),
            root_joint=root_joint,
            **kwargs,
        )
    except Exception as e:
        available_descriptions = list_descriptions()
        raise ValueError(
            f"Failed to load robot description {urdf_path}. Available descriptions: {available_descriptions}: {e}"
        ) from e
    return robot
