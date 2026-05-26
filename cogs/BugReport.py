import os
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Hardcoded endpoint targeting your specific Ogre repository
        self.url = "https://api.github.com/repos/AlienBlox/Ogre/issues"

    @app_commands.command(name="report", description="Submits an Ogre issue securely via your GitHub App profile")
    @app_commands.describe(title="Short summary of the bug", details="Deep explanation or reproduction steps")
    async def report_issue(self, interaction: discord.Interaction, title: str, details: str):
        # Acknowledge the slash command immediately to stop Discord menu timeouts
        await interaction.response.defer(ephemeral=True) 

        # Pull the App-scoped token from your secure Railway dashboard panel
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            await interaction.followup.send("❌ **Configuration Error:** GITHUB_TOKEN is missing on your host dashboard.")
            return

        # Structure headers strictly using official GitHub App REST standards
        headers = {
            "Authorization": f"Bearer {token.strip()}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "Discord-Issue-Report-Bot"
        }

        # Format the markdown text block for the tracking ticket layout
        issue_body = (
            f"### Discord User Bug Report\n"
            f"**Submitted By:** {interaction.user} (ID: {interaction.user.id})\n"
            f"**Server Origin:** {interaction.guild.name if interaction.guild else 'Direct Message'}\n\n"
            f"### Description / Details\n"
            f"{details.strip()}\n\n"
            f"*Generated automatically via the secure Discord `/report` command.*"
        )

        data = {
            "title": f"[Ogre Bug] {title.strip()}",
            "body": issue_body
        }

        # Safe, non-blocking asynchronous web client session loop
        async with aiohttp.ClientSession() as session:
            try:
                print(f"[REST API Dispatch]: Posting issue ticket directly to GitHub...")
                
                async with session.post(self.url, headers=headers, json=data) as response:
                    # 201 means "Created" successfully in GitHub REST guidelines
                    if response.status == 201:
                        response_json = await response.json()
                        issue_url = response_json.get("html_url", "")
                        await interaction.followup.send(f"✅ **Bug tracked successfully!** View the live issue ticket here: {issue_url}")
                    else:
                        error_text = await response.text()
                        await interaction.followup.send(f"❌ **GitHub Rejected Action:** Status Code {response.status}")
                        print(f"GitHub Error Log: {response.status} - {error_text}")
                        
            except Exception as e:
                await interaction.followup.send("💥 **Network Error:** Could not complete the connection to the GitHub server host.")
                print(f"Report System Network Failure Exception: {e}")

async def setup(bot):
    await bot.add_cog(Report(bot))
