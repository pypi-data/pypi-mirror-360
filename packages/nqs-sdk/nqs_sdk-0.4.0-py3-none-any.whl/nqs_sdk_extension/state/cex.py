from dataclasses import dataclass

from nqs_sdk_extension.state import ABCProtocolState


@dataclass(kw_only=True)
class StateCEX(ABCProtocolState):
    # no specific fields for the moment
    numeraire: str
    pass
