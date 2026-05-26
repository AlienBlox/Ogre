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

# THE IMMUNE CORE: These commands are skipped by the database check entirely
# This forces them to register to Discord's UI without getting blocked by empty tables
IMMUNE_COMMANDS = ["report", "ping", "takeme", "ogreinfo", "toggle_command"]

# THE INTERCEPTION CHECK: Runs automatically right before ANY slash command fires
@bot.tree.interaction_check
async def global_command_filter(interaction: discord.Interaction) -> bool:
    # 1. Always pass Direct Messages or commands run outside a standard server channel
    if not interaction.guild_id:
        return True
        
    command_name = interaction.command.name
    
    # 2. FIX: If the command is part of our system core, let it pass immediately!
    if command_name in IMMUNE_COMMANDS:
        return True
        
    guild_id = str(interaction.guild_id)
    
    try:
        # Open connection to local database file safely
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
            await interaction.response.send_message(
                "❌ This command has been disabled by this server's administrators.",
                ephemeral=True
            )
            return False # Halts execution track completely!
            
    except Exception as e:
        print(f"[Database Interceptor Glitch]: {e}")
        return True # Fallback pass-through if the table doesn't exist yet
        
    return True # Passes through smoothly

@bot.event
async def on_ready():
    print(f'Successfully logged in as {bot.user}')
    print(f'testing testing 123')
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="Bot active"),
        afk=False
    )
    
    # DEV GUILD INSTANT SYNC OVERRIDE
    try:
        # ⚠️ REPLACE this number with your exact copied Server ID number!
        guild_target = discord.Object(id=1421919181556944948) 
        
        # Force duplicate our code's local command index directly into your test server
        bot.tree.copy_global_to(guild=guild_target)
        synced = await bot.tree.sync(guild=guild_target)
        print(f"⚡ INSTANT GUILD SYNC: Forced {len(synced)} slash commands directly onto server!")
    except Exception as e:
        print(f"Sync Tree Error: {e}")

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
