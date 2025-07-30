from qcogclient import store


def set_api_key(api_key: str) -> None:
    # Check if an api key is already set.
    partial_store = store.get({"api_key": store.GET})

    in_store_key = partial_store.get("api_key", None)

    if in_store_key:
        raise ValueError("API key already set. Logout first.")

    store.dispatch({"name": "set", "payload": {"api_key": api_key}})


def clear_api_key() -> None:
    store.dispatch({"name": "delete", "payload": {"api_key": store.DEL}})


def clear_store() -> None:
    # Clear all the keys in the store except for the api_key
    keys = store.keys()
    delete_obj: store.PartialStore = {}

    for key in keys:
        if key != "api_key":
            delete_obj[key] = store.DEL  # type: ignore

    store.dispatch({"name": "delete", "payload": delete_obj})
