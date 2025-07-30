from fourier_robot_descriptions.fourier import REPOSITORY_PATH


def list_descriptions():
    """List all available urdfs in the assets/urdf directory."""
    return [p.stem for p in REPOSITORY_PATH.glob("urdf/*.urdf")]
