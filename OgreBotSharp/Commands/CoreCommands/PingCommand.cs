using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;

namespace OgreBotSharp.Commands.CoreCommands
{
    public class UtilityCommands : ApplicationCommandModule
    {
        [SlashCommand("ping", "Checks bot responsiveness and current gateway latency.")]
        public async Task PingCommand(InteractionContext ctx)
        {
            // Calculate current connection frame latency response
            int latency = ctx.Client.Ping;

            // Respond directly inside the channel with your performance metric
            await ctx.CreateResponseAsync(
                InteractionResponseType.ChannelMessageWithSource,
                new DiscordInteractionResponseBuilder().WithContent($"🏓 **Pong!** Latency is `{latency}ms`.")
            );
        }
    }
}