import os
import asyncio
import mysql.connector
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

IMMUNE_COMMANDS = ["report", "ping", "takecopy", "ogreinfo", "toggle_command"]

def get_mysql_connection():
    """Helper to instantly establish a connection to Railway's MySQL service container."""
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT", 3306))
    )

# THE INTERCEPTION CHECK: Runs automatically right before ANY slash command fires
@bot.tree.interaction_check
async def global_command_filter(interaction: discord.Interaction) -> bool:
    if not interaction.guild_id:
        return True
        
    command_name = interaction.command.name.lower().strip()
    if command_name in IMMUNE_COMMANDS:
        return True
        
    guild_id = str(interaction.guild_id)
    
    try:
        # Open safe non-blocking connection pool channels
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT is_disabled FROM command_toggles WHERE guild_id = %s AND command_name = %s",
            (guild_id, command_name)
        )
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        # MySQL extracts data cleanly out of rows
        if result and result[0] == 1:
            await interaction.response.send_message(
                "❌ This command has been disabled by this server's administrators.",
                ephemeral=True
            )
            return False 
            
    except Exception as e:
        print(f"[MySQL Interceptor Error]: {e}")
        return True 
        
    return True

@bot.event
async def on_ready():
    print(f'Successfully logged in as {bot.user}')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="Bot active"), afk=False)

@bot.command()
@commands.is_owner()
async def sync(ctx: commands.Context):
    """Clears all cached guild commands and forces a clean synchronization update."""
    msg = await ctx.send("⏳ *Wiping old command cache and contacting Discord API...*")
    try:
        bot.tree.clear_commands(guild=ctx.guild)
        bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
        await msg.edit(content=f"⚡ **Cache Wiped & Sync Complete!** Forced {len(synced)} slash commands live on this server.")
    except Exception as e:
        await msg.edit(content=f"❌ **Sync Failure:** {e}")

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
