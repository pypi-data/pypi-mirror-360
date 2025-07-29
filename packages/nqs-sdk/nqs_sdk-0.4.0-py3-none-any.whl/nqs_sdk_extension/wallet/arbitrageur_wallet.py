import logging
from typing import Optional

from nqs_pycore import TokenMetadata, Wallet

Arbitrageur_NAME: str = "arbitrageur"


class ArbitrageurWallet(Wallet):
    def __new__(cls, holdings: dict[str, int], tokens_metadata: dict[str, TokenMetadata]):  # type: ignore[no-untyped-def]
        if len(holdings) != 0:
            logging.warning("Holdings are not empty for the Arbitrageur wallet it will modify the observables of it")

        instance = super().__new__(
            cls,
            holdings=holdings,
            tokens_metadata=tokens_metadata,
            erc721_tokens=[],
            agent_name=Arbitrageur_NAME,
        )
        return instance

    def transfer_from(self, token: str, amount: int, action_name: str | None = None) -> None:
        """
        Transfer funds out of the arbitrageur wallet is always successful
        """
        super().transfer_to(token, amount, action_name)
        logging.debug(f"{Arbitrageur_NAME}: Transferred {amount} of {token} from wallet.")

    def has_enough_balance(
        self, amount: int, symbol: str, action_name: Optional[str] = None, raise_warning: bool = False
    ) -> bool:
        """
        Arbitrageur wallet always has enough balance
        :param amount:
        :param symbol:
        :return:
        """
        return True
