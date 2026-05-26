import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

class Changelogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="changelogs", description="View the latest changes to the bot")
    async def changelogs(self, interaction: discord.Interaction):
        async with session.get:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://raw.githubusercontent.com/AlienBlox/Ogre/refs/heads/main/Changelogs.txt") as response:
                    if response.status == 200:
                        text = await response.text()
                        await interaction.response.send_message(text)
                    else:
                        await interaction.response.send_message(f"Error: Status code {response.status}")

async def setup(bot):
    await bot.add_cog(Changelogs(bot))