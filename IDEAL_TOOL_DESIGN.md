# Ideal Star Citizen Localization Tool - Design Document

## Philosophy

A well-designed localization tool should be:
1. **Safe** - Never corrupt game files, always have backups
2. **Smart** - Auto-detect installations, validate changes, warn about issues
3. **Simple** - Easy for casual users, powerful for advanced users
4. **Shareable** - Easy to distribute translation packs to the community

## Technology Stack Choice

### Option 1: Python (RECOMMENDED)
**Pros:**
- Cross-platform (Windows, Linux, Mac)
- Rich ecosystem (configparser, pathlib, rich for beautiful CLI)
- Easy to distribute with PyInstaller (single .exe)
- Readable code for community contributions
- Great for both CLI and GUI (with tkinter/PyQt)

**Cons:**
- Requires Python runtime (unless compiled)
- Slightly slower than compiled languages

### Option 2: Go
**Pros:**
- Single binary, no dependencies
- Fast execution
- Cross-platform compilation
- Good standard library

**Cons:**
- Less accessible for casual contributors
- Smaller ecosystem for GUI

### Option 3: Electron/Tauri (GUI App)
**Pros:**
- Beautiful modern UI
- Cross-platform
- Web technologies (familiar to many)
- Could host online version

**Cons:**
- Large bundle size (Electron)
- Overkill for simple merging
- Longer development time

**CHOICE: Python with optional GUI**

## Core Architecture

```
sc-localization-tool/
├── cli.py                 # Command-line interface
├── gui.py                 # Optional GUI wrapper
├── core/
│   ├── parser.py         # INI parser with error recovery
│   ├── merger.py         # Merge logic with conflict detection
│   ├── validator.py      # Validate translations before applying
│   ├── detector.py       # Auto-detect game installation
│   └── backup.py         # Backup/restore functionality
├── models/
│   ├── translation.py    # Translation entry model
│   ├── project.py        # Project/translation pack model
│   └── config.py         # Tool configuration
├── utils/
│   ├── file_ops.py       # Safe file operations with locks
│   ├── version.py        # Game version detection/tracking
│   └── diff.py           # Show changes before applying
└── packs/                # Community translation packs
    ├── asop_terminal/
    ├── immersive_hud/
    └── memes/
```

## Key Features

### 1. Smart Game Detection
```python
# Auto-detect common installation paths
detected = [
    "C:/Program Files/Roberts Space Industries/StarCitizen/LIVE",
    "D:/Games/StarCitizen/LIVE",
    # Check registry for launcher install path
    # Check Epic Games Store paths
    # Check environment variables
]

# Ask user to confirm or provide custom path
game_path = auto_detect_or_prompt()
```

### 2. Project-Based Workflow
```yaml
# translation_project.yaml
name: "Immersive HUD Pack"
author: "YourName"
version: "1.0.0"
game_version: "4.3.2"
description: "Makes the HUD more immersive and less game-like"

translations:
  - file: global.ini
    changes:
      - key: ui_hud_speed
        original: "Speed"
        new: "Velocity"
        category: "hud"
        comment: "More technical term"

      - key: ui_hud_fuel
        original: "Fuel"
        new: "Hydrogen Level"
        category: "hud"
```

### 3. Interactive Translation Editor
```python
# CLI Interactive Mode
$ sc-loc edit

> Search for text to translate: "landing pad"

Found 5 matches:
[1] ui_asop_landing_pad = "Landing Pad"
[2] ui_landing_request = "Request Landing"
[3] tooltip_landing = "Your assigned landing location"

> Select entry to edit (1-3, or 'n' for next search): 1

Current: ui_asop_landing_pad = "Landing Pad"
New value: Your Ship's Parking Spot
Category [optional]: asop_terminal

✓ Added to translation project

> Continue? (y/n/save): y
```

