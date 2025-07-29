import os

import pyvinecopulib as pv

from nqs_sdk_extension.spot.data_loader import Singleton


class VineCopula(metaclass=Singleton):
    """
    Load copula models
    """

    def __init__(self) -> None:
        self._copulas_dict: dict[str, pv.Vinecop] = {}

    def update(self, copulas_dict: dict[str, pv.Vinecop]) -> None:
        self._copulas_dict.update(copulas_dict)

    def update_from_params(self, params: dict) -> None:
        current_path = os.path.dirname(os.path.realpath(__file__))
        for protocol_id in params.keys():
            calibrated_params_path = (
                params[protocol_id]
                .get("mint", {})
                .get("values", {})
                .get("marks", {})
                .get("vine_copula", {})
                .get("model_params_file", None)
            )
            if calibrated_params_path is not None:
                # use the path string as key
                self._copulas_dict.update(
                    {
                        calibrated_params_path: pv.Vinecop(
                            os.path.dirname(os.path.dirname(os.path.dirname(current_path)))
                            + "/"
                            + calibrated_params_path
                        )
                    }
                )

    def get_protocol_copula(self, conf_path: str) -> pv.Vinecop:
        if self._copulas_dict is not None:
            return self._copulas_dict.get(conf_path, None)
        else:
            raise ValueError(
                f"{conf_path} if not the config path of a calibrated copula used for random transaction" f" simulation"
            )
