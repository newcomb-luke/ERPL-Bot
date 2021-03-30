import pickle
### The bot's Discord Bot token
BOT_TOKEN = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

### The ID of the spreadsheet that contains all of ERPL's current members
SPREADSHEET_ID = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

### These specify when the member's data in the spreadsheet starts and ends
SHEET_NAME = 'SheetName!' # name of the sub-sheet containing master entry list
RANGE_START = 'A2'
RANGE_END = 'D'

### This is Discord's ID that means the "Member" role
MEMBER_ROLE_ID = 000000000000000000
RECRUIT_ROLE_ID = 000000000000000000
BOT_COMMAND_CHANNEL = 000000000000000000

###Use Pickle to write config.bin
with open('config.bin', 'wb') as fh:
    pickle.dump([BOT_TOKEN, SPREADSHEET_ID, SHEET_NAME, RANGE_START, RANGE_END, MEMBER_ROLE_ID, RECRUIT_ROLE_ID, BOT_COMMAND_CHANNEL], fh)
exit
