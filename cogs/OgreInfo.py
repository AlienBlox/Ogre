import platform
import time
import discord
from discord import app_commands
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Track the exact moment the cog initializes to calculate uptime
        self.start_time = time.time()

    @app_commands.command(name="info", description="Displays system information and statistics about the bot")
    async def bot_info(self, interaction: discord.Interaction):
        """Generates a beautifully formatted server card with live bot statistics."""
        await interaction.response.defer()

        # 1. Calculate Live Uptime
        current_time = time.time()
        uptime_seconds = int(current_time - self.start_time)
        
        # Format seconds into days, hours, minutes
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        uptime_string = f"🟢 {days}d {hours}h {minutes}m"

        # 2. Gather Server Metrics
        total_servers = len(self.bot.guilds)
        # Sum up all members across all connected servers
        total_users = sum(guild.member_count for guild in self.bot.guilds if guild.member_count)
        latency = round(self.bot.latency * 1000)

        # 3. Create the Presentation Embed
        embed = discord.Embed(
            title=f"🤖 {self.bot.user.name} - Bot Profile",
            description="An open-source, cloud-hosted community utility bot.",
            color=discord.Color.teal()
        )

        # Set the bot's avatar as the large side thumbnail if it exists
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        # 4. Organize Information Fields into a Grid Structure
        embed.add_field(name="📊 Statistics", value=f"**Servers:** {total_servers}\n**Users:** {total_users}", inline=True)
        embed.add_field(name="⚙️ System Performance", value=f"**Latency:** {latency}ms\n**Uptime:** {uptime_string}", inline=True)
        
        # Add tech stack data fields
        embed.add_field(
            name="🛠️ Tech Stack", 
            value=f"**Library:** discord.py v{discord.__version__}\n**Language:** Python {platform.python_version()}\n**Host:** Railway Cloud", 
            inline=False
        )

        # 5. Add Interactive Buttons/Links (Optional)
        view = discord.ui.View()
        # You can add a button that links straight to your open-source GitHub repo
        view.add_item(discord.ui.Button(label="View GitHub Repository", url="https://github.com", style=discord.ButtonStyle.link))

        # Send the final response card
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Info(bot))