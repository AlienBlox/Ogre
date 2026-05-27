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

            // --- CALCULATE ACTUAL UPTIME ---
            var uptime = DateTime.UtcNow - BotDiagnostics.StartTime;
            // -------------------------------

            var githubButton = new DiscordLinkButtonComponent("https://github.com", "GitHub");
            var installationButton = new DiscordLinkButtonComponent("https://discord.com", "Install Me!");

            var responseContent = $"🤖 **Bot Information**\n" +
                                  $"**Username:** {botUser.Username}#{botUser.Discriminator}\n" +
                                  $"**ID:** {botUser.Id}\n" +
                                  $"**Created On:** {creationDate:yyyy-MM-dd HH:mm:ss} UTC\n" +
                                  $"**Uptime:** {uptime.Days}d {uptime.Hours}h {uptime.Minutes}m {uptime.Seconds}s\n" +
                                  $"**Servers On:** {ctx.Client.Guilds.Count}\n" +
                                  $"**Shards:** {ctx.Client.ShardCount}\n\n" +
                                  $"*An open source discord bot made by AlienBlox and the Dragons!* \n" +
                                  $"**Current Ver:** {BotDiagnostics.Version}";

            await ctx.CreateResponseAsync(
                InteractionResponseType.ChannelMessageWithSource,
                new DiscordInteractionResponseBuilder()
                    .WithContent(responseContent)
                    .AddComponents(githubButton, installationButton)
            );
        }
    }
}