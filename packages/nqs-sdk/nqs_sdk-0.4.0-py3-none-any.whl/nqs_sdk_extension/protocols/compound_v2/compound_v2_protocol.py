import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from nqs_pycore import (
    MetricName,
    MutSharedState,
    ObservableDescription,
    Parameters,
    RefSharedState,
    SealedParameters,
    SimulationClock,
    TokenMetadata,
    TxRequest,
    Wallet,
)

from nqs_sdk.interfaces.observable import Observable
from nqs_sdk.interfaces.protocol import Protocol
from nqs_sdk.tools import to_decimal_exp
from nqs_sdk_extension.agent.transaction_helper import TransactionHelper
from nqs_sdk_extension.agent.ux_transactions import UXTransaction
from nqs_sdk_extension.observer.metric_info import CompoundMarketMetrics
from nqs_sdk_extension.observer.protocol.compoundv2 import ComptrollerObserver
from nqs_sdk_extension.protocol import Comptroller
from nqs_sdk_extension.protocols.common.wrapped_event import WrappedEvent
from nqs_sdk_extension.spot.spot_oracle import SpotOracle

logger = logging.getLogger(__name__)


class CompoundV2Wrapper(Protocol, Observable):
    def __init__(
        self,
        name: str,
        comptroller: Comptroller,
        numeraire: str,
        tokens_metadata: Dict[str, TokenMetadata],
        enable_default_observables: bool = True,
    ) -> None:
        self.name = name
        self.comptroller = comptroller
        self.tokens_metadata = tokens_metadata
        self.tx_helper = TransactionHelper()
        self.last_timestamp: Optional[int] = None

        # Set observer
        self.observer = ComptrollerObserver(self.comptroller)
        self.observer.set_environment(self.id(), {})
        self.observer.numeraire_decimals = tokens_metadata[numeraire].decimals
        for market_name, market in self.comptroller.markets.items():
            self.observer._markets_observables[market_name].metric_info = CompoundMarketMetrics(
                self.id(), token=market.underlying
            )

    def id(self) -> str:
        return self.name

    def build_tx_payload(self, source: str, sender: str, call: Any) -> TxRequest:
        args = call["args"]
        action_name = call["name"]

        transaction = WrappedEvent(action_name, self.name, self.comptroller, args)

        return TxRequest(self.name, source, sender, transaction)

    def execute_tx(self, clock: SimulationClock, state: MutSharedState, tx: TxRequest) -> None:
        transaction = tx.payload

        spot_oracle = state.py_wrapper_spot_oracle(clock)
        updated_spots = spot_oracle.get_selected_spots(
            self.comptroller.required_spots, int(clock.current_time().timestamp())
        )
        self.comptroller.inject_spot_values(clock.current_time(), updated_spots)

        sender = tx.source.split(".")[0]
        wallet_holdings = state.get_wallet(tx.sender)
        if wallet_holdings is not None:
            # somehow wallet already do scaleb conversion
            holdings_dict = {}
            token_list = wallet_holdings.get_list_tokens()
            for key in token_list:
                holdings_dict[key] = wallet_holdings.get_balance_of_float(key)

            holdings: Dict[str, int] = {key: holdings_dict[key] for key in holdings_dict.keys()}

            converted_tokens_metadata = {
                k.replace("/", "_"): TokenMetadata(
                    name=k.replace("/", "_"), symbol=k.replace("/", "_"), decimals=v.decimals
                )
                for k, v in self.tokens_metadata.items()
            }

            wallet = Wallet(
                agent_name=sender,
                holdings=holdings,
                tokens_metadata=converted_tokens_metadata,
                erc721_tokens=[],
            )
        else:
            wallet = None

        if isinstance(transaction, WrappedEvent):
            print("WRAPPED", transaction)
            mapped_tx = transaction.map_tx()

            ux_tx = UXTransaction(mapped_tx, wallet)
            transaction = self.tx_helper.map_ux_transaction(ux_tx)

        if sender == "dummy":
            transaction.sender_wallet = None
        else:
            transaction.sender_wallet = wallet

        transaction.block_number = clock.current_block()

        self.comptroller.process_single_transaction(transaction)

        if wallet is not None:
            wallet_holdings = wallet.holdings

            dec_holdings: Dict[str, Decimal] = {
                key: to_decimal_exp(wallet_holdings[key], wallet._tokens_metadata[convert_symbol(key)].decimals)
                for key in wallet_holdings.keys()
            }

            state.insert_wallet(tx.sender, dec_holdings)

    def register(self, parameters: Parameters) -> None:
        parameters.add_compound_v2_protocol(self.comptroller.underlying_tokens)
        parameters.add_common(self.comptroller.underlying_tokens)

    def describe(self, parameters: SealedParameters) -> ObservableDescription:
        return ObservableDescription([self.id()], [], [])

    def observe(
        self, metric: Optional[List[MetricName]], clock: SimulationClock, state: RefSharedState
    ) -> Dict[MetricName, Decimal]:
        timestamp = int(clock.current_time().timestamp())
        if self.last_timestamp != timestamp:
            spot_oracle: SpotOracle = state.py_wrapper_spot_oracle(clock)
            self.observer.spot_oracle = spot_oracle
            self.observer.collect_observables(clock.current_block(), timestamp)
            self.observer.spot_oracle = None  # type: ignore
            self.last_timestamp = timestamp
        return {
            state.get_parameters().str_to_metric(m): Decimal(v.values[-1]).scaleb(int(-v.decimals))
            for (m, v) in self.observer._observables.items()
        }

    def __str__(self) -> str:
        properties = [
            f"_id: {self.id()}",
            f"protocol: {self.comptroller}",
            f"tran_helper: {self.tx_helper}",
        ]
        return "\n".join(properties)


def convert_symbol(key: str) -> str:
    if key == "cWETH":
        return "cETH"
    else:
        return key
