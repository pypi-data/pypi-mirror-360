import os

# FIXME: change behavior to make compatible with legacy_qis
USE_LEGACY_QIS = os.environ.get("LEGACY_QIS") is not None
