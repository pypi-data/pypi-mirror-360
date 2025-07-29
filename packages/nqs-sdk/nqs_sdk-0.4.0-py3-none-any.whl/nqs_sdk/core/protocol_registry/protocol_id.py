from typing import Any, Optional


class ProtocolID:
    def __init__(self, namespace: str, name: str, version: Optional[str] = None):
        self.namespace = namespace
        self.name = name
        self.version = version

    def __str__(self) -> str:
        if self.version:
            return f"{self.namespace}::{self.name}@{self.version}"
        return f"{self.namespace}::{self.name}"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ProtocolID):
            return False
        return self.namespace == other.namespace and self.name == other.name and self.version == other.version

    def __hash__(self) -> int:
        return hash((self.namespace, self.name, self.version))

    @classmethod
    def from_string(cls, identifier: str) -> "ProtocolID":
        if "@" in identifier:
            namespace_name, version = identifier.split("@", 1)
        else:
            namespace_name, version = identifier, None

        if "::" in namespace_name:
            namespace, name = namespace_name.split("::", 1)
        else:
            namespace, name = "default", namespace_name

        return cls(namespace, name, version)
