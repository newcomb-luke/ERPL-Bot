"""
Bot Commands
"""
def parseCommand(self,message,roleIDs = [MEMBER_ROLE_ID, OFFICER_ROLE_ID, PROJECT_ROLE_ID, RECRUIT_ROLE_ID]):
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
    return

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
    return

    """
    Update Project Command (Officers Only)
    """
    try:
        if '/UpdateProject' in message.content:
            # Check to make sure the person sending the message has officer role
            if OFFICER_ROLE_ID in list(map(lambda role: role.id, message.author.roles)):
                # Attempt to split and save the project name
                try:
                    if len(message.content.split(' '))<2:
                    await message.author.send("Project name is empty")
                    # Unfinished
                
                except Exception as e:
                    print(f"User entry failed: {message.content} \n {e}")
                    await message.author.create_dm()
                    async with message.author.typing():
                        await message.author.send("***Error updating the project...***\nPlease use the format: `/UpdateProject projectName newLead description` \n Where ProjectName is the name of the project, newLead is the username *(not nickname)* of the new lead, and description is the updated description (None provided assumes it stays the same)")
                        the project")
    except Exception as e:
        print(f"An exception occured while updating a project:\n{e}")
    return