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

if ($Rebuild) {
    Write-Host "Rebuilding Docker image..."
    docker build -t modal-runner $scriptDir

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to build Docker image. Exiting."
        exit 1
    }
}

# Run the Docker container with the selected token set and Modal arguments
$currentDir = (Get-Location).Path
docker run --rm -it -v "${currentDir}:/workspace" modal-runner $TokenSet $ModalArgs
