import os
import asyncio
import sqlite3
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# THE INTERCEPTION CHECK: Runs automatically right before ANY slash command fires
@bot.tree.interaction_check
async def global_command_filter(interaction: discord.Interaction) -> bool:
    # Always allow Direct Messages or commands run outside a standard server channel
    if not interaction.guild_id:
        return True
        
    command_name = interaction.command.name
    guild_id = str(interaction.guild_id)
    
    # Open connection to local database file
    conn = sqlite3.connect("bot_management.db")
    cursor = conn.cursor()
    
    # Check if this specific server has disabled this specific command
    cursor.execute(
        "SELECT is_disabled FROM command_toggles WHERE guild_id = ? AND command_name = ?",
        (guild_id, command_name)
    )
    result = cursor.fetchone()
    conn.close()
    
    # If a row is found and the is_disabled flag is True (1)
    if result and result[0] == 1:
        # Inform the user privately that the command is turned off
        await interaction.response.send_message(
            f"❌ This command has been disabled by this server's administrators.",
            ephemeral=True
        )
        return False # Halts execution track completely!
        
    return True # Passes through smoothly

@bot.event
async def on_ready():
    print(f'Successfully logged in as {bot.user}')
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="Bot active"),
        afk=False
    )
    
    try:
        synced = await bot.tree.sync()
        print(f"Successfully synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Error syncing tree: {e}")

async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f"Loaded extension: {filename}")


async def main():
    async with bot:
        await load_extensions()
        await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())
