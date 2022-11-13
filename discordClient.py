import os
import discord
import re

class BotRoles():
    SLRT = 'SLRT'
    LMT = 'LMT'
    SO = 'Senior Officer'
    Recruit = 'Recruit'

    Trainer = 'Trainer'
    Grantable = [SLRT, LMT, SO, Recruit]


class DiscordClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: "{message.content}"')

        # grant self trainer rank (for testing)
        if message.content.lower() == BotRoles.Trainer.lower():
            await self.grantRole(message.guild, message.author, BotRoles.Trainer)

    async def on_raw_reaction_add(self, payload):
        server = await self.fetch_guild(payload.guild_id)
        channel = await self.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = payload.member

        if channel.name.lower() == 'request-rank':
            await self.handleRankReaction(server, message, member)
            return

    async def handleRankReaction(self, server, message, member):
        # Must have rank trainer to approve ranks
        if not self.userHasRole(member, BotRoles.Trainer):
            return

        # run a regex on the message content to identify what roles are being requested
        delimiter = '|'
        grantableRoles = delimiter.join(BotRoles.Grantable)
        regex = r'request\s*rank\s*:\s*('+grantableRoles +')\s*\n*trained by\s*:\s*(.*)'
        searchResult = re.search(regex, message.content, re.MULTILINE | re.IGNORECASE)

        if searchResult is None:
            return

        role = next(r for r in BotRoles.Grantable if r.lower() == searchResult.group(1).lower())
        # trained by entries are in group 2 if we want to verify all trainers have reacted before granting role
        if role is None:
            return

        await self.grantRole(server,  message.author, role)

    def userHasRole(self, member, roleName):
        return any(r.name.lower() == roleName.lower() for r in member.roles)

    async def grantRole(self, server, member, roleName):
        role = next(r for r in server.roles if r.name.lower()
                    == roleName.lower())

        print(f'granting "{role}" role to: {member.name}')
        await member.add_roles(role)

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.members = True

        super().__init__(intents=intents)
        token = os.environ.get('BOT_TOKEN')
        self.run(token)

if __name__ == "__main__":
    DiscordClient()
