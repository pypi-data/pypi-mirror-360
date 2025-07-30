from .franka import Franka
from .humanoid import Humanoid
from .xarm7 import XArm7
from .cobot import Cobot

__all__ = ["Franka", "Humanoid", "XArm7", "Cobot"]

ROBOT_CLASS_REGISTORY = {
    "franka": Franka,
    "humanoid": Humanoid,
    "xarm7": XArm7,
    "cobot": Cobot,
}
