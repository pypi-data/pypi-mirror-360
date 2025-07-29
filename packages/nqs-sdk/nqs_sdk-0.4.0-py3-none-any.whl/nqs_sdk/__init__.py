from . import version
from .core.block_number_or_timestamp import BlockNumberOrTimestamp
from .core.logs import activate_log
from .core.protocol_manager import ProtocolManager
from .core.simulation import Simulation

activate_log()

# Expose version at package level
__version__ = version.__version__

__all__ = [
    "Simulation",
    "ProtocolManager",
    "activate_log",
    "ProtocolRegistry",
    "version",
    "BlockNumberOrTimestamp",
    "__version__",
]
