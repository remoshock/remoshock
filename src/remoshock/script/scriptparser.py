#
# Copyright nilswinter 2021-2025. License: AGPL
# _____________________________________________


class ScriptParser:
    
    def parse(self, content):
        for line in content.splitlines():
            print(line)
            


ScriptParser().parse("""
#!/usr/bin/env remoshockcli
REMOSHOCK SCRIPT VERSION 1
# Testscript
LOG Hello

BEEP 1 at 50% for 500ms by testscript
WAIT FOR 00:00:01
SHOCK   1    at 20  %   for   500  ms   by   testscript1
WAIT    FOR 00:00:01

BEEP 1 50 500 testscript2
WAIT    FOR 00:00:01
BEEPSHOCK 1 30% 500ms
LOG Done
#        <action> ["receiver"] <n> ["at"] <p>[ ]["%"] ["for"] <d> ["ms"] ["by"] [<source>]
#        LOG message
#        EXEC shell command
#        EXEC [WAIT] shell command
#        PLAY [WAIT] audio file
#        WAIT FOR hh:mm:ss
#        WAIT UNTIL hh:mm:ss  // since script start | absolute
#        WAIT UNTIL [yyyy-mm-hh ]hh:mm:ss
""")
