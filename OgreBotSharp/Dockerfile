# Step 1: Build the application using the .NET SDK image
FROM https://microsoft.com AS build-env
WORKDIR /app

# Copy the project file and restore dependencies
COPY *.csproj ./
RUN dotnet restore

# Copy the rest of the files and build the release binaries
COPY . ./
RUN dotnet publish -c Release -o out

# Step 2: Build the runtime container using the lightweight runtime image
FROM https://microsoft.com
WORKDIR /app
COPY --from=build-env /app/out .

# Execute the application assembly
ENTRYPOINT ["dotnet", "OgreBotSharp.dll"]
