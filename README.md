# Star Citizen String Translation Merger Tool

> [!NOTE]
> Originally based on [ExoAE's ScCompLangPack](https://github.com/ExoAE/ScCompLangPack) idea but rather than another fork, I decided instead to tweak the merge tool to make it more usable. `target_strings.ini` is provided for example of organizing your ASOP terminals and other customizations.

### 🗒️ Current String Base: `sc-alpha-4.3.2.10452200`

## 📝 What it Does
- Takes `target_strings.ini` as the input file & `global.ini` as source file from Data.p4k
- Finds the keys from input, matches them to source and replaces the value
- Outputs `merged.ini` to the `output/` folder
- Optionally outputs directly to the specified game file location
- **NEW**: UTF-8 without BOM encoding (fixes game parsing issues)
- **NEW**: Detailed statistics and unused key detection
- **NEW**: Proper error handling with helpful troubleshooting messages

## 🗺️ Usage

### First Time Setup

1. **Extract global.ini from Data.p4k**
   - Use a tool to extract `global.ini` from the game's Data.p4k file
   - Place it in the `src/` folder of this tool

2. **Find strings you want to customize**
   - Open `src/global.ini` (or `src/vehicles.ini`)
   - Search for the text you want to change
   - Copy the entire line (e.g., `ui_button_label=Click Here`)

3. **Create your translations**
   - Open or create `target_strings.ini`
   - Paste the lines you copied
   - Modify the values after the `=` sign
   - Example:
     ```ini
     # Custom ASOP Terminal Text
     ui_button_label=Press This Button
     tooltip_landing_pad=Your Ship's Home
     ```

4. **Configure user.cfg**
   - If you already have a `user.cfg` file in `StarCitizen\LIVE`, add the line:
     ```
     g_language = english
     ```
   - If not, copy `src\user.example.cfg`, rename it to `user.cfg`, and place it in your `StarCitizen\LIVE` folder

### Running the Tool

#### Option 1: Test First (Recommended)
1. Right-click `merge-translations.ps1` and select **Run with PowerShell**
2. If prompted about execution policy, press `R` then `Enter`
3. Check the output in `output\merged.ini`
4. Manually copy it to your game folder to test

#### Option 2: Direct Game Folder Write
1. Open `merge-translations.ps1` in a text editor
2. Update the `$gameInstallPath` if it's not the default location
3. Change `$gameIniWrite = $false` to `$gameIniWrite = $true`
4. Right-click `merge-translations.ps1` and select **Run with PowerShell**
5. The tool will write directly to: `StarCitizen\LIVE\data\Localization\english\global.ini`

### Verifying Changes

1. Navigate to your Star Citizen install location
2. Open `data\Localization\english\global.ini`
3. Search for one of your custom strings using `Ctrl+F`
4. Launch Star Citizen and check in-game

## 🛠️ General Localization Installation

Any translation (localization) files you download should go in your Star Citizen install folder (LIVE, PTU, TECH-PREVIEW, etc.) in the following structure:

```
StarCitizen/
└── LIVE/
    ├── user.cfg
    └── data/
        └── Localization/
            └── english/
                └── global.ini
```

**Required in user.cfg:**
```
g_language = english
```

## 🔧 What's New in This Fixed Version

### Critical Fixes
- **UTF-8 BOM Issue**: Fixed encoding that was breaking game file parsing
- **Comment Handling**: Properly skips comment lines starting with `#` or `;`
- **Error Handling**: Helpful error messages instead of cryptic crashes
- **Duplicate Detection**: Warns when the same key appears multiple times

### New Features
- **Statistics Report**: See how many keys were replaced
- **Unused Key Detection**: Warns about translations for non-existent keys
- **Color-Coded Output**: Easy to read console feedback
- **PowerShell Version Detection**: Works with both PS 5.1 and 6+

### Example Output
```
=== Star Citizen String Translation Merger ===

Loading target strings from: target_strings.ini
Loaded 45 translation strings

Processing global.ini...
Processing complete!

Statistics:
  Total lines processed: 1234
  Keys replaced: 45
  Keys unchanged: 1189
  Comments preserved: 12
  Empty lines: 23

SUCCESS: Merged file written to: output\merged.ini

=== Merge Complete ===
```

## ⚠️ Troubleshooting

### "Execution policy" error
If PowerShell won't run the script:
1. Right-click PowerShell and "Run as Administrator"
2. Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. Press `Y` to confirm
4. Try running the script again

### "Failed to write to game folder"
- Make sure Star Citizen is **completely closed**
- Check you have **write permissions** to the game folder
- Try running PowerShell as **Administrator**
- Or just manually copy `output\merged.ini` to the game folder

### "Keys were NOT found in global.ini" warning
This means you have translations for keys that don't exist in the game file:
- Check for **typos** in key names
- Keys may be **outdated** from a previous game version
- Keys may be in a different file like `vehicles.ini`

### Changes don't appear in-game
1. Verify `user.cfg` contains `g_language = english`
2. Check `data\Localization\english\global.ini` exists
3. Search for your custom text in the file to verify it was written
4. Restart Star Citizen completely

## 🤔 Is this... legit?

> [!IMPORTANT]
> **Made by the Community** - This is an unofficial Star Citizen fan project, not affiliated with the Cloud Imperium group of companies. All content in this repository not authored by its host or users are property of their respective owners.

- The ability to customize your localization using the extracted global.ini file is **intended/authorized by CIG** to support community-made translations until it is officially integrated
  - *[Star Citizen: Community Localization Update](https://robertsspaceindustries.com/spectrum/community/SC/forum/1/thread/star-citizen-community-localization-update)* 2023-10-11
- Considered as third-party contributions, **use at your own discretion**
- [RSI Terms of Service](https://robertsspaceindustries.com/en/tos)
- [Translation & Fan Localization Statement](https://support.robertsspaceindustries.com/hc/en-us/articles/360006895793-Star-Citizen-Fankit-and-Fandom-FAQ#h_01JNKSPM7MRSB1WNBW6FGD2H98)

## 📁 Project Structure

```
SCLocalizationMergeTool/
├── merge-translations.ps1    # Main script
├── target_strings.ini         # Your custom translations (edit this!)
├── README.md                  # This file
├── FIXES.md                   # Detailed technical documentation
├── src/
│   ├── global.ini            # Extracted from Data.p4k
│   ├── vehicles.ini          # (Optional) Vehicle strings
│   └── user.example.cfg      # Example user.cfg
└── output/
    └── merged.ini            # Generated output file
```

## 🙏 Credits

- **Original Concept**: [/u/Asphalt_Expert](https://github.com/ExoAE/ScCompLangPack)
- **Enhanced Tool**: [MrKraken](https://www.youtube.com/@MrKraken)
- **Bug Fixes**: Community contributions
- **Star Citizen**: Cloud Imperium Games

## 📜 License

This is a community tool. See individual file headers for attribution.
