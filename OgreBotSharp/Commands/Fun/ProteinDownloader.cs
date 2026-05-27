using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;

namespace OgreBotSharp.Commands.Fun
{
    public class ProteinCommands : ApplicationCommandModule
    {
        private static readonly HttpClient _httpClient = new HttpClient();

        // Command Trigger: /protein 4hhb (or prefix based on your bot setup)
        [SlashCommand("protein", "Fetch and download a protein structure file from the RCSB PDB.")]
        public async Task GetProteinAsync(InteractionContext context, [Option("pdbid", "The 4-character PDB ID of the protein to fetch")] string pdbId)
        {
            // 1. Sanitize user input
            if (string.IsNullOrWhiteSpace(pdbId) || pdbId.Length != 4)
            {
                await context.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent("❌ **Invalid Format:** Please provide a valid 4-character PDB ID (e.g., `4HHB`)."));
                return;
            }

            await context.DeferAsync();


            string cleanId = pdbId.Trim().ToLower();
            string url = $"https://files.rcsb.org/download/{cleanId}.cif.gz";

            // 2. Trigger typing indicator to show the bot is active
            await context.Channel.TriggerTypingAsync();

            try
            {
                // 3. Fetch data from RCSB PDB API
                HttpResponseMessage response = await _httpClient.GetAsync(url, HttpCompletionOption.ResponseHeadersRead);

                if (!response.IsSuccessStatusCode)
                {
                    await context.EditResponseAsync(new DiscordWebhookBuilder()
                        .WithContent($"❌ **Error:** Could not find protein ID `{pdbId.ToUpper()}` on the RCSB server."));
                    return;
                }

                // 4. Read response directly into an in-memory stream
                using (Stream apiStream = await response.Content.ReadAsStreamAsync())
                {
                    string fileName = $"{cleanId}.cif.gz";

                    // 5. Construct message with the streaming file attachment
                    var messageBuilder = new DiscordMessageBuilder()
                        .WithContent($"🧬 **Protein Data Bank Download**\n" +
                                     $"Here is your dynamically requested modern `.cif.gz` structural file for **{pdbId.ToUpper()}**! " +
                                     $"Open this inside viewing suites like PyMOL or ChimeraX.")
                        .AddFile(fileName, apiStream);

                    Console.WriteLine("Protein Length: " + apiStream.Length);

                    // Send the constructed package to the active channel
                    await context.EditResponseAsync(new DiscordWebhookBuilder()
                        .WithContent(messageBuilder.Content));
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"DSharpPlus Bot Error: {ex.Message}");
                await context.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent("⚠️ An unexpected error occurred while fetching or uploading the protein file."));
            }
        }
    }
}