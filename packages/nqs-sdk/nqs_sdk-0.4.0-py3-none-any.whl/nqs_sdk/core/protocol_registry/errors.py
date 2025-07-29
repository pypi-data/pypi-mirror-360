class ProtocolRegistryError(Exception):
    pass


class ProtocolNotFoundError(ProtocolRegistryError):
    pass


class InvalidProtocolFactoryError(ProtocolRegistryError):
    pass


class DuplicateProtocolError(ProtocolRegistryError):
    pass
