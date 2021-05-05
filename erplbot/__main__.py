import discord
import pickle
from erplbot.club_members import get_members_from_spreadsheet, Name
from erplbot.sheets import GoogleSheets, retrieve_credentials
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
            embed = discord.Embed(
                title="*We hope you rocket to success with us!* :rocket: <:ERPL:809226558988484608>",
                colour=discord.Colour(0x255c6),
                description="<@!${user.id}> Welcome to **ERPL**! Please read our rules on <#${751973296114761788}>.\r\n If you've paid dues, Please set your nick to the name you filled out in payment of dues...\n *<@!${801184786580242552}> should do the rest. This will get you access to project channels.*")
            embed.set_thumbnail(url="https://discord.com/assets/748ff0e7b2f1f22adecad8463de25945.svg")
            embed.set_author(name="Welcome to the Experimental Rocket Propulsion Lab!")
            await JOIN_CHANNEL.send(embed=embed)

        # Message member on join with welcome message
        await member.send(f"Hello {member.name}, welcome to *ERPL*!\n Please read our rules on #rules-info & we hope you rocket to success with us. 🚀\n If you've paid dues, Please set your nick to the name you filled out in payment of dues.\n *@ERPLDiscordBot should do the rest. (if it doesn't work, complain in #join-boost-system )*\n This will get you access to project channels.")
        # Update members
        await self.update_members(member.guild)
    
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

        """
        Bot Commands
        """
        # Make sure channel is specified
        if message.channel == message.guild.get_channel(BOT_COMMAND_CHANNEL):
            """
            Create Project Command (Officers Only)
            """
            try:
                if '/CreateProject' in message.content:
                    # Check to make sure the person sending the message has officer role
                    if OFFICER_ROLE_ID in list(map(lambda role: role.id, message.author.roles)):
                        # Attempt to split and save the project name
                        try:
                            if len(message.content.split(' '))<2:
                               await message.author.send("Project name is empty")
                            projectName = message.content.split(' ')[1]
                            print(message.content.split(' '))
                            if len(message.content.split(' '))>=4:
                                subChatBool = message.content.split(' ')[3]
                                description = " ".join(message.content.split(" ")[4:len(message.content.split(' '))])
                            elif len(message.content.split(' '))==3:
                                subChatBool = message.content.split(' ')[3]
                                description = "Project "+projectName
                            else:
                                subChatBool = True
                                description = "Project "+projectName
                            # Get category
                            for category in message.guild.categories:
                                if category.name == "Projects":
                                    break
                            # Check to make sure the channel/project/role does not already exist 
                            if projectName in [channel.name for channel in category.channels]:
                                await message.author.create_dm()
                                async with message.author.typing():
                                    await message.author.send(f"The project, {projectName}, already exists!")
                            elif projectName in [role.name for role in message.guild.roles]:
                                await message.author.create_dm()
                                async with message.author.typing():
                                    await message.author.send(f"The role, {projectName}, already exists!")
                            else:
                                # Get the new project lead
                                newProjectLead = message.guild.get_member_named(message.content.split(' ')[2])
                                print(f"Project lead: {newProjectLead}")
                                # Create the Project role
                                projectRole = await message.guild.create_role(name=projectName, reason=f'Project creation by {message.author}')
                                # Set the Role Position to 3 (above recruit & member but below VIP)
                                await projectRole.edit(position=3, reason=f'Project creation by {message.author}')
                                # Try to update the description to end with lead's nick
                                try:
                                    description = description+" lead by "+newProjectLead.nick
                                except:
                                    description
                                # Create the project channel
                                projectChannel = await message.guild.create_text_channel(projectName, topic=description, category=category, reason=f'Project creation by {message.author}')
                                await projectChannel.set_permissions(newProjectLead, manage_channels=True, manage_permissions=True, manage_webhooks=True, read_message_history=True, reason=f'Project creation by {message.author}')
                                await projectChannel.set_permissions(projectRole, view_channel=True, read_messages=True, send_messages=True, add_reactions=True, attach_files=True, embed_links=True, read_message_history=True, reason=f'Project creation by {message.author}')
                                
                                if subChatBool:
                                    print(f"Subchat: {subChatBool}")
                                    # Setup Sub-chat category & channel
                                    
                                    # Assign Permissions to category

                                # Give new project lead roles & alert them
                                await newProjectLead.add_roles(message.guild.get_role(PROJECT_ROLE_ID), reason=f'Project creation by {message.author}')
                                await newProjectLead.add_roles(projectRole, reason=f'Project creation by {message.author}')
                                await newProjectLead.send(f"Project {projectName} created by {message.author}!") 
                                # Send a message back to confirm creation
                                await message.channel.send(f"Project {projectName} created!")
                        
                        except Exception as e:
                            print(f"User entry failed: {message.content} \n {e}")
                            await message.author.create_dm()
                            async with message.author.typing():
                                await message.author.send("***Error creating the project...***\nPlease use the format: `/CreateProject projectName projectLeadUsername true/false` \n Where ProjectName is the name of the project, projectLeadUsername is the username (not nick) of the new project lead, the boolean is whether sub-chats are created (default:true), Then the description of the project")

            except Exception as e:
                print(f"An exception occured while creating a new project:\n{e}")

            """
            Delete Project Command (Officers Only)
            """
            try:
                if '/DeleteProject' in message.content:
                    # Check to make sure the person sending the message has officer role
                    if OFFICER_ROLE_ID in list(map(lambda role: role.id, message.author.roles)):
                        # Attempt to split and save the project name
                        try:
                            if len(message.content.split(' '))<2:
                               await message.author.send("Project name is empty")
                            projectName = message.content.split(' ')[1].lower()
                            # Update logs
                            print(f"{message.author} issued /Delete project {projectName}")
                            # Get category, names, and channels
                            for category in message.guild.categories:
                                if category.name == "Projects":
                                    break
                            # Check to make sure the channel/project already exists 
                            if projectName in [channel.name for channel in category.channels]:
                                for channel in category.channels:
                                    if channel.name == projectName:
                                        break
                                # Locate the Project Lead and remove them

                                # Hide Old Project Channel
                                await channel.set_permissions(message.guild.get_role(RECRUIT_ROLE_ID), view_channel=False, read_messages=False, send_messages=False, reason=f'Project Deleted by {message.author}')
                                await channel.set_permissions(message.guild.get_role(MEMBER_ROLE_ID), view_channel=False, read_messages=False, send_messages=False, reason=f'Project Deleted by {message.author}')
                                await channel.set_permissions(message.guild.get_role(PROJECT_ROLE_ID), view_channel=False, read_messages=False, send_messages=False, reason=f'Project Deleted by {message.author}')
                                await channel.set_permissions(message.guild.get_role(OFFICER_ROLE_ID), view_channel=False, read_messages=False, send_messages=False, reason=f'Project Deleted by {message.author}')
                                # Loop through categories to locate sub-chats
                                if projectName+" sub-chats" in [category.name for category in message.guild.categories]:
                                    for category in message.guild.categories:
                                        if category.name == projectName+" sub-chats":
                                            break
                                    await category.set_permissions(message.guild.get_role(PROJECT_ROLE_ID), view_channel=False, read_messages=False, send_messages=False,reason='Project Deleted')
                                    await category.set_permissions(message.guild.get_role(OFFICER_ROLE_ID), view_channel=False, read_messages=False, send_messages=False,reason='Project Deleted')
                                    print("Sub-chats found")
                                else:
                                    print("No Sub-chats found")
                                # Delete Role (not tested, as i couldnt get the /deleteproject to work)
                                for projectRole in message.guild.roles:
                                    if projectRole.name.lower() == projectName:
                                        print(projectRole)
                                        await projectRole.delete(reason=f'Project Deleted by {message.author}')
                                # Send a message back to confirm deletion
                                await message.channel.send(f"Project {projectName} deleted!")
                            else:
                                await message.author.create_dm()
                                async with message.author.typing():
                                    await message.author.send(f"The project, {projectName}, doesn't exist!")
                        
                        except Exception as e:
                            print(f"User entry failed: {message.content} \n {e}")
                            await message.author.create_dm()
                            async with message.author.typing():
                                await message.author.send("***Error deleting the project...***\nPlease use the format: `/DeleteProject projectName` \n Where ProjectName is the name of the project")

            except Exception as e:
                print(f"An exception occured while deleting an old project:\n{e}")

        # WaterLubber easteregg
        try:
            if message.content == 'Waterlubber':
                async with message.channel.typing():
                    await message.guild.me.edit(nick='Waterlubber')
                    await message.channel.send('*Hello my name is Paul and I like to code!*')
                    await message.guild.me.edit(nick='ERPL Discord Bot')
        except Exception as e:
            print(f"An exception occurred during Waterlubber:\n{e}")
            
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