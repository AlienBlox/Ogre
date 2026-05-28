using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;
using System.Text.Json;

namespace OgreBotSharp.Commands.CoreCommands
{
    public class GetIssuesList : ApplicationCommandModule
    {
        [SlashCommand("getissues", "Fetches the bot's issue list on GitHub. (Choose amount.)")]
        public async Task GetIssuesCommand(InteractionContext ctx, [Option("countamount", "Number of issues to fetch (1-20).")] long countAmount = 5)
        {
            try
            {
                if (countAmount < 1 || countAmount > 20)
                {
                    await ctx.CreateResponseAsync(InteractionResponseType.ChannelMessageWithSource,
                        new DiscordInteractionResponseBuilder().WithContent("❌ **Invalid Input:** Please choose a number between 1 and 20."));
                    return;
                }

                HttpClient client = new();
                string user = Environment.GetEnvironmentVariable("GH_REPO_OWNER") ?? "AlienBlox";
                string repo = Environment.GetEnvironmentVariable("GH_REPO_NAME") ?? "Ogre";
                List<string> issues = [];

                client.DefaultRequestHeaders.UserAgent.ParseAdd($"OgreBotSharp/{BotDiagnostics.Version}");

                var content = await client.GetStreamAsync($"https://api.github.com/repos/{user}/{repo}/issues");
                var json = await JsonDocument.ParseAsync(content);

                int count = json.RootElement.EnumerateArray().Count();

                if (count > countAmount)
                    count = (int)countAmount;

                for (var i = 0; i < count; i++)
                {
                    var issue = json.RootElement[i];
                    string title = issue.GetProperty("title").GetString() ?? "No Title";
                    string url = issue.GetProperty("url").GetString() ?? "No URL";
                    string body = issue.GetProperty("body").GetString() ?? "No Content";
                    issues.Add($"Title: {title}\nUrl: {url}\nContent:\n{body}");
                }

                foreach (var issue in issues)
                {
                    await ctx.CreateResponseAsync(InteractionResponseType.ChannelMessageWithSource,
                        new DiscordInteractionResponseBuilder().WithContent(issue));
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[ERROR] Failed to fetch GitHub issues: {ex.Message}");
                await ctx.CreateResponseAsync(InteractionResponseType.ChannelMessageWithSource,
                    new DiscordInteractionResponseBuilder().WithContent("❌ **System Error:** Failed to connect to the GitHub API endpoint. Please try again later."));
            }
        }
    }
}
