#
# Copyright nilswinter 2025. License: AGPL
# ________________________________________

import re
from typing import Optional, List
# from datetime import timedelta
from remoshock.script.scriptmodel import Command, EmptyLine, Comment, ActionCommand, ExecCommand, LogCommand, PlayCommand, ScriptHeader, WaitForCommand, WaitUntilCommand


class ParseError(Exception):
    line_number: int
    line: str
    message: str

    def __str__(self):
        return f"Parse error on line {self.line_number}: {self.message}\n  >> {self.line}"


class ScriptParser:
    def __init__(self, script: str):
        self.lines = script.splitlines()

    def parse(self) -> List[Command]:
        commands: List[Command] = []
        for i, line in enumerate(self.lines, start=1):
            raw_line = line
            line = line.strip()

            # Empty line
            if not line:
                commands.append(EmptyLine(type="EMPTY", line_number=i, raw=raw_line))
                continue

            # Shebang
            if line.startswith("#!"):
                commands.append(Comment(type="COMMENT", line_number=i, raw=raw_line))
                continue

            # Comments
            if line.startswith("#"):
                commands.append(Comment(type="COMMENT", line_number=i, raw=raw_line))
                continue

            cmd = self.parse_line(line, i, raw_line)
            if cmd:
                commands.append(cmd)
            else:
                raise ParseError(i, raw_line, f"Parse error on line {self.line_number}: Unrecognized command or invalid parameters.\n  >> {self.line}")

        return commands

    def parse_line(self, line: str, line_number: int, raw_line: str) -> Optional[Command]:
        # REMOSHOCK SCRIPT VERSION <n>
        if m := re.match(r"REMOSHOCK\s+SCRIPT\s+VERSION\s+(\d+)", line, re.IGNORECASE):
            return ScriptHeader(type="HEADER", version=int(m.group(1)), line_number=line_number, raw=raw_line)

        # LOG
        if line.upper().startswith("LOG "):
            return LogCommand(type="LOG", message=line[4:].strip(), line_number=line_number, raw=raw_line)

        # WAIT FOR hh:mm:ss
        if m := re.match(r"WAIT\s+FOR\s+(\d{2}:\d{2}:\d{2})", line, re.IGNORECASE):
            return WaitForCommand(type="WAIT_FOR", time=m.group(1), line_number=line_number, raw=raw_line)

        # WAIT UNTIL [wall] [yyyy-mm-dd ]hh:mm:ss
        if m := re.match(r"WAIT\s+UNTIL\s+(wall\s+)?((?:\d{4}-\d{2}-\d{2}\s+)?\d{2}:\d{2}:\d{2})", line, re.IGNORECASE):
            return WaitUntilCommand(
                type="WAIT_UNTIL",
                datetime=m.group(2),
                wall=bool(m.group(1)),
                line_number=line_number,
                raw=raw_line
            )
        # ACTION (BEEP, SHOCK, BEEPSHOCK)
        if m := re.match(
            r"(LIGHT|BEEP|VIBRATE|SHOCK|KEEPAWAKE|BEEPSHOCK)\s+(?:receiver\s+)?(\d+)(?:\s+at)?\s+(\d+)(?:\s*%)?(?:\s+for)?\s+(\d+)\s*(?:ms)?(?:\s+by\s+(.*))?",
            line, re.IGNORECASE
        ):
            return ActionCommand(
                type="ACTION",
                action=m.group(1).upper(),
                receiver=int(m.group(2)),
                power=int(m.group(3)),
                duration=int(m.group(4)),
                source=m.group(5),
                line_number=line_number,
                raw=raw_line
            )

        # EXEC [WAIT]
        if m := re.match(r"EXEC(\s+WAIT)?\s+(.+)", line, re.IGNORECASE):
            return ExecCommand(
                type="EXEC",
                wait=bool(m.group(1)),
                command=m.group(2).strip(),
                line_number=line_number,
                raw=raw_line
            )

        # PLAY [WAIT]
        if m := re.match(r"PLAY(\s+WAIT)?\s+(.+)", line, re.IGNORECASE):
            return PlayCommand(
                type="PLAY",
                wait=bool(m.group(1)),
                file=m.group(2).strip(),
                line_number=line_number,
                raw=raw_line
            )

        return None


# Example usage
if __name__ == "__main__":
    from pprint import pprint
    pprint(ScriptParser("""
#!/usr/bin/env remoshockcli --script
REMOSHOCK SCRIPT VERSION 1
# Testscript
LOG Hello

BEEP 1 at 50% for 500ms by testscript
 WAIT FOR 00:00:01
SHOCK  receiver 1    at 20  %   for   500  ms   by   testscript1
WAIT    FOR 00:00:01

BEEP 1 50 500 ms by t
BEEP 1 50 500 testscript2
BEEP 1 50 500    by t
WAIT    FOR 00:00:01
#BEEPSHOCK 1 30% 500ms
LOG Done
#        REMOTESHOCK SCRIPT VERSION <n>
#        <action> ["receiver"] <n> ["at"] <p>[ ]["%"] ["for"] <d> ["ms"] ["by"] [<source>]
#        LOG message
#        EXEC shell command
#        EXEC [WAIT] shell command
#        PLAY [WAIT] audio file
#        WAIT FOR hh:mm:ss
#        WAIT UNTIL ["wall"] [yyyy-mm-hh ]hh:mm:ss
""").parse())
