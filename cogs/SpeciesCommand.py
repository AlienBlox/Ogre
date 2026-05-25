import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

class Species(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Public Wikipedia REST API endpoint (No Token Required)
        self.base_url = "https://wikipedia.org"

    @app_commands.command(name="species", description="Fetches species details and images from Wikipedia")
    @app_commands.describe(name="The common or scientific name of the animal (e.g., Javan Rhinoceros)")
    async def species_search(self, interaction: discord.Interaction, name: str):
        """Asynchronously queries the Wikipedia REST API for a species overview."""
        await interaction.response.defer()

        # Format user string for Wikipedia URL naming rules (CamelCase/Underscores)
        formatted_name = name.strip().title().replace(" ", "_")
        url = f"{self.base_url}/{formatted_name}"

        # Standard User-Agent header (Wikipedia requests this to keep traffic identifiable)
        headers = {
            "User-Agent": "DiscordBot (https://github.com)"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Extract specific metrics from JSON payload
                        title = data.get("title", name.title())
                        description = data.get("description", "No brief description available.")
                        extract = data.get("extract", "No summary available.")
                        page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
                        
                        # Extract the main display image if it exists
                        thumbnail_url = data.get("thumbnail", {}).get("source", None)

                        # Assemble a visual card
                        embed = discord.Embed(
                            title=title,
                            description=f"*{description}*\n\n{extract}",
                            color=discord.Color.blue(),
                            url=page_url
                        )
                        
                        if thumbnail_url:
                            embed.set_thumbnail(url=thumbnail_url)
                            
                        embed.set_footer(text="Data source: Wikimedia Open REST API")

                        await interaction.followup.send(embed=embed)
                    
                    elif response.status == 404:
                        await interaction.followup.send(f"❌ Could not find a species article matching `{name}` on Wikipedia.")
                    else:
                        await interaction.followup.send(f"⚠️ Wikipedia API issue. HTTP Code: {response.status}")
            
            except Exception as e:
                await interaction.followup.send("💥 An error occurred while fetching the database.")
                print(f"Wikipedia Cog Error: {e}")

async def setup(bot):
    await bot.add_cog(Species(bot))