import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

class Species(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Core API Endpoints
        self.search_url = "https://wikipedia.org"
        self.summary_url = "https://wikipedia.org"

    @app_commands.command(name="species", description="Fetches species details and images from Wikipedia")
    @app_commands.describe(name="The common or scientific name of the animal (e.g., Human or Panthera leo)")
    async def species_search(self, interaction: discord.Interaction, name: str):
        """Asynchronously uses Wikipedia Search to correct queries, then fetches summaries."""
        await interaction.response.defer()

        headers = {
            "User-Agent": "DiscordBot (https://github.com)"
        }

        async with aiohttp.ClientSession() as session:
            try:
                # STEP 1: Search Wikipedia to get the closest exact matching page title
                search_params = {
                    "action": "opensearch",
                    "search": name.strip(),
                    "limit": "1",
                    "namespace": "0",
                    "format": "json"
                }
                
                async with session.get(self.search_url, params=search_params, headers=headers) as search_res:
                    if search_res.status != 200:
                        await interaction.followup.send(f"⚠️ Wikipedia Search failed. Code: {search_res.status}")
                        return
                        
                    search_data = await search_res.json()
                    
                    # OpenSearch returns data as [query, [titles], [descriptions], [links]]
                    if not search_data[1]:
                        await interaction.followup.send(f"❌ Could not find any species matching `{name}`.")
                        return
                        
                    # Extract the best exact title match found by Wikipedia
                    corrected_title = search_data[1][0].replace(" ", "_")

                # STEP 2: Query the summary using our freshly corrected title
                fetch_url = f"{self.summary_url}/{corrected_title}"
                
                async with session.get(fetch_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Extract metrics
                        title = data.get("title", name.title())
                        description = data.get("description", "No brief description available.")
                        extract = data.get("extract", "No summary available.")
                        page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
                        thumbnail_url = data.get("thumbnail", {}).get("source", None)

                        # Assemble visual presentation card
                        embed = discord.Embed(
                            title=title,
                            description=f"*{description}*\n\n{extract}",
                            color=discord.Color.blue(),
                            url=page_url
                        )
                        
                        if thumbnail_url:
                            embed.set_thumbnail(url=thumbnail_url)
                            
                        embed.set_footer(text="Data source: Wikimedia Open API with Auto-Search")

                        await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send(f"❌ Found a matching page, but failed to extract the text summary.")
            
            except Exception as e:
                await interaction.followup.send("💥 An internal error occurred while fetching the data.")
                print(f"Wikipedia Cog Error: {e}")

async def setup(bot):
    await bot.add_cog(Species(bot))