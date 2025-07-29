def verify_transfer_allowed() -> None:
    """
    This function checks the caller's class to ensure that the transfer operation is only initiated by "CompoundMarket".
    It uses Python's `inspect` module to examine the call stack and determine if the "parent-parent" class is
    CompoundMarket.

    Raises:
        ValueError: If the caller class is not "CompoundMarket"

    Returns:
        None: This function does not return anything. It either success or raising error
    """
    import inspect

    frame = inspect.currentframe().f_back.f_back  # type: ignore
    caller_class = frame.f_locals.get("self", None).__class__ if "self" in frame.f_locals else None  # type: ignore

    if caller_class is None:
        raise ValueError("Transfer operation must be called from CompoundMarket")

    if caller_class.__name__ != "CompoundMarket":
        raise ValueError(
            "Transfer of cTokens is allowed only by sending a Transfer transaction to the relative cToken."
        )
