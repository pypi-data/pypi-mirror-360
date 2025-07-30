from pathlib import Path
from typing import assert_never

from fourier_robot_descriptions.fourier import REPOSITORY_PATH


def parse_urdf_name(
    description_name: str | Path | tuple[str, str, str] | tuple[str, str],
):
    if isinstance(description_name, tuple):
        if len(description_name) == 2:
            new_description_name = description_name[0] + "_" + description_name[1]
            URDF_PATH = REPOSITORY_PATH / "urdf" / f"{new_description_name}.urdf"
            PACKAGE_PATH = REPOSITORY_PATH / "urdf"
        elif len(description_name) == 3:
            base, left, right = description_name

            if left.replace("_left", "") == right.replace("_right", ""):
                try:
                    new_description_name = base + "_" + left.replace("_left", "")
                    URDF_PATH = REPOSITORY_PATH / "urdf" / f"{new_description_name}.urdf"
                    PACKAGE_PATH = REPOSITORY_PATH / "urdf"
                    if not URDF_PATH.exists():
                        raise FileNotFoundError(f"URDF not found at {URDF_PATH}")
                except FileNotFoundError:
                    from fourier_robot_descriptions.generate import generate_urdf

                    URDF_PATH = generate_urdf(base, left, right)
                    if URDF_PATH is None:
                        raise ValueError(f"Failed to generate URDF for {description_name}") from None
                    PACKAGE_PATH = URDF_PATH.parent
                except Exception as e:
                    raise ValueError(f"Failed to generate URDF for {description_name}") from e
        else:
            raise ValueError(f"Invalid description name: {description_name}")
    elif isinstance(description_name, Path):
        URDF_PATH = description_name
        PACKAGE_PATH = description_name.parent
    elif isinstance(description_name, str):
        URDF_PATH = REPOSITORY_PATH / "urdf" / f"{description_name}.urdf"
        PACKAGE_PATH = REPOSITORY_PATH / "urdf"
    else:
        raise ValueError(f"Invalid description name: {description_name}")

    return URDF_PATH, PACKAGE_PATH
