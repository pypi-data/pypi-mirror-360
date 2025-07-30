# src/xstate_statemachine/__init__.py

__version__ = "0.2.3"  # Version bump for this feature

from .factory import create_machine
from .interpreter import Interpreter
from .machine_logic import MachineLogic
from .events import Event
from .models import ActionDefinition
from .plugins import PluginBase, LoggingInspector
from .exceptions import (
    XStateMachineError,
    InvalidConfigError,
    StateNotFoundError,
    ImplementationMissingError,
    ActorSpawningError,
)
from .logic_loader import LogicLoader


# This is the public API of the library.
__all__ = [
    "create_machine",
    "Interpreter",
    "MachineLogic",
    "Event",
    "PluginBase",
    "LoggingInspector",
    "XStateMachineError",
    "InvalidConfigError",
    "StateNotFoundError",
    "ImplementationMissingError",
    "ActorSpawningError",
    "LogicLoader",
    "ActionDefinition",
]
