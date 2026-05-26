import os
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    def get_api_url(self):
        """Dynamically fetches variables and constructs the GitHub endpoint LIVE on command execution."""
        # FIX: Forcing os.getenv to pull fresh strings exactly when the user clicks the slash command
        owner = os.getenv("GITHUB_OWNER")
        repo = os.getenv("GITHUB_REPO")
        
        if not owner or not repo:
            print("[Report Cog Error] Missing GITHUB_OWNER or GITHUB_REPO in dashboard panel.")
            return None

        # Strip full browser layout prefixes if pasted into your Railway variables view
        if "github.com/" in owner:
            owner = owner.split("github.com/")[-1]
        if "github.com/" in repo:
            repo = repo.split("github.com/")[-1]

        owner = owner.strip().strip("/")
        repo = repo.strip().strip("/")
        
        # Safe fallback if an entire combined owner/repo block was entered into one field
        if "/" in owner:
            return f"https://github.com/{owner}/issues"

        return f"https://github.com/{owner}/{repo}/issues"

    @app_commands.command(name="report", description="Submits an Ogre issue directly to the GitHub Issues tracker")
    @app_commands.describe(
        title="A short summary of the issue (e.g., Ogre asset textures failing to load)",
        details="Provide deep details, step-by-step reproduction, or unexpected bug outcomes"
    )
    async def report_issue(self, interaction: discord.Interaction, title: str, details: str):
        """Asynchronously parses user feedback and securely uploads it to GitHub."""
        await interaction.response.defer(ephemeral=True) 

        # Fetch clean, real-time URL path mappings
        github_url = self.get_api_url()
        token = os.getenv("GITHUB_TOKEN")

        if not github_url or not token:
            await interaction.followup.send(
                "❌ **Configuration Error:** The bot owner has not configured the GitHub environment variables properly."
            )
            return

        # Structure headers using the live verified token payload
        headers = {
            "Authorization": f"Bearer {token.strip()}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Discord-Issue-Report-Bot"
        }

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
            "body": issue_body
        }

        async with aiohttp.ClientSession() as session:
            try:
                # Debug print directly into your Railway console to verify the final connection URL path string
                print(f"[Report Command Routing API Link]: hitting target -> {github_url}")
                
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
                    elif response.status == 404:
                        await interaction.followup.send("⚠️ GitHub connection rejected: Repository tracker location not found.")
                        print(f"GitHub API 404 Link Verification. Current output string: {github_url}")
                    else:
                        error_text = await response.text()
                        await interaction.followup.send(f"⚠️ Failed to connect to GitHub. API Status Code: {response.status}")
                        print(f"GitHub API Unhandled Error: {response.status} - {error_text}")
                        
            except Exception as e:
                await interaction.followup.send("💥 An internal network failure blocked this issue from submitting.")
                print(f"Report Cog Network Failure Exception Details: {e}")

async def setup(bot):
    await bot.add_cog(Report(bot))
