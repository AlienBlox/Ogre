import discord
from discord import app_commands
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash command for the latency check
    @app_commands.command(name="ping", description="Checks the bot's response time and connectivity")
    async def ping(self, interaction: discord.Interaction):
        """Calculates bot latency in milliseconds."""
        # Calculate latency
        latency = round(self.bot.latency * 1000)
        
        # Respond directly to the slash interaction
        await interaction.response.send_message(f'🏓 Pong! Response time: {latency}ms')

# This setup function registers the Cog with the main bot instance
async def setup(bot):
    await bot.add_cog(Utility(bot))