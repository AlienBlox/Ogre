import discord
from discord import app_commands
from discord.ext import commands

class TakeCopy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="takeme", description="Take a copy of the Ogre Bot")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Take a copy of me at https://github.com/AlienBlox/Ogre\nInstall at https://discord.com/oauth2/authorize?client_id=1508446745816989796&permissions=8&integration_type=0&scope=bot+applications.commands')

async def setup(bot):
    await bot.add_cog(TakeCopy(bot))