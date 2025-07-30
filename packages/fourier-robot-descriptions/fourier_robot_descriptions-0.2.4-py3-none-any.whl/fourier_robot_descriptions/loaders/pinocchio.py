#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 Stéphane Caron
# Copyright 2023 Inria

"""Load a robot description in Pinocchio."""

import os
from importlib import import_module  # type: ignore
from pathlib import Path
from typing import Optional, Union

import pinocchio as pin

from fourier_robot_descriptions import list_descriptions
from fourier_robot_descriptions.fourier import PACKAGE_PATH, REPOSITORY_PATH


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
    description_name: str,
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
    if isinstance(description_name, tuple):
        base, left, right = description_name
        from fourier_robot_descriptions.generate import generate_urdf

        URDF_PATH = generate_urdf(base, left, right)
        if URDF_PATH is None:
            raise ValueError(f"Failed to generate URDF for {description_name}")
        PACKAGE_PATH = URDF_PATH.parent
    elif isinstance(description_name, Path):
        URDF_PATH = str(description_name)
        PACKAGE_PATH = description_name.parent
    else:
        URDF_PATH = str(REPOSITORY_PATH / "urdf" / f"{description_name}.urdf")
        PACKAGE_PATH = REPOSITORY_PATH / "urdf"
    try:
        robot = pin.RobotWrapper.BuildFromURDF(
            filename=URDF_PATH,
            package_dirs=get_package_dirs(str(PACKAGE_PATH), str(REPOSITORY_PATH), str(URDF_PATH)),
            root_joint=root_joint,
            **kwargs,
        )
    except Exception as e:
        available_descriptions = list_descriptions()
        raise ValueError(
            f"Failed to load robot description {description_name}. Available descriptions: {available_descriptions}"
        ) from e
    return robot
