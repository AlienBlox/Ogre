using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;

public class BotInfo : ApplicationCommandModule
{
    [SlashCommand("botinfo", "Get information about the bot.")]
    public async Task BotInfoCommand(InteractionContext ctx)
    {
        var botUser = ctx.Client.CurrentUser;
        var creationDate = botUser.CreationTimestamp.UtcDateTime;

        // Note: This calculates how old the account registration is, not application uptime.
        var accountAge = DateTime.UtcNow - creationDate;

        // --- FIXED: Swapped URL and Label positions to match API syntax ---
        var githubButton = new DiscordLinkButtonComponent("https://github.com/AlienBlox/OgreBotSharp", "GitHub");
        var installationButton = new DiscordLinkButtonComponent("https://discord.com/oauth2/authorize?client_id=1508446745816989796&permissions=8&integration_type=0&scope=bot+applications.commands", "Install Me!");

        // Added clean newlines (\n) to prevent text crowding in the final client layout
        var responseContent = $"🤖 **Bot Information**\n" +
                              $"**Username:** {botUser.Username}#{botUser.Discriminator}\n" +
                              $"**ID:** {botUser.Id}\n" +
                              $"**Created On:** {creationDate:yyyy-MM-dd HH:mm:ss} UTC\n" +
                              $"**Account Age:** {accountAge.Days}d {accountAge.Hours}h {accountAge.Minutes}m\n" +
                              $"**Servers On:** {ctx.Client.Guilds.Count}\n" +
                              $"**Shards:** {ctx.Client.ShardCount}\n\n" +
                              $"*An open source discord bot made by AlienBlox and the Dragons!*";

        await ctx.CreateResponseAsync(
            InteractionResponseType.ChannelMessageWithSource,
            new DiscordInteractionResponseBuilder()
                .WithContent(responseContent)
                .AddComponents(githubButton, installationButton)
        );
    }
}