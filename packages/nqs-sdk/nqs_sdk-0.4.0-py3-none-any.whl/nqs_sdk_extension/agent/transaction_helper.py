from typing import Any

from nqs_pycore import Wallet

from nqs_sdk_extension.agent.ux_transactions import UXTransaction
from nqs_sdk_extension.mappings import (
    action_conversion_dictionary,
    mapping_protocol_to_type,
    mapping_type_to_protocol_transaction_helper,
    ux_fields,
)
from nqs_sdk_extension.protocol import ABCProtocol, UniswapV3
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction
from nqs_sdk_extension.transaction.transaction_helper import ProtocolTransactionHelper


class TransactionHelper:
    """
    A class to generate transactions from parameters.
    """

    def __init__(self) -> None:
        self.protocol_transaction_helpers: dict[str, ProtocolTransactionHelper] = {}
        for protocol_type, protocol_transaction_helper in mapping_type_to_protocol_transaction_helper.items():
            self.protocol_transaction_helpers[protocol_type] = protocol_transaction_helper()

    @staticmethod
    def wrap_single_transaction(args_tx: dict, sender_wallet: Wallet) -> list[ABCTransaction]:
        return [UXTransaction(args_tx, sender_wallet)]

    def generate_transactions_from_user_params(
        self, args_tx: dict, sender_wallet: Wallet, action_name: str
    ) -> list[ABCTransaction]:
        action_type = args_tx.get("action_type", None)
        protocol = args_tx.get("protocol", None)
        if action_type is None or protocol is None:
            raise ValueError(f"Action {action_name}: action type and protocol are not set properly")
        protocol_type = mapping_protocol_to_type.get(protocol.__class__, None)
        if protocol_type is None:
            raise ValueError(
                f"Action {action_name}: Protocol type for protocol {protocol.__class__} is not set " f"in mappings"
            )
        method = TransactionHelper.wrap_single_transaction
        transactions = method(args_tx, sender_wallet)
        return self.inject_action_name(transactions, action_name)

    @staticmethod
    def inject_action_name(transactions: list[ABCTransaction], action_name: str) -> list[ABCTransaction]:
        for trx in transactions:
            trx.action_name = action_name
        return transactions

    def map_ux_transaction(self, ux_transaction: ABCTransaction) -> ABCTransaction:
        protocol: ABCProtocol | Any = ux_transaction.__dict__.get("protocol")
        sender_wallet: Wallet | Any = ux_transaction.__dict__.get("sender_wallet")
        action_type: str | Any = ux_transaction.__dict__.get("action_type")
        temp_ux_txn_dict = {
            key: value
            for key, value in ux_transaction.__dict__.items()
            if key not in ["protocol", "sender_wallet", "action_type"]
        }
        final_txn_arguments = {}

        protocol_type = mapping_protocol_to_type.get(protocol.__class__, None)
        if protocol_type is None:
            message = f"Unsupported protocol - {protocol.__class__}"
            message = (
                f"Action {ux_transaction.__dict__.get('action_name')} - " + message
                if ux_transaction.__dict__.get("action_type") is not None
                else message
            )
            raise ValueError(message)

        for ux_field, value in ux_transaction.__dict__.items():
            if (protocol_type, action_type, ux_field) in ux_fields:
                protocol_expected_field = action_conversion_dictionary[(protocol_type, action_type, ux_field)]["field"]
                conversion_method = action_conversion_dictionary[(protocol_type, action_type, ux_field)][
                    "conversion_method"
                ]
                final_txn_arguments.update(
                    dict(zip(protocol_expected_field, conversion_method(**ux_transaction.__dict__)))
                )
                temp_ux_txn_dict.pop(ux_field)

        final_txn_arguments.update(temp_ux_txn_dict)

        if mapping_type_to_protocol_transaction_helper.get(protocol_type) is not None:
            transaction_helper = self.protocol_transaction_helpers[protocol_type]
            if isinstance(protocol, UniswapV3):
                kwargs = {
                    "symbol0": protocol.symbol0,
                    "symbol1": protocol.symbol1,
                    "sqrt_price_x96": protocol.sqrt_price_x96,
                }
            else:
                kwargs = {}
            return transaction_helper.generate_transactions_from_user_params(
                action=action_type, args_tx=final_txn_arguments, sender_wallet=sender_wallet, **kwargs
            )
        else:
            message = f"Unsupported protocol type - {protocol_type}"
            message = (
                f"Action {ux_transaction.__dict__.get('action_name')} - " + message
                if ux_transaction.__dict__.get("action_type") is not None
                else message
            )
            raise ValueError(message)
