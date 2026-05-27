using DSharpPlus.SlashCommands;

namespace OgreBotSharp.Commands.CoreCommands
{
    public class ShutdownBot : ApplicationCommandModule
    {
        [SlashCommand("shutdown", "Shuts down the bot.")]
        public async Task Shutdown(InteractionContext ctx)
        {
            Environment.Exit(0);
        }
    }
}