import discord
from discord import app_commands
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="info", description="Gives information about the bot")
    async def ping(self, interaction: discord.Interaction):
        embed = discord.Embed()
        embed.title = "🤖 Bot Information & Resources"
        embed.description = "Thank you for using the bot! We are fully open-source and community-driven. Check out our resources below."
        embed.color = discord.Color.brand_green() # Clean, modern Discord green
        # Visual anchor thumbnail (use your bot's actual avatar URL)

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
    
        # Multi-column grid layout using inline fields
        embed.add_field(
            name="🌐 Official Links", 
            value="• [Support Server](https://discord.gg)\n• [Invite Bot](https://discord.com/oauth2/authorize?client_id=1508446745816989796&permissions=8&integration_type=0&scope=bot+applications.commands)\n•", 
            inline=True
        )
    
        embed.add_field(
            name="💻 Open Source", 
            value="• [GitHub Repository](https://github.com/AlienBlox/Ogre)\n• [Report a Bug](https://github.com/AlienBlox/Ogre/issues)\n• [Contribute](https://github.com/AlienBlox/Ogre/pulls)", 
            inline=True
        )
    
        # System status or stats field spanning full width
        embed.add_field(
            name="📊 Bot Statistics", 
            value=f"• **Servers:** {len(self.bot.guilds)}\n• **Users:** {len(self.bot.users)}\n• **Latency:** {round(self.bot.latency * 1000)}ms", 
            inline=False
        )
    
        embed.set_footer(text="Made with ❤️ by AlienBlox and the Ogres! • v1.0.0")
    
        await self.ctx.send(embed=embed)
    

async def setup(bot):
    await bot.add_cog(Utility(bot))