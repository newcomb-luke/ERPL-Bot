import sys
import discord
import pickle
from erplbot.club_members import get_members_from_spreadsheet, Name
from erplbot.sheets import GoogleSheets, retrieve_credentials
#try to get variables from pickled config
try:
  print('Loading Config')
  [BOT_TOKEN, SPREADSHEET_ID, SHEET_NAME, RANGE_START, RANGE_END, MEMBER_ROLE_ID, RECRUIT_ROLE_ID] = pickle.load(open ("config.bin", "rb"))
except:
  print("An exception occurred while loading config.bin")
# This variable will store our GoogleSheets instance
google_sheets = None
# This one will store our Google API credentials
creds = None
# This will store 
resetMember = sys.argv.lower().contains('resetmember')

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
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='4 New Members'))
        print("Bot initialized")
    
    async def on_member_join(self, member,resetMember):
        """
        This function runs whenever a new member joins the server
        """
        print(f"{member.name} joined")
        await member.create_dm()
        async with member.typing():
            # Here we will just call the update_members function
            await self.update_members(member.guild,resetMember)
            # Add a welcome message/embed here

        # Message member on join with welcome message
        await member.send(f"Hello {member.name}, welcome to *ERPL*!\n Please read our rules on #rules-info & we hope you rocket to success with us. 🚀\n If you've paid dues, Please set your nick to the name you filled out in payment of dues.\n * @ERPLDiscordBot should do the rest. (if it doesn't work, complain in #join-boost-system )*\n This will get you access to project channels.")
    
    async def on_member_update(self, before, after,resetMember):
        """
        This function runs whenever a new member updates their own profile, like changing their nickname
        """
        print(f"{before.name} updated")
        # Here we will just call the update_members function
        await self.update_members(before.guild,resetMember)
    
    async def on_message(self, message):
        """
        This function runs whenever a message is sent
        """
        if message.author == self.user:
            return

        # WaterLubber easteregg
        if message.content == 'Waterlubber':
            async with message.channel.typing():
                await message.guild.me.edit(nick='Waterlubber')
                await message.channel.send('*Hello my name is Paul and I like to code!*')
                await message.delete()
                await message.guild.me.edit(nick='ERPL Discord Bot')

        elif ('waterlubber' in message.content.lower()):
            await message.delete()

    async def update_members(self, guild,resetMember):
        """
        Updates all members in the ERPL Discord by checking their names, roles, and the spreadsheet
        """

        # "Guild" is the internal name for servers. This gets all members currently in the server
        discord_members = await guild.fetch_members().flatten()

        # Retrieves all current ERPL members listed in the spreadsheet as ClubMember instances
        spreadsheet_members = get_members_from_spreadsheet(google_sheets, SPREADSHEET_ID, SHEET_NAME + ':'.join([RANGE_START, RANGE_END]))

        # Loop through each member in the Discord
        for discord_member in discord_members:
            if resetMember:
                name = None

                # If this member has no nickname
                if discord_member.nick is None:
                    name = Name.from_str(discord_member.name)

                # If they do have a nickname
                else:
                    name = Name.from_str(discord_member.nick)
                # Iterate through each member in the spreadsheet (Ideally we would search the reverse of this list getting the most recent entries)
                for member in spreadsheet_members:
                    if name == member.name:
                        if member.rolled is True:

                            # Move everyone to no longer rolled
                            member_role = guild.get_role(MEMBER_ROLE_ID)
                            await discord_member.remove_roles(member_role)
                            recruit_role = guild.get_role(RECRUIT_ROLE_ID)
                            await discord_member.add_roles(RECRUIT_ROLE_ID, reason='Member Reset')
                            
                        # Set all members to not rolled on sheet
                        member.update_rolled(google_sheets, SPREADSHEET_ID, SHEET_NAME, RANGE_END, False)

            else:
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

                            async with discord_member.typing():
                                # If it is, then we need to add the member role
                                member_role = guild.get_role(MEMBER_ROLE_ID)
                                await discord_member.add_roles(member_role, reason='Found user in club spreadsheet')

                                # We also need to make sure they are marked as added in the spreadsheet
                                member.update_rolled(google_sheets, SPREADSHEET_ID, SHEET_NAME, RANGE_END, True)

                                # We also need to remove the recruit role
                                recruit_role = guild.get_role(RECRUIT_ROLE_ID)
                                await discord_member.remove_roles(recruit_role)

                                print(f'Added member role to {name}')

                                # Send a DM confirming the membership
                                await discord_member.send(f'Hello {name}, you have been given membership on the ERPL discord server!')
                                await discord_member.send(f"Some reccomendations:\nMake the #announcements channel always alert you.\n Read the #rules, *there's useful info in there*.\nIf there's a project you want to join, you may want to unmute that chat too.\nFeel free to dm any of the project leads/officers with questions.")
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