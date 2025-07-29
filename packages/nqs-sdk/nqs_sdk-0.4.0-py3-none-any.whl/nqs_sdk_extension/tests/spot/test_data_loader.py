# type: ignore

from dotenv import load_dotenv

from nqs_sdk_extension.spot import DataLoader

load_dotenv()


def test_data_loader_singleton() -> None:
    d1 = DataLoader.quantlib_source()
    d2 = DataLoader.quantlib_source()

    assert id(d1) == id(d2), "Not a singleton"


def test_data_loader_call(source) -> None:
    d = DataLoader.quantlib_source()
    d.update(source=source)
    r = d.get_token_address("Ethereum", "USDC")
    assert r == "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
