from typing import Any

from nqs_sdk_extension.run_configuration.parameters import SpotTypes
from nqs_sdk_extension.spot import CustomProcess, GBMProcess, HistoricalProcess, OUProcess, WGNProcess

mapping_spot_objects: dict[str, Any] = {
    SpotTypes.GBM.value: GBMProcess,
    SpotTypes.WGN.value: WGNProcess,
    SpotTypes.OU.value: OUProcess,
    SpotTypes.HISTORICAL.value: HistoricalProcess,
    SpotTypes.CUSTOM.value: CustomProcess,
}
