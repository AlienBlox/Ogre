using System.Text.Json;
using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;

public class ChemistryCommands : ApplicationCommandModule
{
    // Reuse a single HttpClient instance across your bot commands to prevent socket exhaustion
    private static readonly HttpClient HttpClient = new();

    [SlashCommand("pubchem", "Search for a chemical compound and download its structural .mol file.")]
    public async Task GetMolFileCommand(
        InteractionContext ctx,
        [Option("compound", "The common or systematic name of the chemical (e.g., aspirin, caffeine)")] string compoundName)
    {
        // Defer response immediately since external API network requests can take a few seconds
        await ctx.CreateResponseAsync(InteractionResponseType.DeferredChannelMessageWithSource);

        try
        {
            // URL Encode the string parameter to make sure spaces or special characters don't break the web request
            string encodedName = Uri.EscapeDataString(compoundName);

            // Step 1: Query PubChem's REST API to resolve the compound name into its standard CID
            string cidUrl = $"https://nih.gov//{encodedName}/cids/JSON";
            var cidResponse = await HttpClient.GetAsync(cidUrl);

            if (!cidResponse.IsSuccessStatusCode)
            {
                await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent($"❌ **Not Found:** Could not locate a compound matching `{compoundName}` on PubChem."));
                return;
            }

            // Parse the CID out of the returned JSON structure
            string jsonString = await cidResponse.Content.ReadAsStringAsync();
            using var jsonDoc = JsonDocument.Parse(jsonString);

            // Extract the first matching ID from the array hierarchy
            var root = jsonDoc.RootElement;
            int cid = root.GetProperty("IdentifierList").GetProperty("CID")[0].GetInt32();

            // Step 2: Request the structural .mol schema string using the resolved CID
            // We request the standard 2D SDF structural layout (which maps matching structural coordinate points)
            string molUrl = $"https://nih.gov/{cid}/SDF";
            var molResponse = await HttpClient.GetAsync(molUrl);

            if (!molResponse.IsSuccessStatusCode)
            {
                await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent($"❌ **API Error:** Found the compound (CID: `{cid}`), but failed to extract structural records."));
                return;
            }

            string molContent = await molResponse.Content.ReadAsStringAsync();

            // Step 3: Convert the raw string content directly into an in-memory byte stream layout
            byte[] fileBytes = System.Text.Encoding.UTF8.GetBytes(molContent);
            using var memoryStream = new MemoryStream(fileBytes);

            // Standardize file name parsing configurations
            string safeFileName = compoundName.Replace(" ", "_").ToLower();

            // Step 4: Dispatch the text block back as a downloadable file attachment
            var responseBuilder = new DiscordWebhookBuilder()
                .WithContent($"🧪 **PubChem Chemical Record Found!**\n" +
                             $"• **Name:** `{compoundName}`\n" +
                             $"• **Compound ID (CID):** `{cid}`\n" +
                             $"• **Source URL:** <https://nih.gov{cid}>\n\n" +
                             $"Attached is your `.mol` structure modeling file:")
                .AddFile($"{safeFileName}.mol", memoryStream);

            await ctx.EditResponseAsync(responseBuilder);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[ERROR] PubChem handler error: {ex.Message}");
            await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                .WithContent("❌ **System Failure:** An error occurred while communicating with the PubChem servers."));
        }
    }
}
