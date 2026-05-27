using System.Text.Json;
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
            string encodedName = Uri.EscapeDataString(compoundName);

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

            // 2. Fetch structural Data File string content (.SDF format)
            string molUrl = $"https://nih.gov{cid}/SDF";
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
            string safeFileName = compoundName.Replace(" ", "_").ToLower();

            // --- 4. BUILD THE RICH EMBED + PNG GENERATOR URL ---
            // PubChem exposes a direct image engine based on CID mappings
            string imageUrl = $"https://nih.gov{cid}/PNG";

            var embed = new DiscordEmbedBuilder()
                .WithTitle($"🧪 PubChem Chemical Record: {char.ToUpper(compoundName[0]) + compoundName[1..]}")
                .WithUrl($"https://nih.gov{cid}")
                .WithColor(new DiscordColor("#0071BC")) // PubChem brand signature blue hue
                .AddField("Compound ID (CID)", $"`{cid}`", true)
                .AddField("Format Type", "`.mol` (2D Spatial Mapping)", true)
                .WithImageUrl(imageUrl) // Embeds the structural schematic image
                .WithFooter("Data sourced dynamically via PubChem PUG REST API Framework");

            // 5. Build and transmit the combined message payload layout
            var responseBuilder = new DiscordWebhookBuilder()
                .AddEmbed(embed)
                .AddFile($"{safeFileName}.mol", memoryStream);

            await ctx.EditResponseAsync(responseBuilder);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[ERROR] PubChem handler error: {ex.Message}");
            await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                .WithContent("❌ **System Failure:** An error occurred while parsing the PubChem data structure."));
        }
    }
}
