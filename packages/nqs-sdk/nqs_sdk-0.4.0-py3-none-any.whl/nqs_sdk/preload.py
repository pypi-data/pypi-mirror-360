import importlib
import pkgutil

import nqs_sdk

for module_info in pkgutil.walk_packages(nqs_sdk.__path__, nqs_sdk.__name__ + "."):
    importlib.import_module(module_info.name)
