using DSharpPlus.SlashCommands;

namespace OgreBotSharp.Commands.CoreCommands
{
    public class ShutdownBot : ApplicationCommandModule
    {
        [SlashCommand("shutdown", "Shuts down the bot.")]
        public async Task Shutdown(InteractionContext ctx)
        {
            if (ctx.User.Id != 1162429758513094758)
                return;

            Console.WriteLine($"[INFO] Shutdown command invoked by {ctx.User.Username}#{ctx.User.Discriminator} ({ctx.User.Id}). Shutting down...");
            Environment.Exit(0);
        }
    }
}