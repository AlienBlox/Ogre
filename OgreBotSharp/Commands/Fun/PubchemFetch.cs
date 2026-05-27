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

            // 1. Query PubChem's REST API to resolve the compound name into its standard CID
            string cidUrl = $"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encodedName}/cids/JSON";
            var cidResponse = await HttpClient.GetAsync(cidUrl);

            if (!cidResponse.IsSuccessStatusCode)
            {
                await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent($"❌ **Not Found:** Could not locate a compound matching `{compoundName}` on PubChem."));
                return;
            }

            string jsonString = await cidResponse.Content.ReadAsStringAsync();
            using var jsonDoc = JsonDocument.Parse(jsonString);

            // --- FIXED JSON EXTRACTION PATH ---
            // PubChem returns "CID" as a JSON Array (e.g., "CID": [2519]). 
            // We use .EnumerateArray().First().GetInt32() to cleanly extract index 0.
            var root = jsonDoc.RootElement;
            int cid = root.GetProperty("IdentifierList")
                          .GetProperty("CID")
                          .EnumerateArray()
                          .First()
                          .GetInt32();
            // ----------------------------------

            // 2. Request the structural .mol schema string using the resolved CID
            string molUrl = $"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/SDF";
            var molResponse = await HttpClient.GetAsync(molUrl);

            if (!molResponse.IsSuccessStatusCode)
            {
                await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent($"❌ **API Error:** Found the compound (CID: `{cid}`), but failed to extract structural records."));
                return;
            }

            string molContent = await molResponse.Content.ReadAsStringAsync();

            // 3. Convert the raw string content directly into an in-memory byte stream layout
            byte[] fileBytes = System.Text.Encoding.UTF8.GetBytes(molContent);
            using var memoryStream = new MemoryStream(fileBytes);

            string safeFileName = compoundName.Replace(" ", "_").ToLower();

            // 4. Dispatch the text block back as a downloadable file attachment
            var responseBuilder = new DiscordWebhookBuilder()
                .WithContent($"🧪 **PubChem Chemical Record Found!**\n" +
                             $"• **Name:** `{compoundName}`\n" +
                             $"• **Compound ID (CID):** `{cid}`\n" +
                             $"• **Source URL:** <https://pubchem.ncbi.nlm.nih.gov/compound/{cid}>\n\n" +
                             $"Attached is your `.mol` structure modeling file:")
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
