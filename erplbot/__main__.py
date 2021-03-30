import discord
import pickle
from erplbot.club_members import get_members_from_spreadsheet, Name
from erplbot.sheets import GoogleSheets, retrieve_credentials
# Try to get variables from pickled config
try:
    print('Loading Config')
    [BOT_TOKEN, SPREADSHEET_ID, SHEET_NAME, RANGE_START, RANGE_END, MEMBER_ROLE_ID, OFFICER_ROLE_ID, PROJECT_LEAD_ID, RECRUIT_ROLE_ID, BOT_COMMAND_CHANNEL] = pickle.load(open ("config.bin", "rb"))
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
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='4 New Members'))
        print("Bot initialized")
    
    async def on_member_join(self, member):
        """
        This function runs whenever a new member joins the server
        """
        print(f"{member.name} joined")
        # Give em' the default role
        recruit_role = member.guild.get_role(RECRUIT_ROLE_ID)
        await member.add_roles(recruit_role, reason='Member join')
        # Create the DM by default
        await member.create_dm()
        async with member.typing():
            # Here we will just call the update_members function
            await self.update_members(member.guild)
            # Add a welcome message/embed here


        # Message member on join with welcome message
        await member.send(f"Hello {member.name}, welcome to *ERPL*!\n Please read our rules on #rules-info & we hope you rocket to success with us. 🚀\n If you've paid dues, Please set your nick to the name you filled out in payment of dues.\n *@ERPLDiscordBot should do the rest. (if it doesn't work, complain in #join-boost-system )*\n This will get you access to project channels.")
    
    async def on_member_leave(self, discord_member):
        """
        This function runs whenever a new member leaves the server
        """
        print(f"{discord_member.name} left")
        # Try to set them to false if they left as a member
        try:
            discord_member.update_rolled(google_sheets, SPREADSHEET_ID, SHEET_NAME, RANGE_END, False)
        except Exception as e:
                print(f"{discord_member.name} leaving raised an exception\n{e}")
            
    async def on_member_update(self, before, after):
        """
        This function runs whenever a new member updates their own profile, like changing their nickname
        """
        # Ignore our own updates
        if after == self.user:
            return

        print(f"{before.name} updated")
        # Here we will just call the update_members function
        await self.update_members(before.guild)
    
    async def on_message(self, message):
        """
        This function runs whenever a message is sent
        """
        # Ignore our own messages
        if message.author == self.user:
            return



        #Clay
        if message.channel.id == BOT_COMMAND_CHANNEL:
            #Command for creating a new project text (through dm)
            try:
                #CreateProject
                if '~CreateProject' in message.content:

                    #Check to make sure the person sending the message has correct role:
                    # Comb through the roles of who sent the message to look for Officer name  
                    if 'Officer' in [x.name for x in message.author.roles]:


                        #Check to make sure the channel/project does not already exist


                        #attempt to split and save the project name
                        try:
                            projectName = message.content.split(' ')[1]
                            if projectName == "":
                               print("Project name empty")


                            #Send a message back to confirm creation
                            await message.channel.send("Project " + projectName + " Created")
                        except Exception as e:
                            print(f"User entry failed: {message.content} \n{e}")
                            await message.channel.send("Error creating the project. Please use the format: '~CreateProject (projectName)'")

            except Exception as e:
                print(f"An exception occured while creating a new project\n{e}")


        # WaterLubber easteregg
        try:
            if message.content == 'Waterlubber':
                async with message.channel.typing():
                    await message.guild.me.edit(nick='Waterlubber')
                    await message.channel.send('*Hello my name is Paul and I like to code!*')
                    await message.guild.me.edit(nick='ERPL Discord Bot')
            elif ('waterlubber' in message.content.lower()):
                await message.delete()
        except:
            print("An exception occurred during Waterlubber")

        

            
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