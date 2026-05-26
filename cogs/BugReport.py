import os
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # FIX: Hardcode your specific repository API link right here 
        # This completely avoids all string-splitting or naming crashes!
        self.github_url = "https://github.com/AlienBlox/Ogre/issues"

    @app_commands.command(name="report", description="Submits an Ogre issue directly to the GitHub Issues tracker")
    @app_commands.describe(
        title="A short summary of the issue",
        details="Provide deep details or step-by-step reproduction"
    )
    async def report_issue(self, interaction: discord.Interaction, title: str, details: str):
        """Asynchronously parses user feedback and securely uploads it to GitHub."""
        await interaction.response.defer(ephemeral=True) 

        token = os.getenv("GITHUB_TOKEN")
        if not token:
            await interaction.followup.send("❌ **Configuration Error:** GITHUB_TOKEN is missing on your host panel.")
            return

        clean_title = str(title).strip() if title else "Untitled Bug Report"
        clean_details = str(details).strip() if details else "No description provided."

        headers = {
            "Authorization": f"Bearer {token.strip()}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "Discord-Issue-Report-Bot"
        }

        issue_body = (
            f"### Discord User Bug Report\n"
            f"**Submitted By:** {interaction.user} (ID: {interaction.user.id})\n"
            f"**Server Origin:** {interaction.guild.name if interaction.guild else 'Direct Message'}\n\n"
            f"### Description / Details\n"
            f"{clean_details}\n\n"
            f"*Generated automatically via the Discord `/report` command.*"
        )

        payload = {
            "title": f"[Ogre Bug] {clean_title}",
            "body": issue_body
        }

        async with aiohttp.ClientSession() as session:
            try:
                # Log verification print statement for your Railway logs
                print(f"[Report Command Executing]: Targeting endpoint -> {self.github_url}")
                
                async with session.post(self.github_url, json=payload, headers=headers) as response:
                    if response.status == 201:
                        data = await response.json()
                        issue_url = data.get("html_url", "")
                        await interaction.followup.send(
                            f"✅ **Issue successfully tracked!** Your report has been posted to our GitHub repository.\n"
                            f"🔗 **Track progress here:** {issue_url}"
                        )
                    elif response.status == 422:
                        error_json = await response.json()
                        error_msg = error_json.get("message", "Validation Failed")
                        await interaction.followup.send(f"⚠️ GitHub 422 Error: {error_msg}. Check your write token permissions.")
                        print(f"❌ [GitHub 422 Rejection]: {error_json}")
                    elif response.status == 401:
                        await interaction.followup.send("⚠️ GitHub connection rejected: Invalid or expired GitHub token.")
                    elif response.status == 404:
                        await interaction.followup.send("⚠️ GitHub connection rejected: Repository tracker location not found.")
                    else:
                        error_text = await response.text()
                        await interaction.followup.send(f"⚠️ Failed to connect to GitHub. Status Code: {response.status}")
                        print(f"GitHub API Error: {response.status} - {error_text}")
                        
            except Exception as e:
                await interaction.followup.send("💥 An internal network failure blocked this issue from submitting.")
                print(f"Report Cog Network Failure Exception Details: {e}")

async def setup(bot):
    await bot.add_cog(Report(bot))
