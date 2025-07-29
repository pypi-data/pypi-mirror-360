# Copyright (c) 2021-present, FriendliAI Inc. All rights reserved.

"""Constants."""

from __future__ import annotations

from enum import Enum

APP_NAME = "friendli-suite"
SERVICE_URL = "https://friendli.ai/suite"
SUITE_PAT_URL = "https://friendli.ai/suite/setting/tokens"


# Command group names
class Panel(str, Enum):
    """Panel names."""

    COMMON = "Common Commands"
    INFERENCE = "Inference Commands"
    DEDICATED = "Dedicated Endpoints Commands"
    SERVERLESS = "Serverless Endpoints Commands"
    CONTAINER = "Container Endpoints Commands"
    OTHER = "Other"
