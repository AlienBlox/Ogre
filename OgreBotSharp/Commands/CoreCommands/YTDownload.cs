using System;
using System.IO;
using System.Threading.Tasks;
using DSharpPlus.CommandsNext;
using DSharpPlus.CommandsNext.Attributes;
using DSharpPlus.Entities;
using YoutubeExplode;
using YoutubeExplode.Videos.Streams;

public class VideoCommands : BaseCommandModule
{
    // Keeping a single instance prevents socket exhaustion in your container
    private readonly YoutubeClient _youtube = new YoutubeClient();

    [Command("download")]
    [Description("Downloads a YouTube video up to 720p and streams it straight to Discord.")]
    public async Task DownloadCommand(CommandContext ctx, [Description("The YouTube URL")] string url)
    {
        // 1. Signal to users that the bot is actively processing
        await ctx.TriggerTypingAsync();

        try
        {
            // 2. Query video metadata and available stream formats
            var video = await _youtube.Videos.GetAsync(url);
            var streamManifest = await _youtube.Videos.Streams.GetManifestAsync(url);

            // 3. Target Muxed streams (contains audio + video, works perfectly without FFmpeg)
            var streamInfo = streamManifest.GetMuxedStreams().GetWithHighestVideoQuality();

            if (streamInfo == null)
            {
                await ctx.RespondAsync("❌ No compatible video formats found.");
                return;
            }

            // 4. Enforce standard Discord upload limits (25MB for normal servers)
            if (streamInfo.Size.MegaBytes > 25)
            {
                // Auto-fallback to lower resolution (like 360p) to fit the upload window
                streamInfo = streamManifest.GetMuxedStreams().GetWithLowestVideoQuality();

                if (streamInfo.Size.MegaBytes > 25)
                {
                    await ctx.RespondAsync($"❌ File is too large ({streamInfo.Size.MegaBytes:F1}MB). Discord limits standard uploads to 25MB.");
                    return;
                }
            }

            // 5. Open a direct network stream pipeline from YouTube's servers
            using (var youtubeStream = await _youtube.Videos.Streams.GetStreamAsync(streamInfo))
            {
                // Sanitize title so special characters don't break the Discord attachment header
                string safeTitle = string.Join("_", video.Title.Split(Path.GetInvalidFileNameChars()));
                string fileName = $"{safeTitle}.{streamInfo.Container}";

                // 6. Build and dispatch the file payload natively through DSharpPlus
                var messageBuilder = new DiscordMessageBuilder()
                    .WithContent($"🎥 **{video.Title}** ({streamInfo.VideoQuality.Label}) successfully fetched!")
                    .WithFile(fileName, youtubeStream);

                await ctx.RespondAsync(messageBuilder);
            }
        }
        catch (Exception ex)
        {
            await ctx.RespondAsync($"⚠️ Failed to process video: {ex.Message}");
        }
    }
}
