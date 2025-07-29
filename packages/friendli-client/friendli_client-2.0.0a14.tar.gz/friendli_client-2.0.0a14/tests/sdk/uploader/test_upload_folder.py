# Copyright (c) 2022-present, FriendliAI Inc. All rights reserved.

"""Test upload folder."""

from __future__ import annotations

from friendli.sdk.uploader import DirectoryUploader, DirectoryPattern


pattern = (
    DirectoryPattern().add_file_pattern("**/input/*").add_file_pattern("**/output/*")
)

uploader = DirectoryUploader(".", pattern)
