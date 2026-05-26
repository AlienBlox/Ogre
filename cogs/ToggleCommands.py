import os
import aiomysql
import discord
from discord import app_commands
from discord.ext import commands

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        """Runs automatically when the cog mounts to initialize the MySQL schemas asynchronously."""
        try:
            conn = await aiomysql.connect(
                host=os.getenv("MYSQLHOST"),
                user=os.getenv("MYSQLUSER"),
                password=os.getenv("MYSQLPASSWORD"),
                port=int(os.getenv("MYSQLPORT", 3306))
            )
            async with conn.cursor() as cursor:
                await cursor.execute("CREATE DATABASE IF NOT EXISTS ogre_database")
                await cursor.execute("USE ogre_database")
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS command_toggles (
                        guild_id VARCHAR(50),
                        command_name VARCHAR(100),
                        is_disabled INT,
                        PRIMARY KEY (guild_id, command_name)
                    )
                """)
                await conn.commit()
            conn.close()
            print("[Management Database]: Async Initialization Complete.")
        except Exception as e:
            print(f"[Management DB Init Error]: {e}")

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
                f"❌ **Invalid Target:** The command `{clean_name}` does not exist. Choices: {', '.join(all_commands)}"
            )
            return

        is_disabled = 1 if status.value == "disable" else 0

        try:
            # Non-blocking async transaction database link
            conn = await aiomysql.connect(
                host=os.getenv("MYSQLHOST"),
                user=os.getenv("MYSQLUSER"),
                password=os.getenv("MYSQLPASSWORD"),
                port=int(os.getenv("MYSQLPORT", 3306))
            )
            async with conn.cursor() as cursor:
                await cursor.execute("USE ogre_database")
                await cursor.execute("""
                    INSERT INTO command_toggles (guild_id, command_name, is_disabled)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE is_disabled = VALUES(is_disabled)
                """, (guild_id, clean_name, is_disabled))
                await conn.commit()
            conn.close()

            message = f"🚫 **Disabled** `{clean_name}`" if is_disabled else f"✅ **Enabled** `{clean_name}`"
            await interaction.followup.send(f"{message} successfully for this server.")
        except Exception as e:
            await interaction.followup.send("❌ Internal Database Failure. Check logs.")
            print(f"Toggle Command DB Error: {e}")

    @toggle_command.error
    async def toggle_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "❌ **Access Denied:** You must have **Administrator** permissions to toggle commands on this server.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Management(bot))
