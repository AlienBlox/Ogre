import sqlite3
import discord
from discord import app_commands
from discord.ext import commands

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Establish a persistent local database file inside your cloud container
        self.conn = sqlite3.connect("bot_management.db")
        self.cursor = self.conn.cursor()
        
        # Create a configuration table for server-specific command overrides
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_toggles (
                guild_id TEXT,
                command_name TEXT,
                is_disabled INTEGER,
                PRIMARY KEY (guild_id, command_name)
            )
        """)
        self.conn.commit()

    # Core lists of commands that can NEVER be disabled under any circumstance
    # Includes 'toggle_command' to completely eliminate any deadlock risks!
    CORE_COMMANDS = ["report", "ping", "takeme", "ogreinfo", "toggle_command"]

    @app_commands.command(name="toggle_command", description="Enables or disables a specific bot command for this server")
    @app_commands.describe(
        command_name="The exact name of the command you want to change (e.g., species, donkey)",
        status="Choose whether to enable or disable the command"
    )
    @app_commands.choices(status=[
        app_commands.Choice(name="Enable", value="enable"),
        app_commands.Choice(name="Disable", value="disable")
    ])
    @app_commands.checks.has_permissions(administrator=True) # Forces Server Admin/Owner execution rules
    async def toggle_command(self, interaction: discord.Interaction, command_name: str, status: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        
        clean_name = command_name.strip().lower()
        guild_id = str(interaction.guild_id)

        # Protection checkpoint: Prevent admins from locking themselves out of fundamental core scripts
        if clean_name in self.CORE_COMMANDS:
            await interaction.followup.send(
                f"❌ **Action Denied:** The command `{clean_name}` is a core system service and cannot be disabled."
            )
            return

        # Check if the command actually exists in the bot's loaded slash tree index
        all_commands = [cmd.name for cmd in self.bot.tree.get_commands()]
        if clean_name not in all_commands:
            await interaction.followup.send(
                f"❌ **Invalid Target:** The command `{clean_name}` does not exist. Loaded commands: {', '.join(all_commands)}"
            )
            return

        is_disabled = 1 if status.value == "disable" else 0

        # Save or update toggle status in the database
        self.cursor.execute("""
            INSERT INTO command_toggles (guild_id, command_name, is_disabled)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, command_name) DO UPDATE SET is_disabled = excluded.is_disabled
        """, (guild_id, clean_name, is_disabled))
        self.conn.commit()

        message = f"🚫 **Disabled** `{clean_name}`" if is_disabled else f"✅ **Enabled** `{clean_name}`"
        await interaction.followup.send(f"{message} successfully for this server.")

async def setup(bot):
    await bot.add_cog(Management(bot))
