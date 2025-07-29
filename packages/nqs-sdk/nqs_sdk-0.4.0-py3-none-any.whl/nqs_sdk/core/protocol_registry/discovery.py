from typing import Dict, List, Optional

from nqs_sdk.core.protocol_registry.protocol_id import ProtocolID
from nqs_sdk.core.protocol_registry.registry import ProtocolRegistry


def list_available_protocols() -> List[Dict[str, str]]:
    protocols = ProtocolRegistry.get_available_protocols()
    metadata = ProtocolRegistry.get_protocol_metadata()

    result: List[Dict[str, str]] = []
    for protocol_id, source in protocols.items():
        protocol_info: Dict[str, str] = {
            "id": protocol_id,
            "source": source,
        }

        for meta_id in metadata:
            if str(meta_id) == protocol_id:
                for key, value in metadata[meta_id].items():
                    protocol_info[key] = str(value)
                break

        result.append(protocol_info)

    return result


def print_protocol_info(protocol_id: Optional[str] = None) -> None:
    if protocol_id:
        protocols = ProtocolRegistry.get_available_protocols()
        if protocol_id not in protocols:
            print(f"Protocol '{protocol_id}' not found.")
            return

        source = protocols[protocol_id]
        metadata = ProtocolRegistry.get_protocol_metadata(ProtocolID.from_string(protocol_id))

        print(f"Protocol: {protocol_id}")
        print(f"Source: {source}")
        for key, value in metadata.items():
            if key not in ["id", "source"]:
                print(f"{key.capitalize()}: {value}")
    else:
        available_protocols: List[Dict[str, str]] = list_available_protocols()
        print(f"Available Protocols ({len(available_protocols)}):")

        for protocol_dict in available_protocols:
            p_id = protocol_dict.get("id", "Unknown")
            p_source = protocol_dict.get("source", "Unknown")
            p_description = protocol_dict.get("description", "No description")

            print(f"- {p_id} ({p_source}): {p_description}")
