"""GR1T2 description."""

from os import path as _path
from pathlib import Path

REPOSITORY_PATH: Path = Path(__file__).parent / "assets"

PACKAGE_PATH: Path = REPOSITORY_PATH / "urdf"

BASE_PACKAGE_PATH: Path = REPOSITORY_PATH / "base_urdf"

# URDF_PATH: str = _path.join(PACKAGE_PATH, "{}.urdf")
