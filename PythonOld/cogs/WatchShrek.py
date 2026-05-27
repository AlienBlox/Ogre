import discord
from discord import app_commands
from discord.ext import commands

class WatchShrek(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="watchshrek", description="Watch the Shrek movie!")
    async def watchshrek(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Shrek movie on YouTube: https://www.youtube.com/watch?v=4N-YcELXPtg')

async def setup(bot):
    await bot.add_cog(WatchShrek(bot))