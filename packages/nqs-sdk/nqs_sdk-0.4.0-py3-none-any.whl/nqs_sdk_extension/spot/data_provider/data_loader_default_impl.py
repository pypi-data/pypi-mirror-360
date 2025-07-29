from datetime import datetime
from typing import Any, Dict, Optional

import numpy as np
import numpy.typing as npt
from nqs_pycore import quantlib

from nqs_sdk import BlockNumberOrTimestamp
from nqs_sdk_extension.utils import forward_flat_interpolator

from .data_loader_interface import IDataLoader


class QuantlibDataLoader(IDataLoader):
    def __init__(self, config_path: Optional[str] = None):
        super().__init__()
        self._source: quantlib.QuantlibDataProvider = quantlib.QuantlibDataProvider(config_path)

    def update(
        self,
        *,
        source: Optional[str] = None,
        alchemy_api_key: Optional[str] = None,
        etherscan_api_key: Optional[str] = None,
        alchemy_url: Optional[str] = None,
        etherscan_url: Optional[str] = None,
    ) -> None:
        if source is not None:
            self._source = quantlib.QuantlibDataProvider(source)
        self._alchemy_api_key = alchemy_api_key if alchemy_api_key is not None else self._alchemy_api_key
        self._etherscan_api_key = etherscan_api_key if etherscan_api_key is not None else self._etherscan_api_key
        self._alchemy_url = alchemy_url if alchemy_url is not None else self._alchemy_url
        self._etherscan_url = etherscan_url if etherscan_url is not None else self._etherscan_url

    def get_token_address(self, blockchain: str, token: str) -> str:
        """
        Retrieve a token address
        :param blockchain: the blockchain where the token symbol lives
        :param token: the token of which the address will be retrieved
        :return:
        """
        assert self._source is not None, "DataLoader not configured"
        # todo - fix this after ok in DTQ - this is a quickfix for compound backtest
        if token == "SAI":
            return "0x89d24a6b4ccb1b6faa2625fe562bdd9a23260359"
        if token == "BAT":
            return "0x0d8775f648430679a709e98d2b0cb6250d2887ef"
        if token == "UNI":
            return "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984".lower()
        token_info = self._source.token_info(blockchain, token).to_dict()
        if not token_info:
            raise ValueError(f"Unknown token: {token}")
        return str(token_info["address"])

    def get_pool_info(self, token0: str, token1: str, token0_address: str, token1_address: str) -> Dict:
        """
        Gets the pool info for the spot pair
        :return: the dictionary with the pool infos
        """
        assert self._source is not None, "DataLoader not configured"
        pools = self._source.uniswap_v3_token_pair_pools(token0, token1)
        pools = pools.move_as_dict()

        if len(pools["pool_address"]) == 0:
            raise ValueError(f"No historical data found for pool {token0}/{token1}.")

        idx = 0
        max_tvl = 0.0
        for i in range(len(pools["pool_address"])):
            if pools["total_value_locked_usd"][i] > max_tvl:
                max_tvl = pools["total_value_locked_usd"][i]
                idx = i

        if pools["token0_address"][idx] == token0_address and pools["token1_address"][idx] == token1_address:
            spot = (token0, token1)
        elif pools["token0_address"][idx] == token1_address and pools["token1_address"][idx] == token0_address:
            spot = (token1, token0)
        else:
            raise ValueError(f"Invalid pool data retrieved for the following pair: {token0}/{token1}")

        infos_pool = self._source.uniswap_v3_pool_info(pools["pool_address"][idx]).to_dict()
        return {
            "spot": spot,
            "pool_address": pools["pool_address"][idx],
            "fee_tier": float(infos_pool["fee_tier"].scaleb(-2)),
            "TVL": pools["total_value_locked_usd"][idx],
            "protocol_name": "amm_uniswap_v3",
            "calibration_param": "max_tvl",
        }

    def get_spot_values(
        self,
        pool_address: str,
        begin: quantlib.BlockNumberOrTimestamp,
        end: Optional[quantlib.BlockNumberOrTimestamp] = None,
        limit: Optional[int] = None,
    ) -> tuple[npt.NDArray[np.int64], npt.NDArray[np.float64]]:
        """
        Retrieve the exchange rate values of a pool between two timestamps or until a limit of values is reached
        """
        assert self._source is not None, "DataLoader not configured"
        result = self._source.uniswap_v3_pool_exchange_rate(
            pool_address,
            begin=begin,
            end=end,
            limit=limit,
        )
        dic_result = result.move_as_dict()
        return dic_result["timestamp"], dic_result["exchange_rate"]

    def get_spot_values_at_timestamps(self, pool_address: str, timestamps: list[int]) -> npt.NDArray[np.float64]:
        """
        Get the spot values at a given set of dates
        :param timestamps: the set of timestamps on which to query the spot prices
        :param pool_address: the pool address
        :return:
        """
        assert self._source is not None, "DataLoader not configured"
        begin, end = timestamps[0], timestamps[-1]

        start_time = BlockNumberOrTimestamp.timestamp(begin)
        end_time = BlockNumberOrTimestamp.timestamp(end)

        result = self._source.uniswap_v3_pool_exchange_rate(
            pool_address,
            begin=start_time,
            end=end_time,
            limit=None,
        )
        dic_result = result.move_as_dict()
        result_timestamps = dic_result["timestamp"]
        result_exchange_rates = list(dic_result["exchange_rate"])
        close_prices = forward_flat_interpolator(result_timestamps, result_exchange_rates, timestamps)
        return np.array(close_prices)

    def get_timestamps_from_interval(self, timestamp_start: int, timestamp_end: int) -> list[int] | Any:
        """
        uses the corresponding pyquantlib function to return all the blocks between begin and end
        :param timestamp_start:
        :param timestamp_end:
        :return:
        """
        start = BlockNumberOrTimestamp.timestamp(timestamp_start)
        end = BlockNumberOrTimestamp.timestamp(timestamp_end)

        result = self._source.blocks_from_interval(
            blockchain="Ethereum",
            begin=start,
            end=end,
        )
        result = result.move_as_dict()
        if len(result["timestamp"]) == 0:
            raise ValueError(f"The list of block timestamps between {timestamp_start} and {timestamp_end} is empty")
        return result["timestamp"]

    def compound_v2_market_list(self) -> Dict:
        result = self._source.compound_v2_market_list()
        return self._ensure_dict(result)

    def all_token_info(self, blockchain: str) -> Dict[str, Any]:
        result = self._source.all_token_info(blockchain)
        return self._ensure_dict(result)

    def token_info(self, blockchain: str, token: str) -> Dict[str, Any]:
        token_info = self._source.token_info(blockchain, token)
        return self._ensure_dict(token_info)

    def compound_v2_globals(
        self,
        begin_block: Optional[int] = None,
        end_block: Optional[int] = None,
        begin: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> Dict:
        result = self._source.compound_v2_globals(begin_block, end_block, begin, end)
        return self._ensure_dict(result)

    def compound_v2_market_snapshot(
        self, market: str, exclusive_upper_bound: bool, at_block: Optional[int] = None, at: Optional[datetime] = None
    ) -> Dict:
        result = self._source.compound_v2_market_snapshot(market, exclusive_upper_bound, at_block, at)
        return self._ensure_dict(result)

    def compound_v2_market_borrow_index(
        self, market: str, event_type: str, at_block: Optional[int] = None, at: Optional[datetime] = None
    ) -> Dict:
        result = self._source.compound_v2_market_borrow_index(market, event_type, at_block, at)
        return self._ensure_dict(result)

    def compound_v2_market_calls(
        self,
        markets: list[str],
        begin: BlockNumberOrTimestamp,
        end: Optional[BlockNumberOrTimestamp] = None,
    ) -> Dict:
        result = self._source.compound_v2_market_calls(markets, begin, end)
        return self._ensure_dict(result)

    def uniswap_v3_pool_exchange_rate(
        self,
        contract: str,
        begin: quantlib.BlockNumberOrTimestamp,
        end: Optional[quantlib.BlockNumberOrTimestamp],
        limit: Optional[int],
        offset: Optional[int],
    ) -> Dict:
        result = self._source.uniswap_v3_pool_exchange_rate(contract, begin, end, limit, offset)
        return self._ensure_dict(result)

    def uniswap_v3_pool_slot0_data(self, pool_address: str, block_number: str) -> Dict:
        result = self._source.uniswap_v3_pool_slot0_data(pool_address, block_number)
        return self._ensure_dict(result)

    def uniswap_v3_pool_info(self, contract_address: str) -> Dict:
        result = self._source.uniswap_v3_pool_info(contract_address)
        return self._ensure_dict(result)

    def blocks_from_interval(
        self, blockchain: str, begin: BlockNumberOrTimestamp, end: Optional[BlockNumberOrTimestamp] = None
    ) -> Dict:
        result = self._source.blocks_from_interval(blockchain, begin, end)
        return self._ensure_dict(result)

    def uniswap_v3_pool_liquidity_positions(self, contract_address: str, timestamp: datetime) -> Dict:
        result = self._source.uniswap_v3_pool_liquidity_positions(contract_address, timestamp)
        return self._ensure_dict(result)

    def uniswap_v3_pool_calls(
        self,
        contract: str,
        begin: BlockNumberOrTimestamp,
        end: Optional[BlockNumberOrTimestamp] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict:
        result = self._source.uniswap_v3_pool_calls(contract, begin, end, limit, offset)
        return self._ensure_dict(result)

    def _ensure_dict(self, result: Any) -> Dict:
        if hasattr(result, "move_as_dict"):
            dict_result: Dict[Any, Any] = result.move_as_dict()
            return dict_result
        dict_result = result.to_dict()
        return dict_result
