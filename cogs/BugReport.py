import os
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    def get_api_url(self):
        """Constructs the GitHub API endpoint, safely parsing full web URLs if pasted."""
        owner = os.getenv("GITHUB_OWNER")
        repo = os.getenv("GITHUB_REPO")
        
        if not owner or not repo:
            return None

        # Clean up full browser links if accidentally pasted into Railway variables
        if "github.com" in owner:
            owner = owner.split("://github.com")[-1]
        if "github.com" in repo:
            repo = repo.split("://github.com")[-1]

        # Strip lingering spaces, slashes, or accidental subpages
        owner = owner.strip().strip("/")
        repo = repo.strip().strip("/")
        
        # Handle cases where the whole 'owner/repo' path was pasted into one variable
        if "/" in owner and repo in owner:
            return f"https://api.://github.comrepos/{owner}/issues"

        return f"https://api.://github.comrepos/{owner}/{repo}/issues"

    @app_commands.command(name="report", description="Submits an Ogre issue directly to the GitHub Issues tracker")
    @app_commands.describe(
        title="A short summary of the issue (e.g., Ogre asset textures failing to load)",
        details="Provide deep details, step-by-step reproduction, or unexpected bug outcomes"
    )
    async def report_issue(self, interaction: discord.Interaction, title: str, details: str):
        """Asynchronously parses user feedback and securely uploads it to GitHub."""
        # Ephemeral=True keeps the transaction confirmation private to the user reporting it
        await interaction.response.defer(ephemeral=True) 

        github_url = self.get_api_url()
        token = os.getenv("GITHUB_TOKEN")

        # Validate existence of infrastructure configuration
        if not github_url or not token:
            await interaction.followup.send(
                "❌ **Configuration Error:** The bot owner has not configured the GitHub environment variables properly."
            )
            print("[Report Cog Error] Missing GITHUB_OWNER, GITHUB_REPO, or GITHUB_TOKEN in environment variables.")
            return

        # Structure modern Bearer credentials header
        headers = {
            "Authorization": f"Bearer {token.strip()}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Discord-Issue-Report-Bot"
        }

        # Build clean markdown text block layout for the GitHub tracker sheet
        issue_body = (
            f"### Discord User Bug Report\n"
            f"**Submitted By:** {interaction.user} (ID: {interaction.user.id})\n"
            f"**Server Origin:** {interaction.guild.name if interaction.guild else 'Direct Message'}\n\n"
            f"### Description / Details\n"
            f"{details}\n\n"
            f"*Generated automatically via the Discord `/report` command.*"
        )

        payload = {
            "title": f"[Ogre Bug] {title.strip()}",
            "body": issue_body,
            "labels": ["bug", "discord-report"]
        }

        # Safe asynchronous network query block
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(github_url, json=payload, headers=headers) as response:
                    if response.status == 201:
                        data = await response.json()
                        issue_url = data.get("html_url", "")
                        
                        await interaction.followup.send(
                            f"✅ **Issue successfully tracked!** Your Ogre bug report has been posted directly to our GitHub repository.\n"
                            f"🔗 **Track progress here:** {issue_url}"
                        )
                    elif response.status == 401:
                        await interaction.followup.send("⚠️ GitHub connection rejected: Invalid or expired GitHub token.")
                        print("GitHub API Error 401: Unauthorized. Check GITHUB_TOKEN permissions.")
                    elif response.status == 404:
                        await interaction.followup.send("⚠️ GitHub connection rejected: Repository tracker location not found.")
                        print(f"GitHub API Error 404: Not Found. Attempted target URL was: {github_url}")
                    else:
                        error_text = await response.text()
                        await interaction.followup.send(f"⚠️ Failed to connect to GitHub. API Status Code: {response.status}")
                        print(f"GitHub API Unhandled Error: {response.status} - {error_text}")
                        
            except Exception as e:
                await interaction.followup.send("💥 An internal network failure blocked this issue from submitting.")
                print(f"Report Cog Network Failure Exception: {e}")

async def setup(bot):
    await bot.add_cog(Report(bot))