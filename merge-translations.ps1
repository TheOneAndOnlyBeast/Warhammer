##################
# Star Citizen String Translation Merger Tool
# Originally based on ExoAE's ScCompLangPack (https://github.com/ExoAE/ScCompLangPack)
# Enhanced by MrKraken (https://www.youtube.com/@MrKraken)
# Design flaws fixed for reliable UTF-8 encoding and better error handling
##################

# User config - you can change these values
$gameInstallPath = 'C:\Program Files\Roberts Space Industries\StarCitizen\LIVE' # Set your game installation path here
$gameIniWrite = $false # Set to $true if you want to write directly to the game folder


################## !!!! ##################
# YOU SHOULD NOT NEED TO EDIT BELOW THIS LINE
################## !!!! ##################

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path # Get the script directory
$targetStringsPath = Join-Path $scriptDir 'target_strings.ini' # input file
$globalIniPath = Join-Path $scriptDir 'src\global.ini' # source file from Data.p4k
$mergedIniPath = Join-Path $scriptDir 'output\merged.ini' # Output file

Write-Host "=== Star Citizen String Translation Merger ===" -ForegroundColor Cyan
Write-Host ""

# Check if files exist first, make folders for outputs if we need them
if (-not (Test-Path $targetStringsPath)) {
    Write-Error "target_strings.ini not found at: $targetStringsPath"
    Write-Host "Create this file with your custom translations." -ForegroundColor Yellow
    exit 1
}
if (-not (Test-Path $globalIniPath)) {
    Write-Error "global.ini not found at: $globalIniPath"
    Write-Host "Extract global.ini from Data.p4k and place it in the 'src' folder." -ForegroundColor Yellow
    exit 1
}
if (-not (Test-Path $gameInstallPath)) {
    Write-Error "Directory not found: $gameInstallPath"
    Write-Host "Update `$gameInstallPath in the script to match your Star Citizen installation." -ForegroundColor Yellow
    exit 1
}
$outputDir = Split-Path $mergedIniPath -Parent
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    Write-Host "Created output directory: $outputDir" -ForegroundColor Green
}
$gameIniPath = Join-Path $gameInstallPath 'data\Localization\english\global.ini' # now we know the install folder is valid we can stitch on the localization path
if ($gameIniWrite) {
    $gameLocalizationDir = Split-Path $gameIniPath -Parent
    if (-not (Test-Path $gameLocalizationDir)) {
        New-Item -ItemType Directory -Path $gameLocalizationDir -Force | Out-Null
        Write-Host "Created game localization directory: $gameLocalizationDir" -ForegroundColor Green
    }
}

# Load target_strings.ini into a hashtable (key -> new value)
Write-Host "Loading target strings from: target_strings.ini" -ForegroundColor Yellow
$replacements = @{}
$lineNumber = 0
Get-Content $targetStringsPath -Encoding UTF8 | ForEach-Object {
    $lineNumber++
    $line = $_.Trim()

    # Skip empty lines and comments
    if ($line -eq '' -or $line.StartsWith('#') -or $line.StartsWith(';')) {
        return
    }

    # Match key=value pairs
    if ($line -match '^([^=]+?)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2]  # Keep value as-is to preserve intentional formatting

        if ($replacements.ContainsKey($key)) {
            Write-Warning "Line $lineNumber : Duplicate key '$key' found - using latest value"
        }

        $replacements[$key] = $value
    }
    else {
        Write-Warning "Line $lineNumber : Skipping invalid line format"
    }
}

Write-Host "Loaded $($replacements.Count) translation strings" -ForegroundColor Green
Write-Host ""

# Track statistics
$stats = @{
    TotalLines = 0
    ReplacedKeys = 0
    UnchangedKeys = 0
    Comments = 0
    EmptyLines = 0
}
$usedKeys = @{}

