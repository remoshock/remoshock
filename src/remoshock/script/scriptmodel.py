#
# Copyright nilswinter 2021-2025. License: AGPL
# _____________________________________________


from dataclasses import dataclass
from typing import Optional


@dataclass
class Command:
    type: str
    line_number: int
    raw: str  # Preserve original text


@dataclass
class ScriptHeader(Command):
    version: int


@dataclass
class Comment(Command):
    pass


@dataclass
class EmptyLine(Command):
    pass


@dataclass
class LogCommand(Command):
    message: str


@dataclass
class ActionCommand(Command):
    action: str          # "BEEP" | "SHOCK" | "BEEPSHOCK"
    receiver: int
    power: int
    duration: int
    source: Optional[str] = None


@dataclass
class WaitForCommand(Command):
    time: str   # "hh:mm:ss"


@dataclass
class WaitUntilCommand(Command):
    datetime: str  # "hh:mm:ss" or "yyyy-mm-dd hh:mm:ss"
    wall: bool     # True if prefixed with "wall"


@dataclass
class ExecCommand(Command):
    wait: bool
    command: str


@dataclass
class PlayCommand(Command):
    wait: bool
    file: str
