# Copyright (c) 2022-present, FriendliAI Inc. All rights reserved.

from __future__ import annotations

from contextlib import closing

from friendli.sdk.sync import SyncClient


def test_sync_client_lifecycle() -> None:
    with SyncClient() as client:
        assert client
