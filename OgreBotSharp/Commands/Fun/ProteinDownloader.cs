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
            if (string.IsNullOrWhiteSpace(pdbId) || pdbId.Length != 4)
            {
                await context.EditResponseAsync(new DiscordWebhookBuilder().WithContent("❌ **Invalid Format:** Please provide a valid 4-character PDB ID (e.g., `4HHB`)."));
                return;
            }

            // 2. Buy processing time to bypass the 3-second Slash Command timeout limit
            await context.DeferAsync();

            string cleanId = pdbId.Trim().ToLower();
            string url = $"https://files.rcsb.org/download/{cleanId}.cif.gz";

            try
            {
                // 3. Fetch from RCSB API
                HttpResponseMessage response = await _httpClient.GetAsync(url, HttpCompletionOption.ResponseHeadersRead);

                if (!response.IsSuccessStatusCode)
                {
                    await context.EditResponseAsync(new DiscordWebhookBuilder().WithContent($"❌ **Error:** Could not find protein ID `{pdbId.ToUpper()}` on the RCSB server."));
                    return;
                }

                // 4. Download file contents into temporary memory
                using (Stream apiStream = await response.Content.ReadAsStreamAsync())
                {
                    string fileName = $"{cleanId}.cif.gz";

                    // 🔥 CRITICAL FIX PART A: Clear the deferred "thinking" status placeholder message completely
                    await context.DeleteResponseAsync();

                    // 🔥 CRITICAL FIX PART B: Construct a brand new message builder object
                    var fileMessage = new DiscordMessageBuilder()
                        .WithContent($"🧬 **Protein Data Bank Download**\n" +
                                     $"Here is your dynamically requested modern `.cif.gz` structural file for **{pdbId.ToUpper()}**! " +
                                     $"Open this inside viewing suites like PyMOL or ChimeraX.")
                        .AddFile(fileName, apiStream);

                    // Send the fresh message directly to the channel with proper attachment streams
                    await context.Channel.SendMessageAsync(fileMessage);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"DSharpPlus Bot Error: {ex.Message}");

                // Fallback recovery check if DeleteResponseAsync hasn't fired yet
                try
                {
                    await context.EditResponseAsync(new DiscordWebhookBuilder().WithContent("⚠️ An unexpected error occurred while fetching or uploading the protein file."));
                }
                catch
                {
                    await context.Channel.SendMessageAsync("⚠️ An unexpected error occurred while processing your protein structure file.");
                }
            }
        }
    }
}