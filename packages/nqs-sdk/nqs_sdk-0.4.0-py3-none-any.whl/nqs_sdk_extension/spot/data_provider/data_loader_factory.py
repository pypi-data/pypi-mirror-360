from .data_loader_default_impl import QuantlibDataLoader
from .data_loader_interface import IDataLoader


class DataLoader:
    _default_data_loader: IDataLoader = QuantlibDataLoader()

    @classmethod
    def quantlib_source(cls) -> IDataLoader:
        return cls._default_data_loader
