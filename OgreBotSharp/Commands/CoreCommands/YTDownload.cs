using DSharpPlus.SlashCommands;
using YoutubeExplode;
using YoutubeExplode.Videos.Streams;

public class VideoCommands : ApplicationCommandModule
{

    [SlashCommand("download", "Downloads a YouTube video up to 720p and streams it straight to Discord.")]
    public async Task DownloadCommand(InteractionContext ctx, [Option("url", "The YouTube URL")] string url)
    {
        var youtube = new YoutubeClient();

        try
        {
            Console.WriteLine("🔍 Analyzing media metadata frameworks...");

            // 2. Extract full descriptive data blocks about the target file
            var video = await youtube.Videos.GetAsync(url);
            Console.WriteLine($"🎥 Target Isolated: \"{video.Title}\" by {video.Author}");

            // 3. Request the mapping layout of all available media stream paths
            var streamManifest = await youtube.Videos.Streams.GetManifestAsync(video.Id);

            // 4. Filter for 'Muxed' streams (streams that bundle BOTH video and audio together)
            // and sort them to grab the absolute highest resolution available (typically 720p maximum for combined streams)
            var streamInfo = streamManifest
                .GetMuxedStreams()
                .GetWithHighestVideoQuality();

            if (streamInfo == null)
            {
                Console.WriteLine("❌ Error: No compatible pre-muxed audio/video pipelines discovered.");
                return;
            }

            // 5. Sanitize target text characters to prevent OS disk writing failures
            string safeTitle = string.Concat(video.Title.Split(Path.GetInvalidFileNameChars()));
            string outputFilePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, $"{safeTitle}.{streamInfo.Container}");

            Console.WriteLine($"📥 Downloading highest available quality asset ({streamInfo.VideoQuality.Label})...");

            // 6. Pipe the web-stream chunks down directly onto the local drive structure
            await youtube.Videos.Streams.DownloadAsync(streamInfo, outputFilePath);

            Console.WriteLine($"\n✅ Transfer complete! Asset written securely to:\n👉 {outputFilePath}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"\n❌ Processing Failure: {ex.Message}");
        }
    }
}
