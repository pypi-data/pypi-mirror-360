def change_dict_key(d: dict, old_key: str, new_key: str) -> None:
    if old_key in d:
        d[new_key] = d.pop(old_key)
