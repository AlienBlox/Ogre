import os
import mysql.connector
import discord
from discord import app_commands
from discord.ext import commands

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._init_db()

    def _init_db(self):
        """Connects to MySQL and initializes the command toggles configuration table."""
        conn = mysql.connector.connect(
            host=os.getenv("MYSQLHOST"),
            user=os.getenv("MYSQLUSER"),
            password=os.getenv("MYSQLPASSWORD"),
            database=os.getenv("MYSQLDATABASE"),
            port=int(os.getenv("MYSQLPORT", 3306))
        )
        cursor = conn.cursor()
        # Creates a matching schema layout for server overrides
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_toggles (
                guild_id VARCHAR(50),
                command_name VARCHAR(100),
                is_disabled INT,
                PRIMARY KEY (guild_id, command_name)
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

    CORE_COMMANDS = ["report", "ping", "takecopy", "ogreinfo", "toggle_command"]

    @app_commands.command(name="toggle_command", description="Enables or disables a specific bot command for this server")
    @app_commands.describe(
        command_name="The exact name of the command you want to change (e.g., species, donkey)",
        status="Choose whether to enable or disable the command"
    )
    @app_commands.choices(status=[
        app_commands.Choice(name="Enable", value="enable"),
        app_commands.Choice(name="Disable", value="disable")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def toggle_command(self, interaction: discord.Interaction, command_name: str, status: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        
        clean_name = command_name.strip().lower()
        guild_id = str(interaction.guild_id)

        if clean_name in self.CORE_COMMANDS:
            await interaction.followup.send(
                f"❌ **Action Denied:** The command `{clean_name}` is a core system service and cannot be disabled."
            )
            return

        all_commands = [cmd.name for cmd in self.bot.tree.get_commands()]
        if clean_name not in all_commands:
            await interaction.followup.send(
                f"❌ **Invalid Target:** The command `{clean_name}` does not exist. Loaded choices: {', '.join(all_commands)}"
            )
            return

        is_disabled = 1 if status.value == "disable" else 0

        # Run connection pipeline to write database rows
        conn = mysql.connector.connect(
            host=os.getenv("MYSQLHOST"),
            user=os.getenv("MYSQLUSER"),
            password=os.getenv("MYSQLPASSWORD"),
            database=os.getenv("MYSQLDATABASE"),
            port=int(os.getenv("MYSQLPORT", 3306))
        )
        cursor = conn.cursor()
        
        # MySQL replacement syntax layout for upsert operations
        cursor.execute("""
            INSERT INTO command_toggles (guild_id, command_name, is_disabled)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE is_disabled = VALUES(is_disabled)
        """, (guild_id, clean_name, is_disabled))
        
        conn.commit()
        cursor.close()
        conn.close()

        message = f"🚫 **Disabled** `{clean_name}`" if is_disabled else f"✅ **Enabled** `{clean_name}`"
        await interaction.followup.send(f"{message} successfully for this server.")

    @toggle_command.error
    async def toggle_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "❌ **Access Denied:** You must have **Administrator** permissions to toggle commands on this server.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Management(bot))
