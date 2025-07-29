from typing import Tuple

TOKENS_TO_WRAP = ["BTC", "ETH"]
STABLECOINS = ["USDT", "USDC", "DAI", "TUSD", "LUSD", "FRAX"]
ETH_STABLE_PAIRS = ["stETH"]
TOKEN_DECIMALS = {"USDC": 6, "USDT": 6, "WBTC": 8}


def wrap_token(token: str) -> str:
    if token in TOKENS_TO_WRAP:
        return "W" + token
    else:
        return token


def get_wrapped_spot(spot: Tuple[str, str]) -> Tuple[str, str]:
    ccy1, ccy2 = spot[0], spot[1]
    return wrap_token(ccy1), wrap_token(ccy2)
