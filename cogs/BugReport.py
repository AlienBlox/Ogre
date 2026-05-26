import os
import time
import base64
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_url = "https://github.com"
        self.issue_url = f"{self.base_url}/repos/AlienBlox/Ogre/issues"

    def _base64url_encode(self, data: bytes) -> str:
        """Helper to encode cryptographic components securely for web payload transport."""
        return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

    def _generate_jwt_native(self) -> str:
        """Assembles and signs a JWT manually using cryptography to prevent thread blocking hangs."""
        app_id = os.getenv("GH_APP_ID")
        private_key_text = os.getenv("GH_PRIVATE_KEY")
        
        if not app_id or not private_key_text:
            return None

        # Clean line breaks from the Railway environment input variable
        private_key_text = private_key_text.replace("\\n", "\n").strip()

        # Step 1: Standard JWT Headers and Claims
        import json
        header = json.dumps({"alg": "RS256", "typ": "JWT"}).encode('utf-8')
        payload = json.dumps({
            "iat": int(time.time()) - 60,
            "exp": int(time.time()) + (10 * 60), # 10 minute life window
            "iss": int(app_id)
        }).encode('utf-8')

        segments = [self._base64url_encode(header), self._base64url_encode(payload)]
        signing_input = ".".join(segments).encode('utf-8')

        try:
            # Step 2: Load the private key using the cryptography primitive core
            private_key = serialization.load_pem_private_key(
                private_key_text.encode('utf-8'),
                password=None
            )
            # Step 3: Cryptographically sign the header payload segments
            signature = private_key.sign(
                signing_input,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            segments.append(self._base64url_encode(signature))
            return ".".join(segments)
        except Exception as e:
            print(f"[Crypto Generation Error]: Failed to sign key. Details: {e}")
            return None

    async def _get_installation_token(self, session):
        """Asynchronously requests a short-lived write token for our repository application."""
        app_jwt = self._generate_jwt_native()
        installation_id = os.getenv("GH_INSTALLATION_ID")
        
        if not app_jwt or not installation_id:
            return None

        url = f"{self.base_url}/app/installations/{installation_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "Discord-Issue-Report-Bot"
        }

        async with session.post(url, headers=headers) as response:
            if response.status == 201:
                data = await response.json()
                return data.get("token")
            else:
                err_text = await response.text()
                print(f"[App Access Token Error] Status: {response.status} - {err_text}")
                return None

    @app_commands.command(name="report", description="Submits an Ogre issue via your clean GitHub App identity")
    @app_commands.describe(title="Bug summary", details="Reproduction steps")
    async def report_issue(self, interaction: discord.Interaction, title: str, details: str):
        await interaction.response.defer(ephemeral=True)

        async with aiohttp.ClientSession() as session:
            # Generate the temporary authorization token
            token = await self._get_installation_token(session)
            if not token:
                await interaction.with_item.send("❌ **Authorization Error:** The GitHub App handshake failed. Check Railway variables.")
                return

            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "User-Agent": "Discord-Issue-Report-Bot"
            }

            issue_body = (
                f"### Discord User Bug Report\n"
                f"**Submitted By:** {interaction.user} (ID: {interaction.user.id})\n\n"
                f"### Description / Details\n"
                f"{details.strip()}\n\n"
                f"*Generated securely via the Ogre GitHub App integration.*"
            )

            data = {
                "title": f"[Ogre Bug] {title.strip()}",
                "body": issue_body
            }

            try:
                async with session.post(self.issue_url, headers=headers, json=data) as response:
                    if response.status == 201:
                        response_json = await response.json()
                        issue_url = response_json.get("html_url", "")
                        await interaction.followup.send(f"✅ **Bug posted!** Track progress under the App profile here: {issue_url}")
                    else:
                        error_text = await response.text()
                        await interaction.followup.send(f"❌ GitHub App Rejected Action: Status {response.status}")
                        print(f"App Endpoint Error: {response.status} - {error_text}")
            except Exception as e:
                await interaction.followup.send("💥 A network failure blocked the app communication pipeline.")
                print(f"Exception: {e}")

async def setup(bot):
    await bot.add_cog(Report(bot))
