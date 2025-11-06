# Output Folder

This folder contains the generated merged localization file.

## Generated Files

- **merged.ini** - The result of merging your `target_strings.ini` with `src/global.ini`

## Usage

After running `merge-translations.ps1`, you can:

1. **Test manually**: Copy `merged.ini` to your Star Citizen folder:
   ```
   StarCitizen\LIVE\data\Localization\english\global.ini
   ```

2. **Automatic write**: Enable `$gameIniWrite = $true` in the script to write directly

## Note

The `merged.ini` file is regenerated each time you run the merge script.
