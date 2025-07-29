from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

import numpy as np
import numpy.typing as npt
from nqs_pycore import quantlib

from nqs_sdk import BlockNumberOrTimestamp


class IDataLoader(ABC):
    def __init__(self) -> None:
        self._source: Any | None = None
        self._alchemy_api_key: str | None = None
        self._etherscan_api_key: str | None = None
        self._alchemy_url: str | None = None
        self._etherscan_url: str | None = None

    def is_source_configured(self) -> bool:
        return self._source is not None

    def source(self) -> Optional[Any]:
        return self._source

    def alchemy_api_key(self) -> Optional[str]:
        return self._alchemy_api_key

    def etherscan_api_key(self) -> Optional[str]:
        return self._etherscan_api_key

    def alchemy_url(self) -> Optional[str]:
        return self._alchemy_url

    def etherscan_url(self) -> Optional[str]:
        return self._etherscan_url

    @abstractmethod
    def update(
        self,
        *,  # keyword argument only
        source: Optional[Any] = None,
        alchemy_api_key: Optional[str] = None,
        etherscan_api_key: Optional[str] = None,
        alchemy_url: Optional[str] = None,
        etherscan_url: Optional[str] = None,
    ) -> None:
        pass

    @abstractmethod
    def all_token_info(self, blockchain: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def token_info(self, blockchain: str, token: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_token_address(self, blockchain: str, token: str) -> str:
        pass

    @abstractmethod
    def get_pool_info(self, token0: str, token1: str, token0_address: str, token1_address: str) -> Dict:
        pass

    @abstractmethod
    def get_spot_values(
        self,
        pool_address: str,
        begin: quantlib.BlockNumberOrTimestamp,
        end: Optional[quantlib.BlockNumberOrTimestamp],
        limit: Optional[int],
    ) -> tuple[npt.NDArray[np.int64], npt.NDArray[np.float64]]:
        pass

    @abstractmethod
    def get_spot_values_at_timestamps(self, pool_address: str, timestamps: list[int]) -> npt.NDArray[np.float64]:
        pass

    @abstractmethod
    def get_timestamps_from_interval(self, timestamp_start: int, timestamp_end: int) -> list:
        pass

    @abstractmethod
    def compound_v2_market_list(self) -> Dict:
        pass

    @abstractmethod
    def compound_v2_globals(
        self,
        begin_block: Optional[int] = None,
        end_block: Optional[int] = None,
        begin: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> Dict:
        pass

    @abstractmethod
    def compound_v2_market_snapshot(
        self, market: str, exclusive_upper_bound: bool, at_block: Optional[int] = None, at: Optional[datetime] = None
    ) -> Dict:
        pass

    @abstractmethod
    def compound_v2_market_borrow_index(
        self, market: str, event_type: str, at_block: Optional[int] = None, at: Optional[datetime] = None
    ) -> Dict:
        pass

    @abstractmethod
    def uniswap_v3_pool_exchange_rate(
        self,
        contract: str,
        begin: quantlib.BlockNumberOrTimestamp,
        end: Optional[quantlib.BlockNumberOrTimestamp],
        limit: Optional[int],
        offset: Optional[int],
    ) -> Dict:
        pass

    @abstractmethod
    def uniswap_v3_pool_slot0_data(self, pool_address: str, block_number: str) -> Dict:
        pass

    @abstractmethod
    def uniswap_v3_pool_info(self, contract_address: str) -> Dict:
        pass

    @abstractmethod
    def blocks_from_interval(
        self, blockchain: str, begin: BlockNumberOrTimestamp, end: Optional[BlockNumberOrTimestamp] = None
    ) -> Dict:
        pass

    @abstractmethod
    def uniswap_v3_pool_liquidity_positions(self, contract_address: str, timestamp: datetime) -> Dict:
        pass

    @abstractmethod
    def compound_v2_market_calls(
        self,
        markets: list[str],
        begin: BlockNumberOrTimestamp,
        end: Optional[BlockNumberOrTimestamp] = None,
    ) -> Dict:
        pass

    @abstractmethod
    def uniswap_v3_pool_calls(
        self,
        contract: str,
        begin: BlockNumberOrTimestamp,
        end: Optional[BlockNumberOrTimestamp] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict:
        pass
