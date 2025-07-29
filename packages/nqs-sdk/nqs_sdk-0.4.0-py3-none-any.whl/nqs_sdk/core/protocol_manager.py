from typing import Any, Dict

from nqs_pycore import ProtocolFactoryAdapter

from .protocol_registry import ProtocolID, ProtocolRegistry


class ProtocolManager:
    """
    Manager for individual protocol integrations

    This component serves as a facade for protocol-specific factories, handling the
    instantiation and configuration of protocol implementations. Each ProtocolManager
    represents a single protocol type (e.g. Uniswap V3, Compound V2...)

    The manager abstracts away the complexity of protocol factory instantiation
    and provides a unified interface for the Simulation class to work with
    different protocol types

    Attributes:
        protocol_id: Unique identifier for the protocol type
        _factory_instance: Internal factory instance for creating protocol objects
    """

    def __init__(self, protocol_id: str):
        """
        Initialize a protocol manager for the specified protocol type

        Args:
            protocol_id: Identifier for the protocol (e.g., "uniswap_v3", "compound_v2")

        Raises:
            ValueError: If protocol_id is not recognized or supported

        Example:
            >>> uniswap_manager = ProtocolManager("uniswap_v3")
            >>> compound_manager = ProtocolManager("compound_v2")
        """
        self.protocol_id = protocol_id

        self.protocol_identifier = ProtocolID.from_string(protocol_id)

        factory = ProtocolRegistry.get_factory(protocol_id)

        if isinstance(factory, ProtocolFactoryAdapter):
            self._factory_instance = factory
        else:
            self._factory_instance = ProtocolFactoryAdapter(factory)

    def get_factory(self) -> Any:
        """
        Get the protocol factory instance

        Returns the factory object responsible for creating instances of this
        protocol type. The factory handles protocol-specific configuration
        and state initialization

        Returns:
            ProtocolFactoryAdapter wrapping the protocol-specific factory

        Note:
            The factory is wrapped in a ProtocolFactoryAdapter to provide
            a consistent interface across different protocol implementations
        """
        return self._factory_instance

    @classmethod
    def get_available_protocols(cls) -> Dict[str, str]:
        """
        Get a mapping of all available protocol types

        Returns:
            Dictionary mapping protocol IDs to their implementation source:
            - "native": Built-in protocol implementations
            - "custom": User-defined protocol implementations

        Example:
            >>> available = ProtocolManager.get_available_protocols()
            >>> print(available)
            {'uniswap_v3': 'native', 'compound_v2': 'native', 'custom_amm': 'custom'}
        """
        return ProtocolRegistry.get_available_protocols()

    @classmethod
    def from_id(cls, id: ProtocolID) -> "ProtocolManager":
        """
        Create a ProtocolManager from a ProtocolID object

        This class method provides an alternative constructor that accepts a structured
        ProtocolID object instead of a raw string. It's particularly useful when working
        with namespaced protocols or when the protocol identifier is already encapsulated
        in a ProtocolID type

        Args:
            id: ProtocolID object containing the protocol identifier information.
                This is typically a structured identifier that may include namespace,
                version, or other metadata

        Returns:
            New ProtocolManager instance configured for the specified protocol

        Raises:
            ValueError: If the ProtocolID cannot be converted to a valid protocol string
                    or if the resulting protocol is not found in the registry

        Example:
            >>> from nqs_sdk.core.protocol_id import ProtocolID
            >>> protocol_id = ProtocolID(namespace="v2", name="uniswap")
            >>> manager = ProtocolManager.from_id(protocol_id)
            >>> # Equivalent to: ProtocolManager("v2.uniswap")

        Note:
            The ProtocolID is converted to string using str(id), so ensure your
            ProtocolID class has a proper __str__ implementation that returns
            the expected protocol identifier format
        """
        return cls(str(id))

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the ProtocolManager

        Provides a clear, descriptive string showing which protocol this manager
        handles. Useful for logging, debugging, and user-facing messages

        Returns:
            String in the format "ProtocolManager for {protocol_id}"

        Example:
            >>> manager = ProtocolManager("uniswap_v3")
            >>> print(manager)
            "ProtocolManager for uniswap_v3"
            >>>
            >>> manager = ProtocolManager.from_id(ProtocolID("custom", "my_amm"))
            >>> str(manager)
            "ProtocolManager for custom.my_amm"
        """
        return f"ProtocolManager for {self.protocol_id}"

    def __repr__(self) -> str:
        """
        Return a string representation suitable for debugging and development

        This method delegates to __str__ to provide consistent representation
        across different contexts (print, debugger, REPL, etc.). In this case,
        the string representation is sufficient for both user-facing and
        developer-facing contexts

        Returns:
            Same as __str__() - "ProtocolManager for {protocol_id}"

        Example:
            >>> manager = ProtocolManager("compound_v2")
            >>> repr(manager)
            "ProtocolManager for compound_v2"
            >>>
            >>> # In a list or when debugging
            >>> managers = [ProtocolManager("uniswap_v3"), ProtocolManager("compound_v2")]
            >>> managers
            [ProtocolManager for uniswap_v3, ProtocolManager for compound_v2]
        """
        return self.__str__()
