using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;
using Octokit;
using OgreBotSharp.Utilities;

namespace OgreBotSharp.Commands.CoreCommands
{
    public class ReportCommands : ApplicationCommandModule
    {
        private static readonly string RepoOwner = Environment.GetEnvironmentVariable("GH_REPO_OWNER") ?? "your-username";
        private static readonly string RepoName = Environment.GetEnvironmentVariable("GH_REPO_NAME") ?? "your-repo";

        [SlashCommand("report", "Submit a bug report or issue directly to our GitHub repository.")]
        public async Task ReportCommand(
            InteractionContext ctx,
            [Option("title", "A brief headline summarizing the problem")] string title,
            [Option("description", "Provide steps to reproduce or details about the issue")] string description,
            [Option("anonymous", "Hide your username and server origin from the public GitHub ticket")] bool isAnonymous = false)
        {
            // Defer response immediately since the GitHub API handshake can take a few seconds
            await ctx.CreateResponseAsync(InteractionResponseType.DeferredChannelMessageWithSource,
                new DiscordInteractionResponseBuilder().AsEphemeral(true));

            try
            {
                // 1. Authenticate with GitHub App
                var github = await GitHubClientFactory.GetAuthenticatedClientAsync();

                // 2. Extract and format origin details safely (handles Direct Messages gracefully)
                string serverName = ctx.Guild != null ? ctx.Guild.Name : "Direct Message";

                // 3. Format metadata blocks conditional to anonymity profile
                string submitterLine = isAnonymous
                    ? "*Submitted anonymously via Discord Bot Integration.*"
                    : $"*Submitted by: @{ctx.User.Username} ({ctx.User.Id}) from server: **{serverName}***";

                string issueBody = $"""
            ### Issue Description
            {description}

            ---
            {submitterLine}
            """;

                // 4. Create and dispatch the issue package
                var newIssue = new NewIssue(title) { Body = issueBody };
                var issue = await github.Issue.Create(RepoOwner, RepoName, newIssue);

                // 5. Update deferred response back to the user with the tracking link
                await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent($"✅ **Report Submitted Successfully!** You can track progress here: {issue.HtmlUrl}"));
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[ERROR] Failed to submit GitHub issue: {ex.Message}");
                await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent("❌ **System Error:** Failed to connect to the GitHub submission endpoint. Please try again later."));
            }
        }
    }
}