### 4. Validation System
```python
class Validator:
    def validate_translation(self, key, original, new):
        warnings = []
        errors = []

        # Check for placeholder variables
        original_vars = re.findall(r'\{[^}]+\}', original)
        new_vars = re.findall(r'\{[^}]+\}', new)
        if set(original_vars) != set(new_vars):
            errors.append(f"Variable mismatch! Original: {original_vars}, New: {new_vars}")

        # Check length (UI constraints)
        if len(new) > len(original) * 1.5:
            warnings.append(f"New text is {len(new)}/{len(original)} chars - may not fit in UI")

        # Check for common mistakes
        if '\\n' in original and '\\n' not in new:
            warnings.append("Original has newline, yours doesn't")

        # Check encoding
        try:
            new.encode('utf-8')
        except UnicodeEncodeError:
            errors.append("Contains characters that can't be encoded in UTF-8")

        return warnings, errors
```

### 5. Safe File Operations
```python
class SafeFileWriter:
    def write_with_backup(self, target_path, content):
        # Create timestamped backup
        backup_path = self.create_backup(target_path)

        # Acquire file lock
        with FileLock(target_path):
            # Check if game is running
            if self.is_game_running():
                raise GameRunningError("Close Star Citizen before modifying files")

            # Verify write permissions
            if not os.access(target_path, os.W_OK):
                raise PermissionError(f"No write access to {target_path}")

            # Write to temp file first
            temp_path = f"{target_path}.tmp"
            self.write_utf8_no_bom(temp_path, content)

            # Verify written content
            if not self.verify_integrity(temp_path):
                os.remove(temp_path)
                raise IntegrityError("Written file failed verification")

            # Atomic rename
            os.replace(temp_path, target_path)

            print(f"✓ Success! Backup saved to: {backup_path}")
```

### 6. Diff Preview
```python
$ sc-loc apply my_translations.yaml --preview

Changes to be applied:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ASOP Terminal]
  ui_asop_retrieval
  - Retrieve Ship
  + Get Your Ship Back

  ui_asop_stored
  - Ship in Hangar
  + Chillin' in Storage

[HUD]
  hud_speed
  - Speed
  + Velocity
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Apply these changes? (yes/no/edit):
```

### 7. Version Management
```python
class GameVersionManager:
    def detect_game_version(self, game_path):
        # Read from version file or executable metadata
        version = self.read_version_info(game_path)
        return version

    def check_compatibility(self, translation_version, game_version):
        if translation_version != game_version:
            print(f"⚠️  Warning: Translation made for {translation_version}, you're running {game_version}")
            print("Some keys may have changed. Run 'sc-loc validate' to check.")
            return False
        return True

    def auto_migrate(self, old_translations, old_version, new_version):
        # Attempt to migrate translations to new version
        migration_log = self.load_migration_rules(old_version, new_version)
        updated = self.apply_migrations(old_translations, migration_log)
        return updated
```

### 8. Community Pack System
```python
$ sc-loc browse

Available Translation Packs:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1] Immersive HUD               by SpaceCowboy   ★★★★★ (523 downloads)
    Makes UI more lore-friendly

[2] ASOP Terminal Clarity       by MrKraken      ★★★★☆ (342 downloads)
    Clear terminal instructions

[3] Pirate Speak               by YarrMatey     ★★★☆☆ (89 downloads)
    Everything in pirate slang
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

$ sc-loc install immersive-hud
✓ Downloaded pack
✓ Verified signature
✓ Applied 127 translations
✓ Backup created

$ sc-loc uninstall immersive-hud
✓ Restored from backup
```

### 9. GUI Version (Optional)
```
┌─────────────────────────────────────────────────────────┐
│ Star Citizen Localization Tool                    v2.0  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Game Path: C:\...\LIVE        [Auto-detect] [Browse]   │
│ Version: 4.3.2                Status: ✓ Ready           │
│                                                          │
│ ┌──────────────────┬──────────────────────────────────┐ │
│ │ Translation List │ Editor                           │ │
│ │                  │                                  │ │
│ │ ☑ ASOP Terminal  │ Key: ui_asop_retrieval          │ │
│ │ ☐ HUD Text       │                                  │ │
│ │ ☐ Mission Dialog │ Original:                        │ │
│ │ ☐ Ship Names     │ Retrieve Ship                    │ │
│ │                  │                                  │ │
│ │ [+ New]          │ Translation:                     │ │
│ │ [Import Pack]    │ Get Your Ship Back               │ │
│ │                  │                                  │ │
│ │                  │ [Validate]  [Add Translation]    │ │
│ └──────────────────┴──────────────────────────────────┘ │
│                                                          │
│ [Preview Changes]  [Apply to Game]  [Export Pack]       │
└─────────────────────────────────────────────────────────┘
```

