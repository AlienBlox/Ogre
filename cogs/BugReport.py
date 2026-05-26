import os
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Copilot's exact REST API URL structure
        self.url = "https://github.com"

    @app_commands.command(name="report", description="Submits an Ogre issue directly to the GitHub Issues tracker")
    @app_commands.describe(title="Short summary", details="Deep details/reproduction")
    async def report_issue(self, interaction: discord.Interaction, title: str, details: str):
        # Acknowledge the interaction immediately to stop Discord timeouts
        await interaction.response.defer(ephemeral=True) 

        token = os.getenv("GITHUB_TOKEN")
        if not token:
            await interaction.followup.send("❌ GITHUB_TOKEN is missing on your host panel.")
            return

        # Copilot's exact headers
        headers = {
            "Authorization": f"Bearer {token.strip()}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "Discord-Issue-Report-Bot" # GitHub requires a User-Agent header
        }

        # Copilot's exact data structure mapped to user inputs
        data = {
            "title": f"[Ogre Bug] {title}",
            "body": f"**Reported by {interaction.user}:**\n\n{details}",
        }

        # The Asynchronous (Async) version of requests.post
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.url, headers=headers, json=data) as response:
                    # 201 means "Created" successfully in GitHub's REST API
                    if response.status == 201:
                        response_json = await response.json()
                        issue_url = response_json.get("html_url", "")
                        await interaction.followup.send(f"✅ Bug posted! Track progress here: {issue_url}")
                    else:
                        error_text = await response.text()
                        await interaction.followup.send(f"❌ GitHub API Error: {response.status}")
                        print(f"Error: {response.status} - {error_text}")
                        
            except Exception as e:
                await interaction.followup.send("💥 Network failure connecting to GitHub.")
                print(f"Exception: {e}")

async def setup(bot):
    await bot.add_cog(Report(bot))
