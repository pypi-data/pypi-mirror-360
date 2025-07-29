import logging
from decimal import Decimal
from typing import Any, List, Optional

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
)

from nqs_sdk.interfaces.observable import Observable
from nqs_sdk.interfaces.protocol import Protocol
from nqs_sdk_extension.agent.transaction_helper import TransactionHelper
from nqs_sdk_extension.agent.ux_transactions import UXTransaction
from nqs_sdk_extension.observer.protocol.cex import CEXObserver
from nqs_sdk_extension.protocol.cex import CEX, RebalanceTransactionCEX, SwapTransactionCEX
from nqs_sdk_extension.protocols.common.wrapped_event import WrappedEvent

logger = logging.getLogger(__name__)


class CexWrapper(Protocol, Observable):
    def __init__(
        self,
        name: str,
        cex: CEX,
        numeraire: str,
        tokens_metadata: TokenMetadata,
    ) -> None:
        self.name = name
        self.cex = cex
        self.tokens_metadata = tokens_metadata
        self.tx_helper = TransactionHelper()
        self.last_timestamp = None

        # Set observer
        self.observer = CEXObserver(self.cex)
        self.observer.set_environment(self.id(), {})
        self.observer.numeraire_decimals = tokens_metadata[numeraire].decimals

    def id(self) -> str:
        return self.name

    def build_tx_payload(self, source: str, sender: str, call: Any) -> TxRequest:
        args = call["args"]
        action_name = call["name"]
        transaction = WrappedEvent(action_name, self.name, self.cex, args)

        return TxRequest(self.name, source, sender, transaction)

    def execute_tx(self, clock: SimulationClock, state: MutSharedState, tx: TxRequest) -> None:
        transaction = tx.payload

        # sender = tx.source.split(".")[0]
        # holdings = state.get_wallet(tx.sender)

        wallet = state.get_wallet(tx.sender)

        # if holdings is not None:
        #     # somehow wallet already do scaleb conversion
        #     holdings: dict[str, int] = {key: holdings[key] for key in holdings.keys()}

        #     wallet = Wallet(
        #         agent_name=sender,
        #         holdings=holdings,
        #         tokens_metadata=self.tokens_metadata,
        #     )
        # else:
        #     wallet = None

        # Get required spot pairs
        spot_oracle = state.py_wrapper_spot_oracle(clock)
        pairs = [(token, spot_oracle.numeraire) for token in spot_oracle.tokens]
        pairs += [(token, token) for token in spot_oracle.tokens]

        if isinstance(transaction, WrappedEvent):
            mapped_tx = transaction.map_tx()
            ux_tx = UXTransaction(mapped_tx, wallet)
            transaction = self.tx_helper.map_ux_transaction(ux_tx)

            if isinstance(transaction, SwapTransactionCEX):
                pairs += [
                    (transaction.token_to_buy, transaction.token_to_sell),
                    (transaction.token_to_sell, transaction.token_to_buy),
                ]

            if isinstance(transaction, RebalanceTransactionCEX):
                pairs += [(token, spot_oracle.numeraire) for token in transaction.weights]

            pairs = list(set(pairs))
            updated_spots = spot_oracle.get_selected_spots(pairs, int(clock.current_time().timestamp()))

            # The spot prices have to be rounded to 18 for parity with python sim
            updated_spots = {pair: round(price, 18) for (pair, price) in updated_spots.items()}
            self.cex.inject_spot_values(clock.current_time(), updated_spots)

        transaction.sender_wallet = wallet
        transaction.block_number = clock.current_block()

        self.cex.process_single_transaction(transaction)

        # if wallet is not None:
        #     holdings = wallet.holdings
        #     holdings: dict[str, Decimal] = {
        #         key: to_decimal_exp(holdings[key], wallet._tokens_metadata[convert_symbol(key)].decimals)
        #         for key in holdings.keys()
        #     }
        #     state.insert_wallet(tx.sender, holdings)
        return

    def register(self, parameters: Parameters) -> None:
        pass

    def describe(self, parameters: SealedParameters) -> ObservableDescription:
        return ObservableDescription([self.id()], [], [])

    def observe(
        self, metric: Optional[List[MetricName]], clock: SimulationClock, state: RefSharedState
    ) -> dict[MetricName, Decimal]:
        timestamp = clock.current_time()
        if self.last_timestamp != timestamp:
            spot_oracle = state.py_wrapper_spot_oracle(clock)
            self.observer.spot_oracle = spot_oracle
            self.observer.collect_observables(clock.current_block(), timestamp)
            self.last_timestamp = timestamp
        return {
            state.get_parameters().str_to_metric(m): Decimal(v.values[-1]).scaleb(int(-v.decimals))
            for (m, v) in self.observer._observables.items()
        }

    def __str__(self) -> str:
        properties = [
            f"_id: {self.id()}",
            f"protocol: {self.cex}",
            f"tran_helper: {self.tx_helper}",
        ]
        return "\n".join(properties)


def convert_symbol(key: str) -> str:
    if key == "cWETH":
        return "cETH"
    else:
        return key
