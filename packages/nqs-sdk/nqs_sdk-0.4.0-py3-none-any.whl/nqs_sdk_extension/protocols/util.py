import logging
from dataclasses import dataclass
from typing import List

from nqs_sdk_extension.spot import DataLoader

from .stub import MyTokenMetadata

logger = logging.getLogger(__name__)


@dataclass
class TokenInfo:
    decimals: int
    symbol: str


def get_tokens(tokens: List[str]) -> dict:
    out = {}
    quantlib = DataLoader.quantlib_source()
    for token in set(tokens):
        info = quantlib.token_info("Ethereum", token)
        if info is not None:
            out[token] = TokenInfo(
                symbol=token,
                decimals=info["decimals"],
            )
        else:
            logger.error(f"token {token} has no info")
    return out


def get_all_tokens() -> dict:
    all_token_info = DataLoader.quantlib_source().all_token_info("Ethereum")

    tokens_metadata = {
        token: MyTokenMetadata(int(decimals))
        for token, decimals in zip(all_token_info["symbol"], all_token_info["decimals"])
        if token is not None
    }

    return tokens_metadata
