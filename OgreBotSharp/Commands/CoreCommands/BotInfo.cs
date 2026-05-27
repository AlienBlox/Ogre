using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;

namespace OgreBotSharp.Commands.CoreCommands
{
    public class BotInfo : ApplicationCommandModule
    {
        [SlashCommand("botinfo", "Get information about the bot.")]
        public async Task BotInfoCommand(InteractionContext ctx)
        {
            var botUser = ctx.Client.CurrentUser;
            var creationDate = botUser.CreationTimestamp.UtcDateTime;
            var uptime = DateTime.UtcNow - creationDate;
            var githubButton = new DiscordLinkButtonComponent("GitHub", "https://github.com/AlienBlox/OgreBotSharp");
            var installationButton = new DiscordLinkButtonComponent("Install Me!", "https://discord.com/oauth2/authorize?client_id=1508446745816989796&permissions=8&integration_type=0&scope=bot+applications.commands");

            await ctx.CreateResponseAsync(InteractionResponseType.ChannelMessageWithSource, new DiscordInteractionResponseBuilder()
                .WithContent($"🤖 **Bot Information**\n" +
                             $"**Username:** {botUser.Username}#{botUser.Discriminator}\n" +
                             $"**ID:** {botUser.Id}\n" +
                             $"**Created On:** {creationDate:yyyy-MM-dd HH:mm:ss} UTC\n" +
                             $"**Uptime:** {uptime.Days}d {uptime.Hours}h {uptime.Minutes}m" +
                             $"**Servers On:** {ctx.Client.Guilds.Count}" +
                             $"**Shards:** {ctx.Client.ShardCount}" +
                             "*An open source discord bot made by AlienBlox and the Dragons!*"
                             ).
                AddComponents(githubButton, installationButton)
                );
        }
    }
}