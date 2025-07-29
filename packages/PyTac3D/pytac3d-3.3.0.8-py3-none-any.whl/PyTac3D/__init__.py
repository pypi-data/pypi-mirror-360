from .Sensor import Sensor
from .Displayer import Displayer, SensorView
from .Manager import Manager
from .Analyzer import Analyzer
from .Data import DataLoader, DataRecorder

from . import Presets
from . import ErrorMessage

__all__ = ['Sensor',
           'Displayer',
           'SensorView',
           'Manager',
           'Analyzer',
           'DataLoader',
           'DataRecorder',
           'Presets',
           'ErrorMessage',
           ]

print("Welcome to PyTac3D. Please run `pytac3d-demo` in the command line to obtain example programs.")
print("For more information about PyTac3D, please visit https://pypi.org/project/PyTac3D/")
