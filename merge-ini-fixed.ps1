##################
# String processing file - Fixed version with proper error handling and reporting
# Originally from /u/Asphalt_Expert's component stats language pack
# Enhanced by MrKraken, design flaws fixed by Claude
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

Write-Host "=== SC Localization Merge Tool ===" -ForegroundColor Cyan
Write-Host ""

# Check if files exist first, make folders for outputs if we need them
if (-not (Test-Path $targetStringsPath)) {
    Write-Error "target_strings.ini not found at: $targetStringsPath"
    exit 1
}
if (-not (Test-Path $globalIniPath)) {
    Write-Error "global.ini not found at: $globalIniPath"
    exit 1
}
if (-not (Test-Path $gameInstallPath)) {
    Write-Error "Directory not found: $gameInstallPath"
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
Write-Host "Loading target strings from: $targetStringsPath" -ForegroundColor Yellow
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
            Write-Warning "Line $lineNumber : Duplicate key '$key' found in target_strings.ini - using latest value"
        }

        $replacements[$key] = $value
    }
    else {
        Write-Warning "Line $lineNumber : Skipping invalid line: $_"
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
    $unusedKeys | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
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
    Write-Host "Merged file written to: $mergedIniPath" -ForegroundColor Green
}
catch {
    Write-Error "Failed to write merged.ini: $_"
    exit 1
}

# Write to game folder if requested
if ($gameIniWrite) {
    try {
        if ($PSVersionTable.PSVersion.Major -ge 6) {
            $processedContent | Set-Content $gameIniPath -Encoding UTF8NoBOM
        }
        else {
            $utf8NoBom = New-Object System.Text.UTF8Encoding $false
            [System.IO.File]::WriteAllLines($gameIniPath, $processedContent, $utf8NoBom)
        }
        Write-Host "Game file written to: $gameIniPath" -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to write to game folder: $_"
        Write-Host "Make sure the game is not running and you have write permissions." -ForegroundColor Yellow
        exit 1
    }
}
else {
    Write-Host "Game folder write disabled. Set `$gameIniWrite = `$true to enable." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Merge Complete ===" -ForegroundColor Cyan
