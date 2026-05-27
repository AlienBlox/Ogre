using System.IO;
using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;
using YoutubeExplode;
using YoutubeExplode.Videos.Streams;

public class YoutubeModule : ApplicationCommandModule
{
    private static readonly YoutubeClient Youtube = new();

    [SlashCommand("download", "Downloads a YouTube video and uploads it directly to the channel.")]
    public async Task DownloadVideoCommand(
        InteractionContext ctx,
        [Option("url", "The full YouTube video URL")] string videoUrl)
    {
        // 1. Defer the interaction response immediately to give the bot time to download the file
        await ctx.CreateResponseAsync(InteractionResponseType.DeferredChannelMessageWithSource);

        // Define a safe temporary local storage path
        string tempFilePath = Path.Combine(Path.GetTempPath(), $"{Guid.NewGuid()}.mp4");

        try
        {
            // 2. Extract video details and metadata
            var video = await Youtube.Videos.GetAsync(videoUrl);

            // 3. Request the video stream configurations mapping
            var streamManifest = await Youtube.Videos.Streams.GetManifestAsync(video.Id);

            // 4. Extract the highest available muxed audio/video combo stream (Maxes at 720p/360p due to YT changes)
            var streamInfo = streamManifest.GetMuxedStreams().GetWithHighestVideoQuality();

            if (streamInfo == null)
            {
                await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent("❌ **Error:** No compatible pre-muxed video streams could be found."));
                return;
            }

            // 5. Check video size before downloading to prevent unnecessary processing
            // Discord free limit is ~10MB (approx 10,485,760 bytes). 
            long discordMaxBytes = 10 * 1024 * 1024;
            if (streamInfo.Size.Bytes > discordMaxBytes)
            {
                await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent($"⚠️ **File Too Large:** This video is `{streamInfo.Size.MegaBytes:F1} MB`, which exceeds Discord's file upload limit."));
                return;
            }

            // 6. Download the stream to our temporary disk file asset
            await Youtube.Videos.Streams.DownloadAsync(streamInfo, tempFilePath);

            // 7. Open a readable file stream over the downloaded temporary file
            using (var fileStream = new FileStream(tempFilePath, FileMode.Open, FileAccess.Read))
            {
                // Sanitize file title characters to prevent Discord attachment string faults
                string safeTitle = string.Concat(video.Title.Split(Path.GetInvalidFileNameChars())).Replace(" ", "_");

                var responseBuilder = new DiscordWebhookBuilder()
                    .WithContent($"🎬 **Downloaded:** `{video.Title}`\n⏱️ **Duration:** {video.Duration}")
                    .AddFile($"{safeTitle}.mp4", fileStream); // Forwards the stream to Discord

                // 8. Upload the file to Discord
                await ctx.EditResponseAsync(responseBuilder);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[ERROR] YouTube Download Exception: {ex.Message}\n{ex.StackTrace}");
            await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                .WithContent("❌ **System Failure:** An error occurred while parsing or uploading the YouTube file payload."));
        }
        finally
        {
            // 9. Clean up the disk footprint by purging the local temp file safely
            if (File.Exists(tempFilePath))
            {
                try { File.Delete(tempFilePath); } catch { /* Ignore locked thread file issues */ }
            }
        }
    }
}