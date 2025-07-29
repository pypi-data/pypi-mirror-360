from typing import Callable, Optional, Type

from nqs_sdk.core.protocol_registry.registry import ProtocolRegistry
from nqs_sdk.interfaces import ProtocolFactory


def protocol_factory(
    namespace: Optional[str] = None, name: Optional[str] = None, version: Optional[str] = None, **metadata: str
) -> Callable[[Type[ProtocolFactory]], Type[ProtocolFactory]]:
    return ProtocolRegistry.register(namespace, name, version, metadata)
