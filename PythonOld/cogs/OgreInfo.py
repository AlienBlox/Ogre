import platform
import time
import discord
from discord import app_commands
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Track initialization timestamp
        self.start_time = time.time()

    @app_commands.command(name="ogreinfo", description="Displays system information and statistics about the bot")
    async def ogre_info(self, interaction: discord.Interaction):
        """Generates a beautifully formatted server card with live bot statistics."""
        await interaction.response.defer()

        try:
            # 1. Calculate Live Uptime safely
            current_time = time.time()
            uptime_seconds = int(current_time - self.start_time)
            
            days = uptime_seconds // 86400
            hours = (uptime_seconds % 86400) // 3600
            minutes = (uptime_seconds % 3600) // 60
            uptime_string = f"🟢 {days}d {hours}h {minutes}m"

            # 2. Gather Server Metrics with concrete numerical fallbacks
            total_servers = len(self.bot.guilds)
            
            # FIX: Explicit check ensures no NoneType fields leak into the sum tracker
            total_users = 0
            for guild in self.bot.guilds:
                if guild.member_count is not None:
                    total_users += guild.member_count

            latency = round(self.bot.latency * 1000) if self.bot.latency else 0

            # 3. Create the Presentation Embed
            embed = discord.Embed(
                title=f"🤖 {self.bot.user.name} - Bot Profile",
                description="An open-source, cloud-hosted community utility bot.",
                color=discord.Color.teal()
            )

            if self.bot.user.avatar:
                embed.set_thumbnail(url=self.bot.user.avatar.url)

            # 4. Organize Information Fields
            embed.add_field(name="📊 Statistics", value=f"**Servers:** {total_servers}\n**Users:** {total_users}", inline=True)
            embed.add_field(name="⚙️ System Performance", value=f"**Latency:** {latency}ms\n**Uptime:** {uptime_string}", inline=True)
            
            embed.add_field(
                name="🛠️ Tech Stack", 
                value=f"**Library:** discord.py v{discord.__version__}\n**Language:** Python {platform.python_version()}\n**Host:** Railway Cloud", 
                inline=False
            )

            # 5. Add Interactive Buttons
            view = discord.ui.View()
            view.add_item(discord.ui.Button(
                label="View GitHub Repository", 
                url="https://github.com/AlienBlox/Ogre", 
                style=discord.ButtonStyle.link
            ))

            # Send response card
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            # Catch block guarantees the bot process won't crash even if computation fails
            await interaction.followup.send("💥 An internal display error occurred.")
            print(f"Info Cog Runtime Error: {e}")

async def setup(bot):
    await bot.add_cog(Info(bot))