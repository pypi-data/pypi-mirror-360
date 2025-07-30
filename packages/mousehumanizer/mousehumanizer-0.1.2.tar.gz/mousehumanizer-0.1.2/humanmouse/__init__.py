import sys
from .linux_controller import LinuxHumanMouseController
from .windows_controller import HumanMouseController

def HumanMouse(*args, **kwargs):
    if 'screen_width' not in kwargs or 'screen_height' not in kwargs:
        raise ValueError("screen_width and screen_height must be provided to HumanMouse")
    if sys.platform.startswith('linux'):
        return LinuxHumanMouseController(*args, **kwargs)
    return HumanMouseController(*args, **kwargs)

__all__ = ['HumanMouse']

from .utilities.human_behavior import *

