import logging
from typing import Any, Optional

from nqs_pycore import TokenMetadata

from nqs_sdk.utils.pickable_generator import NoneGenerator, PickableGenerator
from nqs_sdk_extension.generator.historical.dataquasar.abc_dtq import DTQSoloGenerator
from nqs_sdk_extension.legacy_workaround import USE_LEGACY_QIS
from nqs_sdk_extension.observer import ABCObserver
from nqs_sdk_extension.spot import DataLoader
from nqs_sdk_extension.state import ABCProtocolState
from nqs_sdk_extension.state.erc20 import StateERC20
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction

if USE_LEGACY_QIS:
    from legacy_qis.shared_kernel.message_dispatcher import MessageDispatcher


class DTQERC20Generator(DTQSoloGenerator):
    function_to_query = ["decimals", "symbol", "name"]

    def __init__(
        self,
        id: int,
        name: str,
        token_mapping: Optional[dict[str, str]] = None,
    ):
        super().__init__(id, name)
        if token_mapping is None:
            raise ValueError("Provide a list of token addresses with at least one element...")
        self.token_mapping = token_mapping
        # logger
        self.logger = logging.getLogger("DTQERC20Generator")

    def generate_state_at_block(self, block_number: int) -> StateERC20:
        """
        Generate state only if there is just a single token. Otherwise, should not use the SoloGenerator Parent class
        """
        if not len(self.token_mapping) == 1:
            raise ValueError("Can only generate state for a single token")
        # token_metadata = self._get_token_metadata(list(self.token_mapping.values())[0])

        token_address = list(self.token_mapping.values())[0]
        data = DataLoader.quantlib_source().token_info("Ethereum", token_address)

        if data is None:
            raise ValueError(f"No token data for token: {token_address}...")
        return StateERC20(
            name=data["name"],
            decimals=data["decimals"],
            symbol=data["symbol"],
            address=data["address"],
            id=-1,
            block_number=-1,
            block_timestamp=-1,
        )

    def generate_transactions_at_block(self, block_number: int) -> list[ABCTransaction]:
        return []

    def generate_transactions_between_blocks(
        self, block_number_from: int, block_number_to: int
    ) -> list[ABCTransaction]:
        return []

    if USE_LEGACY_QIS:

        def produce_next_message(self, **kwargs: Any) -> PickableGenerator:
            return NoneGenerator()

    if USE_LEGACY_QIS:

        def set_environment(  # type: ignore[override]
            self, env_protocol_id: str, env_message_dispatcher: MessageDispatcher, env_observer: ABCObserver
        ) -> None:
            return

    def compare_two_states(self, state_left: ABCProtocolState, state_right: ABCProtocolState) -> None:
        return

    def generate_token_metadata(self) -> list[TokenMetadata]:
        token_metadata = [self._get_token_metadata(token_address) for token_address in self.token_mapping.values()]
        for i, input_symbol in enumerate(self.token_mapping.keys()):
            if input_symbol != token_metadata[i].symbol:
                self.logger.warning(
                    f"The user input symbol for the token address {token_metadata[i].address} "
                    f"({input_symbol}), does not correspond to the one fetched from the database "
                    f"({token_metadata[i].symbol}). This could lead to inconsistencies. Please "
                    f"check the input parameters"
                )
        return token_metadata

    # ----------------------------------------
    # Private methods for getting the tokens
    # ----------------------------------------

    def _get_token_metadata(self, token_address: str) -> TokenMetadata:
        data = DataLoader.quantlib_source().token_info("Ethereum", token_address)
        if data is None:
            raise ValueError(f"No token data for token: {token_address}...")
        return TokenMetadata(
            name=data["name"],
            decimals=data["decimals"],
            symbol=data["symbol"],
            # address=data.address,
        )


if __name__ == "__main__":
    import os

    source = os.getenv("QUANTLIB_CONFIG")

    token_mapping = {
        "DAI": "0x6b175474e89094c44da98b954eedeac495271d0f",
        "USDC": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "USDT": "0xdac17f958d2ee523a2206206994597c13d831ec7",
    }

    this_generator = DTQERC20Generator(
        id=-1,
        name="ERC20",
        token_mapping=token_mapping,
    )

    token_metadata = this_generator.generate_token_metadata()

    print(token_metadata)
