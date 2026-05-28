using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;
using System.Security.Cryptography;

namespace OgreBotSharp.Commands.Fun
{
    public class Dice : ApplicationCommandModule
    {
        [SlashCommand("dice", "Roll a dice (uses CSPRNG by default)")]
        public async Task DiceRoll(InteractionContext ctx, [Option("sides", "Number of sides on the dice")] long sides = 6, [Option("fast", "Use usual PRNG which is faster but less random")] bool fast = false)
        {
            if (fast)
            {
                var random = new Random();

                await ctx.CreateResponseAsync(InteractionResponseType.ChannelMessageWithSource, new DiscordInteractionResponseBuilder()
                    .WithContent($"🎲 You rolled a {random.Next(1, (int)(sides + 1))} on a {sides}-sided dice!"));

                return;
            }

            
            await ctx.CreateResponseAsync(InteractionResponseType.ChannelMessageWithSource, new DiscordInteractionResponseBuilder()
                .WithContent($"🎲 You rolled a {RandomNumberGenerator.GetInt32(1, (int)(sides + 1))} on a {sides}-sided dice!"));
        }
    }
}