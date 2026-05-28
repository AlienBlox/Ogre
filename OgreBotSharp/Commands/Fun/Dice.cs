using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;
using System.Security.Cryptography;

namespace OgreBotSharp.Commands.Fun
{
    public class Dice : ApplicationCommandModule
    {
        [SlashCommand("dice", "Roll a dice")]
        public async Task DiceRoll(InteractionContext ctx, [Option("sides", "Number of sides on the dice (With CSPRNG)")] long sides = 6)
        {
            await ctx.CreateResponseAsync(InteractionResponseType.ChannelMessageWithSource, new DiscordInteractionResponseBuilder()
                .WithContent($"🎲 You rolled a {RandomNumberGenerator.GetInt32(1, (int)(sides + 1))} on a {sides}-sided dice!"));
        }
    }
}