using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;

namespace OgreBotSharp.Commands.CoreCommands
{
    public class Dice : ApplicationCommandModule
    {
        [SlashCommand("dice", "Roll a dice")]
        public async Task DiceRoll(InteractionContext ctx, [Option("sides", "Number of sides on the dice")] long sides = 6)
        {
            await ctx.CreateResponseAsync(InteractionResponseType.ChannelMessageWithSource, new DiscordInteractionResponseBuilder()
                .WithContent($"🎲 You rolled a {new Random().Next(1, (int)(sides + 1))} on a {sides}-sided dice!"));
        }
    }
}