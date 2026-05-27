using DSharpPlus;
using DSharpPlus.SlashCommands;
using System.Reflection;

namespace OgreBotSharp
{
    /// <summary>
    /// The core of OgreBotSharp...
    /// </summary>
    public class OgreBotSharp
    {
        public static async Task Main(string[] args)
        {
            try
            {
                var discord = new DiscordClient(new DiscordConfiguration
                {
                    Token = Environment.GetEnvironmentVariable("DISCORD_BOT_TOKEN") ?? "YOUR_BOT_TOKEN_HERE",
                    TokenType = TokenType.Bot,
                    Intents = DiscordIntents.AllUnprivileged
                });

                discord.Ready += (sender, args) =>
                {
                    Console.WriteLine($"[SUCCESS] {sender.CurrentUser.Username} is fully initialized, connected, and online!");
                    return Task.CompletedTask;
                };

                var slash = discord.UseSlashCommands();

                // --- DYNAMIC REGISTRATION SYSTEM ---
                // 1. Scan the current executing assembly for command modules
                var moduleTypes = Assembly.GetExecutingAssembly()
                    .GetTypes()
                    .Where(t => t.IsSubclassOf(typeof(ApplicationCommandModule)) && !t.IsAbstract);

                // 2. Loop through and register each module dynamically
                foreach (var type in moduleTypes)
                {
                    slash.RegisterCommands(type);
                }
                // ------------------------------------

                await discord.ConnectAsync();
                await Task.Delay(-1);
            }
            catch (Exception ex)
            {
                Console.WriteLine("Bot failure with exception: " + ex.Message);
            }
        }
    }
}