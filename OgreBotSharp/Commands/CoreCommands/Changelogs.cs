using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;

namespace OgreBotSharp.Commands.CoreCommands
{
    public class Changelogs : ApplicationCommandModule
    {
        [SlashCommand("changelogs", "Fetches the bot's changelogs")]
        public async Task ChangelogsCommand(InteractionContext ctx)
        {
            HttpClient client = new HttpClient();

            string changelogUrl = "https://raw.githubusercontent.com/AlienBlox/Ogre/main/Changelogs.txt";

            try
            {
                client.DefaultRequestHeaders.UserAgent.ParseAdd("OgreBot/1.0");

                string FileContents = await client.GetStringAsync(changelogUrl);

                var embed = new DiscordEmbedBuilder
                {
                    Title = "Ogre Bot Changelogs",
                    Description = $"```\n{FileContents}\n```",
                    Color = DiscordColor.Green
                };

                await ctx.CreateResponseAsync(InteractionResponseType.ChannelMessageWithSource,
                    new DiscordInteractionResponseBuilder().AddEmbed(embed));
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[ERROR] Failed to fetch changelogs: {ex.Message}");
                await ctx.CreateResponseAsync(InteractionResponseType.ChannelMessageWithSource,
                    new DiscordInteractionResponseBuilder().WithContent("❌ **Error:** Unable to retrieve changelogs at this time. Please try again later."));
            }
        }
    }
}