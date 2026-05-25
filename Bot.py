import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load secret environment variables
load_dotenv()

# Configure permissions
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Triggers automatically when the bot logs into Discord
@bot.event
async def on_ready():
    print(f'Successfully logged in as {bot.user}')
    
    # Set the permanent status message
    # This will display as: "Playing Bot active"
    await bot.change_presence(
        activity=discord.Game(name="Bot active")
    )

# Simple activity checker command
@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000) 
    print(f'Run cmd: ping')
    await ctx.send(f'🏓 Pong! Response time: {latency}ms')

# Run the bot using your hidden token
bot.run(os.getenv('DISCORD_TOKEN'))