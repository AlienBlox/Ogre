import os
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Construct the official GitHub API endpoint using your secure variables
        owner = os.getenv("GITHUB_OWNER")
        repo = os.getenv("GITHUB_REPO")
        self.github_url = f"https://github.com/{owner}/{repo}/issues"

    @app_commands.command(name="report", description="Submits an Ogre issue directly to the GitHub Issues tracker")
    @app_commands.describe(
        title="A short summary of the issue (e.g., Ogre asset textures failing to load)",
        details="Provide deep details, step-by-step reproduction, or unexpected bug outcomes"
    )
    async def report_issue(self, interaction: discord.Interaction, title: str, details: str):
        """Asynchronously parses user feedback and securely uploads it to GitHub."""
        await interaction.response.defer(ephemeral=True) # Ephemeral=True keeps the user's report hidden from public view

        # 1. Structure the security authentication headers requested by GitHub
        headers = {
            "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Discord-Issue-Report-Bot"
        }

        # 2. Build the formatting layout for the GitHub Issue body text
        issue_body = (
            f"### Discord User Bug Report\n"
            f"**Submitted By:** {interaction.user} (ID: {interaction.user.id})\n\n"
            f"### Description / Details\n"
            f"{details}\n\n"
            f"*Generated automatically via the Discord `/report` command.*"
        )

        # 3. Create the JSON packet payload
        payload = {
            "title": f"[Ogre Bug] {title}",
            "body": issue_body,
            "labels": ["bug", "discord-report"] # Optional: Automatically applies labels to the issue
        }

        # 4. Process the asynchronous web request via aiohttp
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.github_url, json=payload, headers=headers) as response:
                    if response.status == 201:
                        data = await response.json()
                        issue_url = data.get("html_url", "")
                        
                        # Inform the user securely with a confirmation message and link
                        await interaction.followup.send(
                            f"✅ **Issue successfully tracked!** Your Ogre bug report has been posted directly to our GitHub repository.\n"
                            f"🔗 **Track progress here:** {issue_url}"
                        )
                    else:
                        error_text = await response.text()
                        await interaction.followup.send("⚠️ Failed to connect to GitHub. Please notify an administrator.")
                        print(f"GitHub API Error: {response.status} - {error_text}")
                        
            except Exception as e:
                await interaction.followup.send("💥 An internal network failure blocked this issue from submitting.")
                print(f"Report Cog Failure: {e}")

async def setup(bot):
    await bot.add_cog(Report(bot))
