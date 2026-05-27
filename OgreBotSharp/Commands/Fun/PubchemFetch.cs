using System.Text.Json;
using System.Globalization;
using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;

public class ChemistryCommands : ApplicationCommandModule
{
    private static readonly HttpClient HttpClient = new();

    [SlashCommand("pubchem", "Search for a chemical compound and download its structural .mol file.")]
    public async Task GetMolFileCommand(
        InteractionContext ctx,
        [Option("compound", "The common or systematic name of the chemical (e.g., aspirin, caffeine)")] string compoundName)
    {
        await ctx.CreateResponseAsync(InteractionResponseType.DeferredChannelMessageWithSource);

        try
        {
            // Lowercase and trim the input to ensure predictable API query results
            string cleanInput = compoundName.Trim().ToLower();
            string encodedName = Uri.EscapeDataString(cleanInput);

            // 1. Resolve Compound Name to unique PubChem CID
            string cidUrl = $"https://nih.gov{encodedName}/cids/JSON";
            var cidResponse = await HttpClient.GetAsync(cidUrl);

            if (!cidResponse.IsSuccessStatusCode)
            {
                await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent($"❌ **Not Found:** Could not locate a compound matching `{compoundName}` on PubChem."));
                return;
            }

            string jsonString = await cidResponse.Content.ReadAsStringAsync();
            using var jsonDoc = JsonDocument.Parse(jsonString);

            var root = jsonDoc.RootElement;
            int cid = root.GetProperty("IdentifierList")
                          .GetProperty("CID")
                          .EnumerateArray()
                          .First()
                          .GetInt32();

            // 2. Fetch structural Data File string content (.SDF/.MOL format)
            string molUrl = $"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/SDF";
            var molResponse = await HttpClient.GetAsync(molUrl);

            if (!molResponse.IsSuccessStatusCode)
            {
                await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent($"❌ **API Error:** Found the compound (CID: `{cid}`), but failed to extract structural records."));
                return;
            }

            string molContent = await molResponse.Content.ReadAsStringAsync();

            // 3. Prepare the plain-text in-memory data attachment stream
            byte[] fileBytes = System.Text.Encoding.UTF8.GetBytes(molContent);
            using var memoryStream = new MemoryStream(fileBytes);
            string safeFileName = cleanInput.Replace(" ", "_");

            // --- 4. SAFE STRING CAPITIALIZATION FIX ---
            // Uses TextInfo to prevent character slicing array indexing crashes
            string formattedTitle = CultureInfo.InvariantCulture.TextInfo.ToTitleCase(cleanInput);
            string imageUrl = $"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG";

            var embed = new DiscordEmbedBuilder()
                .WithTitle($"🧪 PubChem Chemical Record: {formattedTitle}")
                .WithUrl($"https://nih.gov{cid}")
                .WithColor(new DiscordColor("#0071BC")) // PubChem signature blue
                .AddField("Compound ID (CID)", $"`{cid}`", true)
                .AddField("Format Type", "`.mol` (2D Spatial Mapping)", true)
                .WithImageUrl(imageUrl)
                .WithFooter("Data sourced dynamically via PubChem PUG REST API Framework");

            // 5. Build and transmit the combined message payload layout
            var responseBuilder = new DiscordWebhookBuilder()
                .AddEmbed(embed)
                .AddFile($"{safeFileName}.mol", memoryStream);

            await ctx.EditResponseAsync(responseBuilder);
        }
        catch (Exception ex)
        {
            // Logs the specific crash point to your console/Railway dashboard for easy debugging
            Console.WriteLine($"[CRITICAL ERROR] PubChem Engine Exception: {ex.Message}\n{ex.StackTrace}");
            await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                .WithContent("❌ **System Failure:** An error occurred while parsing the PubChem data structure. Check internal console runtime logs."));
        }
    }
}
