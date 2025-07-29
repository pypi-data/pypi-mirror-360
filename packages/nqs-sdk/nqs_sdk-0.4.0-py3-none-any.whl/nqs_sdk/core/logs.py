import nqs_pycore


def activate_log() -> None:
    """
    Initialize logging subsystem for the NQS SDK

    This function activates the logging system, enabling detailed tracking of
    simulation execution, transaction processing, and error reporting. It
    configures both Python and Rust logging components

    The function is designed to be called once during SDK initialization,
    typically when importing the main nqs_sdk module. It gracefully handles
    cases where the rust logging system is already initialized

    Raises:
        Exception: Silently caught - logging activation failures don't prevent
                  SDK functionality, they just reduce observability

    Example:
        >>> from nqs_sdk.core.logs import activate_log
        >>> activate_log()  # Enable detailed logging

    Note:
        This function is automatically called when importing nqs_sdk,
        so manual invocation is typically unnecessary
    """
    try:
        nqs_pycore.activate_log()
    except Exception:
        pass