# Process global.ini line by line and only replace values for keys found in the hashtable
Write-Host "Processing global.ini..." -ForegroundColor Yellow
$processedContent = Get-Content $globalIniPath -Encoding UTF8 | ForEach-Object {
    $stats.TotalLines++
    $line = $_
    $trimmedLine = $line.Trim()

    # Preserve empty lines
    if ($trimmedLine -eq '') {
        $stats.EmptyLines++
        return $line
    }

    # Preserve comments (lines starting with # or ;)
    if ($trimmedLine.StartsWith('#') -or $trimmedLine.StartsWith(';')) {
        $stats.Comments++
        return $line
    }

    # Match key=value pairs, excluding comments
    if ($line -match '^([^=]+?)=(.*)$') {
        $key = $matches[1].Trim()
        $originalValue = $matches[2]

        if ($replacements.ContainsKey($key)) {
            # Found a replacement - preserve any leading whitespace from original key, then add key=newvalue
            $leadingWhitespace = ''
            if ($line -match '^(\s*)') {
                $leadingWhitespace = $matches[1]
            }

            $stats.ReplacedKeys++
            $usedKeys[$key] = $true

            # Return the new line with consistent formatting
            return "$leadingWhitespace$key=$($replacements[$key])"
        }
        else {
            $stats.UnchangedKeys++
            return $line
        }
    }
    else {
        # Lines that don't match the pattern (like section headers [Section])
        return $line
    }
}

Write-Host "Processing complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Statistics:" -ForegroundColor Cyan
Write-Host "  Total lines processed: $($stats.TotalLines)"
Write-Host "  Keys replaced: $($stats.ReplacedKeys)" -ForegroundColor Green
Write-Host "  Keys unchanged: $($stats.UnchangedKeys)"
Write-Host "  Comments preserved: $($stats.Comments)"
Write-Host "  Empty lines: $($stats.EmptyLines)"
Write-Host ""

# Check for unused keys in target_strings.ini
$unusedKeys = $replacements.Keys | Where-Object { -not $usedKeys.ContainsKey($_) }
if ($unusedKeys.Count -gt 0) {
    Write-Warning "The following $($unusedKeys.Count) keys from target_strings.ini were NOT found in global.ini:"
    Write-Host "  (These may be typos, outdated keys, or from a different game version)" -ForegroundColor Yellow
    $unusedKeys | Sort-Object | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    Write-Host ""
}

# Write to merged.ini with UTF8 NO BOM to avoid game parsing issues
try {
    # PowerShell 6+ uses UTF8NoBOM by default, but PS 5.1 needs explicit handling
    if ($PSVersionTable.PSVersion.Major -ge 6) {
        $processedContent | Set-Content $mergedIniPath -Encoding UTF8NoBOM
    }
    else {
        # For PS 5.1, write as UTF8 without BOM using .NET
        $utf8NoBom = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::WriteAllLines($mergedIniPath, $processedContent, $utf8NoBom)
    }
    Write-Host "SUCCESS: Merged file written to: output\merged.ini" -ForegroundColor Green
}
catch {
    Write-Error "Failed to write merged.ini: $_"
    exit 1
}

# Write to game folder if requested
if ($gameIniWrite) {
    Write-Host ""
    Write-Host "Writing to game folder..." -ForegroundColor Yellow
    try {
        if ($PSVersionTable.PSVersion.Major -ge 6) {
            $processedContent | Set-Content $gameIniPath -Encoding UTF8NoBOM
        }
        else {
            $utf8NoBom = New-Object System.Text.UTF8Encoding $false
            [System.IO.File]::WriteAllLines($gameIniPath, $processedContent, $utf8NoBom)
        }
        Write-Host "SUCCESS: Game file written to: $gameIniPath" -ForegroundColor Green
        Write-Host ""
        Write-Host "IMPORTANT: Make sure your user.cfg contains the line:" -ForegroundColor Cyan
        Write-Host "  g_language = english" -ForegroundColor White
    }
    catch {
        Write-Error "Failed to write to game folder: $_"
        Write-Host ""
        Write-Host "Troubleshooting:" -ForegroundColor Yellow
        Write-Host "  1. Make sure Star Citizen is completely closed" -ForegroundColor White
        Write-Host "  2. Check you have write permissions to the game folder" -ForegroundColor White
        Write-Host "  3. Try running PowerShell as Administrator" -ForegroundColor White
        Write-Host ""
        Write-Host "You can manually copy output\merged.ini to the game folder instead." -ForegroundColor Yellow
        exit 1
    }
}
else {
    Write-Host ""
    Write-Host "Game folder write is DISABLED." -ForegroundColor Yellow
    Write-Host "To enable automatic game folder updates:" -ForegroundColor White
    Write-Host "  1. Edit merge-translations.ps1" -ForegroundColor White
    Write-Host "  2. Change `$gameIniWrite = `$false to `$gameIniWrite = `$true" -ForegroundColor White
    Write-Host ""
    Write-Host "Or manually copy output\merged.ini to:" -ForegroundColor White
    Write-Host "  $gameIniPath" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== Merge Complete ===" -ForegroundColor Cyan
Write-Host ""
