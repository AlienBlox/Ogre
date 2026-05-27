# Step 1: Build the application using the .NET SDK image
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build-env
WORKDIR /app

# Copy the project file and restore dependencies
COPY *.csproj ./
RUN dotnet restore

# Copy the rest of the files and build the release binaries
COPY . ./
RUN dotnet publish -c Release -o out

# Step 2: Build the runtime container using the lightweight runtime image
FROM mcr.microsoft.com/dotnet/runtime:10.0
WORKDIR /app
COPY --from=build-env /app/out .

# Execute the application assembly
ENTRYPOINT ["dotnet", "OgreBotSharp.dll"]