### 10. Advanced Features

#### A. Regex Search & Replace
```python
$ sc-loc replace --pattern "ui_.*_button" --find "Click" --replace "Press"

Found 23 matches. Preview:
  ui_main_button: "Click Here" → "Press Here"
  ui_submit_button: "Click to Submit" → "Press to Submit"

Apply? (y/n):
```

#### B. Translation Memory
```python
# Remember common translations across projects
memory = {
    "Ship": "Spacecraft",
    "Fuel": "Hydrogen",
    "Landing Pad": "Pad",
}

# Suggest translations based on history
$ sc-loc suggest "Landing Pad Assignment"
💡 Based on your history, you might want:
   "Landing Pad" → "Pad" (used 15 times)
   "Assignment" → "Designation" (used 8 times)

Suggested: "Pad Designation"
```

#### C. Collaborative Features
```python
$ sc-loc share my_asop_pack.yaml
✓ Uploaded to community hub
🔗 Share link: https://sc-loc.community/packs/abc123

$ sc-loc fork immersive-hud
✓ Created your own copy to modify

$ sc-loc pr --pack immersive-hud --add my_improvements.yaml
✓ Pull request submitted to pack author
```

## CLI Commands

```bash
# Setup
sc-loc init                    # Create new translation project
sc-loc config                  # Configure tool settings

# Editing
sc-loc edit                    # Interactive translation editor
sc-loc add <key> <value>       # Add single translation
sc-loc remove <key>            # Remove translation
sc-loc search <text>           # Search in source files

# Management
sc-loc validate                # Check translations for errors
sc-loc preview                 # Show diff of changes
sc-loc apply                   # Apply translations to game
sc-loc restore                 # Restore from backup

# Packs
sc-loc browse                  # Browse community packs
sc-loc install <pack>          # Install translation pack
sc-loc uninstall <pack>        # Uninstall pack
sc-loc export                  # Export your translations as pack
sc-loc share                   # Upload pack to community

# Maintenance
sc-loc backup                  # Create manual backup
sc-loc update                  # Check for tool updates
sc-loc doctor                  # Diagnose installation issues
```

## Configuration File

```yaml
# ~/.sc-loc/config.yaml
game:
  path: "C:/Program Files/Roberts Space Industries/StarCitizen/LIVE"
  auto_detect: true
  backup_before_write: true
  backup_count: 5  # Keep last 5 backups

editor:
  show_line_numbers: true
  syntax_highlighting: true
  word_wrap: true

validation:
  check_variables: true
  check_length: true
  length_tolerance: 1.5  # 150% of original length
  warn_special_chars: true

community:
  auto_check_updates: true
  allow_telemetry: false  # Anonymous usage stats
  trusted_authors: ["MrKraken", "SpaceCowboy"]

advanced:
  encoding: "utf-8-no-bom"
  line_endings: "crlf"  # Windows default
  preserve_formatting: true
  create_backups: true
```

## Error Handling Examples

```python
# Graceful degradation
try:
    game_path = auto_detect_game()
except GameNotFoundError:
    game_path = prompt_user_for_path()

# Helpful error messages
if not valid_utf8(translation):
    print("❌ Error: Translation contains invalid characters")
    print("   The game only supports UTF-8 encoding")
    print("   Problematic character at position 45: '�'")
    print("   Try: Remove or replace special characters")

# Recovery options
if file_locked:
    print("⚠️  File is locked (game may be running)")
    print("Options:")
    print("  1. Close Star Citizen and retry")
    print("  2. Save to output file instead")
    print("  3. Cancel")
    choice = get_user_choice()
```

