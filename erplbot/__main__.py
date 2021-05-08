import discord
import pickle
from erplbot.club_members import get_members_from_spreadsheet, Name
from erplbot.sheets import GoogleSheets, retrieve_credentials
from erplbot.commands import bot_command
# Try to get variables from pickled config
try:
    print('Loading Config')
    [BOT_TOKEN, SPREADSHEET_ID, SHEET_NAME, RANGE_START, RANGE_END, MEMBER_ROLE_ID, OFFICER_ROLE_ID, PROJECT_ROLE_ID, RECRUIT_ROLE_ID, JOIN_CHANNEL, BOT_COMMAND_CHANNEL] = pickle.load(open("config.bin", "rb"))
except Exception as e:
    print(f"An exception occurred while loading config.bin\n{e}")
# This variable will store our GoogleSheets instance
google_sheets = None
# This one will store our Google API credentials
creds = None

class ERPLBot(discord.Client):
    """
    This class represents the core functionality of the ERPL Discord Bot
    """
    async def on_ready(self):
        """
        This function runs when the bot is connected to Discord
        """
        global google_sheets

        # Let's connect to Google's API now
        google_sheets = GoogleSheets(creds)

        #Change status
        print("Bot initialized")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='4 New Members'))
    
    async def on_member_join(self, member):
        """
        This function runs whenever a new member joins the server
        """
        print(f"{member.name} joined")
        # Give em' the default role
        recruit_role = member.guild.get_role(RECRUIT_ROLE_ID)
        await member.add_roles(recruit_role, reason='Member join')
        # Create the DM by default
        dm_channel = await member.create_dm()
        async with member.guild.get_channel(JOIN_CHANNEL).typing():
            # Add a welcome message/embed here
            embed = discord.Embed(
                title="*We hope you rocket to success with us!* :rocket: <:ERPL:809226558988484608>",
                colour=discord.Colour(0x255c6),
                description=f"<@!{member.id}> Welcome to **[ERPL](https://erpl.space)**! Please read our rules on <#{751973296114761788}>.\r\n If you've [paid dues](https://www.cognitoforms.com/ERAUERPL/erplclubdues), Please [set your nick](https://support.discord.com/hc/en-us/articles/219070107-Server-Nicknames#h_01EJTEHFA19Q5BK1GQY2XJ2ZJS) to the name you filled out in payment of dues...\n *<@!{801184786580242552}> should do the rest. This will get you access to project channels.*")
            embed.set_thumbnail(url="https://discord.com/assets/748ff0e7b2f1f22adecad8463de25945.svg")
            embed.set_author(name="Welcome to the Experimental Rocket Propulsion Lab!")
            await member.guild.get_channel(JOIN_CHANNEL).send(embed=embed)
        # Message member on join with welcome message
        await dm_channel.send(f"Hello <@!{member.id}>, welcome to *ERPL*!\n Please read our rules on <#{751973296114761788}> *(There is actually useful info in there)* & we hope you rocket to success with us. 🚀\n If you've paid dues, Please set your nick to the name you filled out in payment of dues.\n *<@!{801184786580242552}> should do the rest. (if it doesn't work, complain in <#{751980318025580654}> )*\n This will get you access to project channels.")
        # Finnaly we will just call the update_members function
        member_update = await self.update_members(member.guild)
        return member_update
    
    async def on_member_leave(self, discord_member):
        """
        This function runs whenever a new member leaves the server
        """
        # Try to set them to false if they left as a member
        try:
            discord_member.update_rolled(google_sheets, SPREADSHEET_ID, SHEET_NAME, RANGE_END, False)
        except Exception as e:
                print(f"{discord_member.name} leaving raised an exception\n{e}")
        # Print for record keeping
        print(f"{discord_member.name} left")
            
    async def on_member_update(self, before, after):
        """
        This function runs whenever a new member updates their own profile, like changing their nickname
        """
        # Ignore our own updates
        if after == self.user:
            return

        print(f"{before.name} updated")
        # If a nick is changed we call the update_members function
        if before.nick is not after.nick:
            await self.update_members(before.guild)
        
    async def on_message(self, message):
        """
        This function runs whenever a message is sent
        """
        # Ignore our own messages
        if message.author == self.user:
            return
        # Handle text chat messages first
        if message.channel.type =="text":
            """
            Bot Commands
            """
            # Make sure channel is specified
            if message.channel == message.guild.get_channel(BOT_COMMAND_CHANNEL):
                await bot_command(self, message, MEMBER_ROLE_ID, OFFICER_ROLE_ID, PROJECT_ROLE_ID, RECRUIT_ROLE_ID)

            # WaterLubber easteregg
            try:
                if message.content == 'Waterlubber':
                    async with message.channel.typing():
                        await message.guild.me.edit(nick='Waterlubber')
                        await message.channel.send('*Hello my name is Paul and I like to code!*')
                        await message.guild.me.edit(nick='ERPL Discord Bot')
            except Exception as e:
                print(f"An exception occurred during Waterlubber:\n{e}")
            return
        
        # Handle DM chat messages
        if message.channel.type =="private":
            return
            
    async def update_members(self, guild):
        """
        Updates all members in the ERPL Discord by checking their names, roles, and the spreadsheet
        """
        # "Guild" is the internal name for servers. This gets all members currently in the server
        discord_members = await guild.fetch_members().flatten()
        # Retrieves all current ERPL members listed in the spreadsheet as ClubMember instances
        spreadsheet_members = get_members_from_spreadsheet(google_sheets, SPREADSHEET_ID, SHEET_NAME + ':'.join([RANGE_START, RANGE_END]))
        # Loop through each member in the Discord
        for discord_member in discord_members:
            # Let's check if it is even worth our time to check if they are in the spreadsheet
            # We will check if they already have the member role
            if MEMBER_ROLE_ID in list(map(lambda role: role.id, discord_member.roles)):
                # Then just skip over them
                continue
            # If they don't have the role, we need to check if they are in the spreadsheet
            # First though, we need to get their name
            name = None
            # If this member has no nickname
            if discord_member.nick is None:
                name = Name.from_str(discord_member.name)
            # If they do have a nickname
            else:
                name = Name.from_str(discord_member.nick)
            # Iterate through each member in the spreadsheet (Ideally we would search the reverse of this list getting the most recent entries)
            for member in spreadsheet_members:
                # Check if their name is in the spreadsheet
                if name == member.name:
                    #Check to see if they are not already rolled
                    if member.rolled is False:
                        # Create a DM channel if non-existent
                        if discord_member.dm_channel is None:
                            await discord_member.create_dm()
                        async with discord_member.dm_channel.typing():
                            # If it is, then we need to add the member role
                            await discord_member.add_roles(guild.get_role(MEMBER_ROLE_ID), reason='Found user in club spreadsheet')
                            # We also need to make sure they are marked as added in the spreadsheet
                            member.update_rolled(google_sheets, SPREADSHEET_ID, SHEET_NAME, RANGE_END, True)
                            # We also need to remove the recruit role
                            await discord_member.remove_roles(guild.get_role(RECRUIT_ROLE_ID), reason='Found user in club spreadsheet')
                            print(f'Added member role to {name}')
                            # Send a DM confirming the membership
                            await discord_member.send(f'Hello {name}, you have been given membership on the ERPL discord server!')
                            await discord_member.send(f"Some reccomendations:\nMake the #announcements channel always alert you.\nRead the #rules, *there's useful info in there*.\nIf there's a project you want to join, you may want to unmute that chat too.\nFeel free to dm any of the project leads/officers with questions.")
                            await discord_member.send(f'We want to thank you {name}, your dues will help to propel the club and hopefully you will help us rocket to success!')
                    else:
                        print(f'Name Taken: {name}')

def main():
    """
    Our "main" function
    """
    global creds
    # Reads our Google API credentials before starting the bot
    creds = retrieve_credentials()
    # Sets up our intents as a Discord Bot
    intents = discord.Intents.default()
    intents.members = True
    # Connects to Discord and runs our bot with the bot's token
    client = ERPLBot(intents=intents)
    client.run(BOT_TOKEN)
if __name__ == "__main__":
    main()