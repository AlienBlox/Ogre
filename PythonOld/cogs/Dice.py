import discord
import random
from discord import app_commands
from discord.ext import commands

class DiceRoll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash command for rolling a die
    @app_commands.command(name="roll", description="Rolls a die (Choose your own number of sides, 6 default.)")
    @app_commands.describe(sides="Number of sides on the die")
    async def roll(self, interaction: discord.Interaction, sides: int = 6):
        # Calculate latency
        
        randomNum = random.randint(1, sides)  # Simulate rolling a die with the specified number of sides

        # Respond directly to the slash interaction
        await interaction.response.send_message(f'Rolled: {randomNum}')

# This setup function registers the Cog with the main bot instance
async def setup(bot):
    await bot.add_cog(DiceRoll(bot))