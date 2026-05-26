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
        self.base_url = "https://api.github.com"
        # Hardcoded endpoint targeting your specific Ogre repository tracker
        self.issue_url = f"{self.base_url}/repos/AlienBlox/Ogre/issues"

    def _generate_jwt(self):
        """Natively assembles and signs a high-security JWT using RS256 encryption."""
        app_id = os.getenv("GH_APP_ID")
        private_key = os.getenv("GH_PRIVATE_KEY")
        
        if not app_id or not private_key:
            print("[Report Cog Error] Missing GH_APP_ID or GH_PRIVATE_KEY in dashboard variables.")
            return None

        # Clean up line break text anomalies if pasted oddly into your cloud variables box
        private_key = private_key.replace("\\n", "\n").strip()

        # CRUCIAL TIMING HACK: Subtracting 60 seconds from the 'iat' (issued at) parameter 
        # prevents clock-drift synchronization hangs with GitHub's servers.
        now = int(time.time())
        payload = {
            "iat": now - 60,               # Set issuance to 1 minute ago to allow for clock drift
            "exp": now + (10 * 60),          # Token remains valid for 10 minutes maximum
            "iss": int(app_id),              # Your GitHub App ID
        }
        
        try:
            # Generate the signed cryptographic identity token using RS256
            return jwt.encode(payload, private_key, algorithm="RS256")
        except Exception as e:
            print(f"❌ [JWT Encoding Failure]: Private key structure validation failed. Details: {e}")
            return None

    async def _get_installation_token(self, session):
        """Asynchronously requests a short-lived write token for our repository application."""
        app_jwt = self._generate_jwt()
        installation_id = os.getenv("GH_INSTALLATION_ID")
        
        if not app_jwt or not installation_id:
            return None

        url = f"{self.base_url}/app/installations/{installation_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "Discord-Issue-Report-Bot"
        }

        # Safe, non-blocking outbound token request handshake
        async with session.post(url, headers=headers) as response:
            if response.status == 201:
                data = await response.json()
                return data.get("token")
            else:
                err_text = await response.text()
                print(f"❌ [App Token Rejection] Status Code: {response.status} - Response: {err_text}")
                return None

    @app_commands.command(name="report", description="Submits an Ogre bug directly via your secure GitHub App profile")
    @app_commands.describe(title="Short summary of the bug", details="Deep explanation or reproduction steps")
    async def report_issue(self, interaction: discord.Interaction, title: str, details: str):
        # Acknowledge the interaction immediately to stop Discord's 3-second menu timeout
        await interaction.response.defer(ephemeral=True)

        async with aiohttp.ClientSession() as session:
            print("[Report Command Executing]: Generating dynamic GitHub installation access token...")
            
            # 1. Fetch our short-lived installation write token automatically
            token = await self._get_installation_token(session)
            if not token:
                await interaction.followup.send(
                    "❌ **Integration Failure:** The bot failed to generate a live secure token handshake with GitHub. Check your Railway logs."
                )
                return

            # 2. Build headers using our fresh dynamic access token
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "User-Agent": "Discord-Issue-Report-Bot"
            }

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

            try:
                # 3. Ship the bug packet directly to your repository issues board
                async with session.post(self.issue_url, headers=headers, json=data) as response:
                    if response.status == 201:
                        response_json = await response.json()
                        issue_url = response_json.get("html_url", "")
                        await interaction.followup.send(f"✅ **Bug posted successfully!** Track progress under the App profile here: {issue_url}")
                    else:
                        error_text = await response.text()
                        await interaction.followup.send(f"❌ **GitHub Rejected Action:** Status Code {response.status}")
                        print(f"App Endpoint Error: {response.status} - {error_text}")
            except Exception as e:
                await interaction.followup.send("💥 A network failure blocked the app communication pipeline.")
                print(f"Exception: {e}")

async def setup(bot):
    await bot.add_cog(Report(bot))
