param(
    [Parameter(Mandatory=$true)]
    [string]$TokenSet,
    
    [Parameter(Mandatory=$false)]
    [switch]$Rebuild,
    
    [Parameter(Mandatory=$true, ValueFromRemainingArguments=$true)]
    [string[]]$ModalArgs
)

# Get the directory of the script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Change to the parent directory (workspace root)
Set-Location (Split-Path -Parent $scriptDir)

# Check if the Docker image exists, if not, build it
if (-not (docker images -q modal-runner)) {
    Write-Host "Docker image not found. Building..."
    docker build -t modal-runner $scriptDir

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to build Docker image. Exiting."
        exit 1
    }
}
elseif ($Rebuild) {
    Write-Host "Rebuilding Docker image..."
    docker build -t modal-runner $scriptDir

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to build Docker image. Exiting."
        exit 1
    }
}

# Get Doppler configuration
$dopplerProject = doppler configure get project --plain
$dopplerConfig = doppler configure get config --plain
$dopplerToken = doppler configure get token --plain

$currentDir = (Get-Location).Path
docker run --rm -it `
    -v "${currentDir}:/workspace" `
    -e DOPPLER_TOKEN="$dopplerToken" `
    -e DOPPLER_PROJECT="$dopplerProject" `
    -e DOPPLER_CONFIG="$dopplerConfig" `
    modal-runner $TokenSet $ModalArgs