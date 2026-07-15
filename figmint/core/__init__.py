"""Core editing engine: commands, undo/redo history, and the edit log.

Everything the user does is a :class:`~figmint.core.commands.Command`. A single
:class:`~figmint.core.history.CommandStack` provides undo/redo and feeds a single
:class:`~figmint.core.editlog.EditLog`, which is the one source of truth behind both
code generation and project save/load.
"""

from figmint.core.commands import (
    Command,
    DeleteArtistCommand,
    MoveTextCommand,
    SetArtistPropCommand,
)
from figmint.core.editlog import EditLog
from figmint.core.history import CommandStack

__all__ = [
    "Command",
    "SetArtistPropCommand",
    "MoveTextCommand",
    "DeleteArtistCommand",
    "EditLog",
    "CommandStack",
]
