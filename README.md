# ERPL-Bot
The bot that will do all things for the ERPL Discord that we want done.

### Member Discord Dues Tracking
We have a google sheet with all members who paid dues, first and last. We have a discord with members joining. 
This bot will update a person's role in the discord server when they change their name to a name in the list (First last) then mark their name as taken on the spreadsheet.

### Further Discord Features:
- [x] On user join, send intro message. (explain rolling)
- [x] On user join, set role to 'recruit'.
- [x] On user made member, send message.
- [ ] Automation of group roles by messaging to the bot (member wants to join cardea chat, gets cardea role)
- [ ] Add DECtalk tts (*John Madden*)

## Operation
 * Add requirements (*see requirements.txt*)
 * Edit makeConfig to your values (*Discord bot token, spreadsheet ID, IDs from discord*)
 * Run makeConfig to generate config.bin