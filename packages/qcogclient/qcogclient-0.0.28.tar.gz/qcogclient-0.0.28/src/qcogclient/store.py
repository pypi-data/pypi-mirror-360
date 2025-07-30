from __future__ import annotations

import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal, NotRequired, TypedDict


class PartialStore(TypedDict):
    api_key: NotRequired[str]
    user_id: NotRequired[str]
    experiment_id: NotRequired[str]
    project_id: NotRequired[str]


DEL = "DEL"
GET = "GET"
STORE_PATH = Path.home() / ".qcogclient" / "store.json"


class Store:
    _test: bool = False
    _instance: Store | None = None
    _callbacks: dict[
        Literal["set", "delete", "update"], list[Callable[[PartialStore], None]]
    ] = {
        "set": [],
        "delete": [],
        "update": [],
    }

    def __new__(cls, *args: Any, **kwargs: Any) -> Store:
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Prevent initialization if running in tests
        if os.environ.get("QCOG_ENV") == "TEST":
            self._store: PartialStore = {}
            self._test = True
            return

        self._store: PartialStore = {}  # type: ignore
        self._init_store_folder()
        self._load_store()

    @property
    def store(self) -> PartialStore:
        if self._test:
            return {}

        if not self._store:
            self._store = {}
        self._load_store()
        return self._store

    @store.setter
    def store(self, value: PartialStore) -> None:
        if self._test:
            return

        self._store = {
            **self._store,
            **value,
        }
        self._store = {k: v for k, v in self._store.items() if v != DEL}  # type: ignore
        self._dump_store()

    def _init_store_folder(self) -> None:
        if self._test:
            return

        folder = STORE_PATH.parent
        folder.mkdir(parents=True, exist_ok=True)

    def _dump_store(self) -> None:
        if self._test:
            return

        with STORE_PATH.open("w") as f:
            json.dump(self._store, f, indent=2)

    def _load_store(self) -> None:
        if self._test:
            return

        if not STORE_PATH.exists():
            # Dump the current store
            self._dump_store()

        with STORE_PATH.open("r") as f:
            self._store = json.load(f)

    def __getattr__(self, key: str) -> Any:
        if key not in self.store:
            raise AttributeError(f"Key {key} not found in store")
        return self.store[key]  # type: ignore

    def get(self, key: str) -> Any:
        value = self.store.get(key)
        if value is None:
            raise ValueError(f"Key {key} not found in store")
        return value

    def set(self, partialstore: PartialStore) -> None:
        for k in partialstore:
            if k in self.store:
                raise ValueError(f"Key {k} already exists in store")

        self.store = {
            **self.store,
            **partialstore,
        }

    def delete(self, partialstore: PartialStore) -> None:
        for k in partialstore:
            if k not in self.store:
                return

        self.store = partialstore

    def update(self, partialstore: PartialStore) -> None:
        for k in partialstore:
            if k not in self.store:
                raise ValueError(f"Key {k} not found in store")

        self.store = {
            **self.store,
            **partialstore,
        }

    def on(self, event: Event, callback: Callable[[PartialStore], None]) -> None:
        self._callbacks[event["name"]].append(callback)


class Event(TypedDict):
    name: Literal["set", "delete", "update"]
    payload: PartialStore


def dispatch(event: Event) -> Store:
    s = Store()
    if event["name"] == "set":
        s.set(event["payload"])
    elif event["name"] == "delete":
        s.delete(event["payload"])
    elif event["name"] == "update":
        s.update(event["payload"])
    else:
        raise ValueError(f"Invalid event name: {event['name']}")

    for callback in s._callbacks[event["name"]]:
        callback(event["payload"])

    return s


def keys() -> list[str]:
    s = Store()
    return list(s.store.keys())


def on(event: Event, callback: Callable[[PartialStore], None]) -> None:
    """Register a callback for a specific event"""
    s = Store()
    s.on(event, callback)


def get(store: PartialStore) -> PartialStore:
    """Get the key values from the store

    Parameters
    ----------
    store: PartialStore
        The store to get the key values from.
        Values should be set as `GET` events.

    Returns
    -------
    PartialStore
        The key values from the store.
    """
    s = Store()
    retval: PartialStore = {}

    for k, v in store.items():
        if k not in s.store:
            retval[k] = None  # type: ignore
        elif v == GET:
            retval[k] = s.store[k]  # type: ignore
        else:
            raise RuntimeError("Something went wrong")

    return retval
