# SC Localization Merge Tool - Design Flaws Fixed

## Critical Issues Fixed

### 1. **UTF-8 BOM (Byte Order Mark) Issue** ⚠️ CRITICAL
**Problem:** The original script used `-Encoding UTF8` which in PowerShell 5.1 adds a BOM to the file. Many applications, including Star Citizen, cannot properly parse UTF-8 files with BOM, causing the localization to fail silently or crash.

**Fix:**
- PowerShell 6+: Use `-Encoding UTF8NoBOM`
- PowerShell 5.1: Use .NET `System.Text.UTF8Encoding($false)` to write without BOM

```powershell
# Old (adds BOM):
$processedContent | Set-Content $mergedIniPath -Encoding UTF8

# New (no BOM):
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllLines($mergedIniPath, $processedContent, $utf8NoBom)
```

### 2. **Comment Handling**
**Problem:** Lines starting with `;` or `#` (standard INI comment formats) were being processed as key-value pairs if they contained `=`, potentially corrupting the output.

**Fix:** Explicitly skip lines that start with `#` or `;` after trimming whitespace.

```powershell
# Skip empty lines and comments
if ($line -eq '' -or $line.StartsWith('#') -or $line.StartsWith(';')) {
    return
}
```

### 3. **No Validation or Reporting**
**Problem:** Users had no visibility into:
- How many keys were successfully merged
- Which keys from target_strings.ini weren't found in global.ini
- What went wrong if the merge failed

**Fix:** Added comprehensive statistics and warnings:
- Total lines processed
- Keys replaced vs unchanged
- Comments and empty lines preserved
- List of unused keys from target_strings.ini
- Color-coded console output

### 4. **No Error Handling**
**Problem:** If files were locked (game running) or permissions were insufficient, the script would fail with cryptic errors.

**Fix:** Added try-catch blocks with user-friendly error messages:
```powershell
try {
    # Write file
}
catch {
    Write-Error "Failed to write to game folder: $_"
    Write-Host "Make sure the game is not running and you have write permissions."
    exit 1
}
```

### 5. **Duplicate Key Detection**
**Problem:** If target_strings.ini had duplicate keys, the script silently used the last value without warning the user.

**Fix:** Added detection and warning for duplicate keys:
```powershell
if ($replacements.ContainsKey($key)) {
    Write-Warning "Duplicate key '$key' found - using latest value"
}
```

### 6. **Inconsistent Whitespace Handling**
**Problem:** The original script trimmed keys but not values, and mixed formatting from both source files.

**Fix:**
- Keys are trimmed for consistent matching
- Values are preserved as-is to maintain intentional formatting
- Leading whitespace before keys is preserved to maintain file structure

## Usage Improvements

### Visual Feedback
The fixed version provides clear, color-coded output:
- **Cyan**: Section headers
- **Green**: Success messages and counts
- **Yellow**: Warnings and informational messages
- **Red**: Errors

### Statistics Report
```
Statistics:
  Total lines processed: 1234
  Keys replaced: 45
  Keys unchanged: 1189
  Comments preserved: 12
  Empty lines: 23
```

### Unused Key Detection
```
WARNING: The following 3 keys from target_strings.ini were NOT found in global.ini:
  - ui_old_button_label
  - deprecated_tooltip
  - test_string
```

## Testing Recommendations

1. **Backup First**: Always backup your original global.ini before running
2. **Dry Run**: Keep `$gameIniWrite = $false` initially to test output
3. **Verify Output**: Check `output/merged.ini` before enabling game writes
4. **Close Game**: Ensure Star Citizen is completely closed before writing to game folder
5. **Verify Encoding**: Use a hex editor to confirm no BOM (file should NOT start with `EF BB BF`)

## PowerShell Version Compatibility

- ✅ PowerShell 5.1 (Windows default)
- ✅ PowerShell 6.x
- ✅ PowerShell 7.x+

The script automatically detects the PowerShell version and uses the appropriate UTF-8 encoding method.
