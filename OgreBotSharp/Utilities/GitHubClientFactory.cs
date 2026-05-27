using Microsoft.IdentityModel.JsonWebTokens;
using Microsoft.IdentityModel.Tokens;
using Octokit;
using System.Security.Cryptography;

namespace OgreBotSharp.Utilities
{
    public static class GitHubClientFactory
    {
        private static readonly string AppId = Environment.GetEnvironmentVariable("GH_APP_ID") ?? "";
        private static readonly string InstallationId = Environment.GetEnvironmentVariable("GH_INSTALLATION_ID") ?? "";
        private static readonly string PrivateKeyPem = Environment.GetEnvironmentVariable("GH_PRIVATE_KEY") ?? "";

        public static async Task<GitHubClient> GetAuthenticatedClientAsync()
        {
            var githubClient = new GitHubClient(new ProductHeaderValue("DiscordBot-ReportSystem"));

            // 1. Generate JWT signed with your GitHub App's Private Key
            using var rsa = RSA.Create();
            rsa.ImportFromPem(PrivateKeyPem.ToCharArray());

            var handler = new JsonWebTokenHandler();
            var jwt = handler.CreateToken(new SecurityTokenDescriptor
            {
                Issuer = AppId,
                Expires = DateTime.UtcNow.AddMinutes(10),
                IssuedAt = DateTime.UtcNow,
                SigningCredentials = new SigningCredentials(new RsaSecurityKey(rsa), SecurityAlgorithms.RsaSha256)
            });

            // 2. Authenticate as the App to fetch the installation token
            githubClient.Credentials = new Credentials(jwt, AuthenticationType.Bearer);

            var response = await githubClient.GitHubApps.CreateInstallationToken(long.Parse(InstallationId));

            // 3. Re-authenticate using the scoped installation access token
            githubClient.Credentials = new Credentials(response.Token);
            return githubClient;
        }
    }
}