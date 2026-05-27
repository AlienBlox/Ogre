# Step 1: Use the official Microsoft .NET SDK image to build the app
FROM ://microsoft.com AS build-env
WORKDIR /app

# Copy the csproj file and restore any NuGet packages
COPY *.csproj ./
RUN dotnet restore

# Copy the remaining source files and compile the release binary
COPY . ./
RUN dotnet publish -c Release -o out

# Step 2: Build the runtime container using a lightweight .NET image
FROM ://microsoft.com
WORKDIR /app
COPY --from=build-env /app/out .

# Tell the container how to execute your application
# Replace "Bot" with the exact name of your compiled assembly (usually your project name)
ENTRYPOINT ["dotnet", "OgreBotSharp.dll"]
