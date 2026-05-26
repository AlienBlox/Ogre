from time import sleep

import discord
from discord import app_commands
from discord.ext import commands

class Donkey(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash command for the latency check
    @app_commands.command(name="donkey", description="donkey")
    async def donkey(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Donkey from shrek...')
        sleep(1)
        await interaction.followup.send(f'What are you doing in my swamp?')

# This setup function registers the Cog with the main bot instance
async def setup(bot):
    await bot.add_cog(Donkey(bot))