## Testing Strategy

```python
# Unit tests
test_ini_parsing()
test_utf8_no_bom_writing()
test_variable_validation()
test_backup_restore()

# Integration tests
test_full_merge_workflow()
test_game_detection()
test_pack_install()

# End-to-end tests
test_cli_commands()
test_gui_workflow()

# Edge case tests
test_corrupted_ini_recovery()
test_permission_denied_handling()
test_disk_full_handling()
test_concurrent_access()
```

## Distribution

### For End Users
```bash
# Windows
> winget install sc-localization-tool
> sc-loc-installer.exe

# Linux
$ sudo apt install sc-localization-tool
$ pip install sc-localization-tool

# Portable
sc-loc-portable.exe  # Single executable, no install
```

### For Developers
```bash
$ git clone https://github.com/sc-community/sc-localization-tool
$ pip install -e .
$ pytest  # Run tests
```

## Future Enhancements

1. **Live Preview** - See changes in real-time with game running (if possible)
2. **Translation Services** - Integration with DeepL/Google Translate for quick drafts
3. **Voice Line Support** - When CIG adds audio, support subtitle timing
4. **Mod Manager Integration** - Work with existing SC mod managers
5. **Discord Bot** - Share packs, search translations via Discord
6. **Web Version** - Browser-based editor for quick edits
7. **Mobile Companion** - Browse/edit translations on phone
8. **AI Assistance** - Suggest consistent terminology across translations

## Why This Approach?

### Safety First
- Automatic backups prevent disasters
- Validation catches errors before they reach the game
- File locking prevents corruption
- Permission checking gives helpful messages

### User Experience
- Auto-detection removes manual configuration
- Interactive mode guides beginners
- Preview shows exactly what will change
- Clear error messages help troubleshooting

### Community Building
- Pack system encourages sharing
- Easy to install others' work
- Version tracking prevents incompatibilities
- Attribution built-in

### Maintainability
- Clean architecture separates concerns
- Comprehensive testing catches bugs
- Python makes community contributions easy
- Good documentation helps onboarding

### Extensibility
- Plugin system for custom validators
- Pack format allows creativity
- API for integration with other tools
- CLI and GUI share core logic

## Comparison: Current vs Ideal

| Feature | Current PowerShell | Ideal Tool |
|---------|-------------------|------------|
| Cross-platform | ❌ Windows only | ✅ Win/Mac/Linux |
| Game detection | ❌ Manual config | ✅ Auto-detect |
| Backups | ❌ Manual | ✅ Automatic |
| Validation | ❌ None | ✅ Comprehensive |
| Preview | ❌ None | ✅ Diff view |
| Error messages | ⚠️ Basic | ✅ Detailed |
| UTF-8 handling | ⚠️ Version-dependent | ✅ Always correct |
| Community sharing | ❌ Manual | ✅ Built-in |
| Interactive editing | ❌ Manual file edit | ✅ Guided workflow |
| GUI option | ❌ CLI only | ✅ Both CLI & GUI |
| Update checking | ❌ None | ✅ Auto-update |
| Project management | ❌ Single file | ✅ Full projects |

## Estimated Development Time

- **MVP (CLI only, basic features):** 2-3 weeks
- **Full CLI with all features:** 4-6 weeks
- **Add GUI:** +2-3 weeks
- **Community platform:** +3-4 weeks
- **Polish & testing:** +2 weeks

**Total for v1.0:** ~3 months with 1 developer
**Total for v2.0 (with community):** ~6 months

## Conclusion

The ideal tool would be **a Python-based CLI application** with an optional GUI that:
- Makes translation **safe** (backups, validation)
- Makes translation **easy** (auto-detect, interactive, preview)
- Makes translation **shareable** (packs, community hub)
- Makes translation **maintainable** (version tracking, migration)

It would transform localization from a technical task into a creative, community-driven activity that enhances everyone's Star Citizen experience.
