import os
import time
import jwt
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Static target endpoints
        self.base_url = "https://api.github.com"
        self.issue_url = f"{self.base_url}/repos/AlienBlox/Ogre/issues"

    def _generate_jwt(self):
        """Generates a high-security signing token required to verify our App identity to GitHub."""
        app_id = os.getenv("GH_APP_ID")
        private_key = os.getenv("GH_PRIVATE_KEY")
        
        if not app_id or not private_key:
            return None

        # Clean up accidental literal string characters if pasted oddly
        private_key = private_key.replace("\\n", "\n")

        # Payload requires current time and expiration window stamps
        payload = {
            "iat": int(time.time()) - 60,
            "exp": int(time.time()) + (10 * 60), # Valid for 10 minutes
            "iss": int(app_id),
        }
        
        # Cryptographically sign the JWT packet using RS256 encryption algorithm
        return jwt.encode(payload, private_key, algorithm="RS256")

    async def _get_installation_token(self, session):
        """Asynchronously requests a short-lived write token for our specific repository install target."""
        app_jwt = self._generate_jwt()
        installation_id = os.getenv("GH_INSTALLATION_ID")
        
        if not app_jwt or not installation_id:
            return None

        url = f"{self.base_url}/app/installations/{installation_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github+json",
        }

        async with session.post(url, headers=headers) as response:
            if response.status == 201:
                data = await response.json()
                return data.get("token")
            else:
                print(f"[GH App Token Generation Failed]: {response.status}")
                return None

    @app_commands.command(name="report", description="Submits an Ogre issue directly via the GitHub App integration")
    @app_commands.describe(title="Short summary", details="Deep details/reproduction steps")
    async def report_issue(self, interaction: discord.Interaction, title: str, details: str):
        await interaction.response.defer(ephemeral=True)

        async with aiohttp.ClientSession() as session:
            # 1. Fetch our short-lived installation access token
            token = await self._get_installation_token(session)
            if not token:
                await interaction.followup.send("❌ **Integration Failure:** Could not authorize the GitHub App connection.")
                return

            # 2. Build the structural authentication payload headers
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "Discord-Issue-Report-Bot"
            }

            issue_body = (
                f"### Discord User Bug Report\n"
                f"**Submitted By:** {interaction.user} (ID: {interaction.user.id})\n"
                f"**Server Origin:** {interaction.guild.name if interaction.guild else 'Direct Message'}\n\n"
                f"### Description / Details\n"
                f"{details.strip()}\n\n"
                f"*Generated securely via the Ogre GitHub App integration.*"
            )

            data = {
                "title": f"[Ogre Bug] {title.strip()}",
                "body": issue_body
            }

            try:
                # 3. Ship the bug packet directly to your repository issues board
                async with session.post(self.issue_url, headers=headers, json=data) as response:
                    if response.status == 201:
                        response_json = await response.json()
                        issue_url = response_json.get("html_url", "")
                        await interaction.followup.send(f"✅ Bug posted successfully! Track progress here: {issue_url}")
                    else:
                        error_text = await response.text()
                        await interaction.followup.send(f"❌ GitHub API Error: {response.status}")
                        print(f"Error: {response.status} - {error_text}")
            except Exception as e:
                await interaction.followup.send("💥 A network failure blocked the app communication pipeline.")
                print(f"Exception: {e}")

async def setup(bot):
    await bot.add_cog(Report(bot))
