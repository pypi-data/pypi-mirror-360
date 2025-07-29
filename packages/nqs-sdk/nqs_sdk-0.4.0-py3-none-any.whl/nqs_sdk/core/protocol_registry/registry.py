from typing import Any, Callable, Dict, Optional, Type

from nqs_pycore import implementations

from nqs_sdk.interfaces import ProtocolFactory

from .errors import DuplicateProtocolError, InvalidProtocolFactoryError, ProtocolNotFoundError
from .protocol_id import ProtocolID


class ProtocolRegistry:
    """
    Global registry for protocol factory classes

    This singleton-like class maintains a registry of all available protocol factories,
    enabling dynamic discovery and instantiation of protocol implementations. It supports
    both built-in (native) protocols and user-defined custom protocols

    The registry uses a decorator pattern for registration and falls back to the
    rust implementation for native protocols not explicitly registered

    Class Attributes:
        _factories: Dictionary mapping protocol IDs to their factory classes
    """

    _factories: Dict[ProtocolID, Type[ProtocolFactory]] = {}
    _default_namespace = "nqs_sdk"
    _metadata: Dict[ProtocolID, Dict[str, str]] = {}

    @classmethod
    def register(
        cls,
        namespace: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Callable[[Type[ProtocolFactory]], Type[ProtocolFactory]]:
        """
        Decorator for registering protocol factory classes

        This decorator registers a protocol factory class with the registry,
        making it available for use in simulations. If no protocol_id is provided,
        the factory's id() method is called to determine the identifier

        Args:
            protocol_id: Optional explicit identifier for the protocol.
                        If None, uses the factory's id() method

        Returns:
            Decorator function that registers the factory class

        Example:
            >>> @ProtocolRegistry.register("my_custom_protocol")
            ... class MyCustomProtocolFactory(ProtocolFactory):
            ...     def id(self) -> str:
            ...         return "my_custom_protocol"
            ...
            ...     def build(self, ...):
            ...         # Implementation
        """

        def decorator(factory_class: Type[ProtocolFactory]) -> Type[ProtocolFactory]:
            tmp_factory = factory_class()

            protocol_name = name if name is not None else tmp_factory.id()
            protocol_namespace = namespace if namespace is not None else cls._default_namespace

            id = ProtocolID(protocol_namespace, protocol_name, version)

            cls._validate_factory(factory_class, id)
            cls._factories[id] = factory_class

            if metadata:
                cls._metadata[id] = metadata
            else:
                cls._metadata[id] = {"name": str(id), "description": factory_class.__doc__ or "No description provided"}

            return factory_class

        return decorator

    @classmethod
    def get_factory(cls, protocol_id: str) -> ProtocolFactory:
        """
        Retrieve a protocol factory by its string identifier

        This method first checks the custom registry for user-defined protocols,
        then falls back to native implementations from the rust layer

        Args:
            protocol_id: Unique identifier for the protocol

        Returns:
            ProtocolFactory instance for the specified protocol

        Raises:
            ProtocolNotFoundError: If the protocol_id is not found in either custom or native registries

        Example:
            >>> factory = ProtocolRegistry.get_factory("uniswap_v3")
            >>> protocols, generators = factory.build(...)
        """
        try:
            id = ProtocolID.from_string(protocol_id)
            if id in cls._factories:
                factory_class = cls._factories[id]
                factory_from_class: ProtocolFactory = factory_class()
                return factory_from_class
        except Exception:
            pass

        default_id = ProtocolID(cls._default_namespace, protocol_id)
        if default_id in cls._factories:
            factory_class = cls._factories[default_id]
            factory_from_class = factory_class()
            return factory_from_class

        for id, factory_class in cls._factories.items():
            if id.name == protocol_id:
                factory_from_class = factory_class()
                return factory_from_class

        factory_name = f"{protocol_id}_factory"
        if hasattr(implementations, factory_name):
            factory_func = getattr(implementations, factory_name)
            factory_from_func: ProtocolFactory = factory_func()
            return factory_from_func

        available_protocols = list(cls.get_available_protocols().keys())
        raise ProtocolNotFoundError(
            f"Protocol '{protocol_id}' not found. " f"Available protocols are: {available_protocols}"
        )

    @classmethod
    def get_factory_by_id(cls, id: ProtocolID) -> ProtocolFactory:
        """
        Retrieve a protocol factory by its identifier

        Same as get_factory but with a ProtocolID identifier this time

        Args:
            id: Unique identifier for the protocol

        Returns:
            ProtocolFactory instance for the specified protocol

        Raises:
            ProtocolNotFoundError: If the protocol_id is not found in either custom or native registries
        """
        if id in cls._factories:
            factory_class = cls._factories[id]
            factory_from_class: ProtocolFactory = factory_class()
            return factory_from_class
        raise ProtocolNotFoundError(f"No factory registered for id: {id}")

    @classmethod
    def _validate_factory(cls, factory_class: Type[ProtocolFactory], protocol_id: ProtocolID) -> None:
        required_methods = ["id", "build"]
        for method in required_methods:
            if not hasattr(factory_class, method) or not callable(getattr(factory_class, method)):
                raise InvalidProtocolFactoryError(f"Factory class must implement method: {method}")

        if protocol_id in cls._factories:
            raise DuplicateProtocolError(f"Protocol ID '{protocol_id}' is already registered")

    @classmethod
    def get_available_protocols(cls) -> Dict[str, str]:
        """
        Get all available protocols and their sources

        Returns:
            Dictionary mapping protocol IDs to their implementation source:
            - "custom": Registered via Python decorator
            - "native": Available in rust implementation

        The method gives priority to custom implementations when the same
        protocol_id exists in both registries

        Example:
            >>> protocols = ProtocolRegistry.get_available_protocols()
            >>> for pid, source in protocols.items():
            ...     print(f"{pid}: {source}")
        """
        result = {}

        for id in cls._factories:
            result[str(id)] = id.namespace

        native_protocols = [
            name.replace("_factory", "")
            for name in dir(implementations)
            if callable(getattr(implementations, name)) and name.endswith("_factory")
        ]

        for protocol_id in native_protocols:
            if protocol_id not in result:
                result[protocol_id] = "native"

        return result

    @classmethod
    def set_default_namespace(cls, namespace: str) -> None:
        """
        Set the default namespace for protocol resolution

        This method configures a global default namespace that will be used
        when resolving protocol identifiers that don't explicitly specify
        a namespace. This is particularly useful for applications that primarily
        work with protocols from a specific version or source

        Args:
            namespace: The default namespace identifier (e.g., "v2", "mainnet", "testing")

        Example:
            >>> ProtocolRegistry.set_default_namespace("v2")
            >>> # Now "uniswap" will resolve to "v2.uniswap" if not found directly
            >>> factory = ProtocolRegistry.get_factory("uniswap")
            >>>
            >>> # Clear default namespace
            >>> ProtocolRegistry.set_default_namespace("")

        Note:
            This setting is global and affects all subsequent protocol lookups.
            Setting an empty string disables the default namespace behavior.
            The namespace only applies when a protocol is not found with its
            original identifier
        """
        cls._default_namespace = namespace

    @classmethod
    def get_protocol_metadata(cls, protocol_id: Optional[ProtocolID] = None) -> Any:
        """
        Retrieve metadata for a specific protocol or all protocols

        This method provides access to additional information about registered
        protocols beyond their factory classes. Metadata can include version
        information, configuration schemas, dependencies, or other descriptive data

        Args:
            protocol_id: Optional ProtocolID to get metadata for a specific protocol.
                        If None, returns metadata for all registered protocols.

        Returns:
            If protocol_id is provided: Metadata object for the specific protocol
            If protocol_id is None: Dictionary mapping all ProtocolIDs to their metadata

        Raises:
            ProtocolNotFoundError: If the specified protocol_id is not found in the registry

        Example:
            >>> # Get metadata for a specific protocol
            >>> metadata = ProtocolRegistry.get_protocol_metadata(ProtocolID("v3", "uniswap"))
            >>> print(metadata.version, metadata.description)
            >>>
            >>> # Get all metadata
            >>> all_metadata = ProtocolRegistry.get_protocol_metadata()
            >>> for protocol_id, metadata in all_metadata.items():
            ...     print(f"{protocol_id}: {metadata.version}")

        Note:
            Metadata is optional - not all protocols may have associated metadata.
            The structure of metadata objects depends on how protocols were registered.
        """
        if protocol_id:
            if protocol_id in cls._metadata:
                return cls._metadata[protocol_id]
            raise ProtocolNotFoundError(f"Protocol '{protocol_id}' not found")

        return cls._metadata

    @classmethod
    def unregister(cls, protocol_id: ProtocolID) -> bool:
        """
        Remove a protocol from the registry

        This method removes both the factory class and any associated metadata
        for the specified protocol from the registry. This is useful for dynamic
        protocol management, testing scenarios, or when protocols need to be
        replaced at runtime

        Args:
            protocol_id: ProtocolID of the protocol to remove from the registry

        Returns:
            True if the protocol was successfully unregistered
            False if the protocol was not found in the registry

        Example:
            >>> # Register a custom protocol
            >>> @ProtocolRegistry.register()
            >>> class TestProtocolFactory(ProtocolFactory):
            ...     def id(self) -> str:
            ...         return "test.protocol"
            >>>
            >>> # Later, remove it
            >>> success = ProtocolRegistry.unregister(ProtocolID("test", "protocol"))
            >>> assert success == True
            >>>
            >>> # Attempt to remove non-existent protocol
            >>> success = ProtocolRegistry.unregister(ProtocolID("missing", "protocol"))
            >>> assert success == False

        Note:
            Unregistering a protocol does not affect existing ProtocolManager
            instances that were created before the unregistration. It only
            prevents new instances from being created.

            This operation also removes any metadata associated with the protocol.
        """
        if protocol_id in cls._factories:
            del cls._factories[protocol_id]
            if protocol_id in cls._metadata:
                del cls._metadata[protocol_id]
            return True
        return False
