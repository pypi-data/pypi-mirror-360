# Copyright (c) 2021-present, FriendliAI Inc. All rights reserved.

"""Init."""

from __future__ import annotations

from typer import Typer

from ..const import Panel
from ..typer_util import CommandUsageExample, format_examples

app = Typer(
    no_args_is_help=True,
    name="endpoint",
    rich_help_panel=Panel.DEDICATED,
    help="Manage your Dedicated Endpoints.",
)


@app.command(
    "list",
    help="""
List endpoints.
""",
    epilog=format_examples(
        [
            CommandUsageExample(
                synopsis=(
                    "Use browser to login to Friendli Suite. [yellow](RECOMMENDED)[/]"
                ),
                args="login",
            ),
        ]
    ),
)
def _list() -> None:
    pass # TODO: implement this command
