#!/usr/bin/env python3
"""
Star Citizen Localization Tool - Proof of Concept
Demonstrates ideal architecture and features
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class ValidationLevel(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    level: ValidationLevel
    message: str
    key: Optional[str] = None


@dataclass
class Translation:
    key: str
    original: str
    translated: str
    category: str = "general"
    comment: str = ""

    def to_dict(self):
        return asdict(self)


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

    @staticmethod
    def strip_if_no_tty():
        """Remove colors if not in a terminal"""
        if not hasattr(os.sys.stdout, 'isatty') or not os.sys.stdout.isatty():
            for attr in dir(Colors):
                if not attr.startswith('_') and attr != 'strip_if_no_tty':
                    setattr(Colors, attr, '')


class GameDetector:
    """Auto-detect Star Citizen installation"""

    COMMON_PATHS = [
        "C:/Program Files/Roberts Space Industries/StarCitizen/LIVE",
        "D:/Program Files/Roberts Space Industries/StarCitizen/LIVE",
        "E:/Games/StarCitizen/LIVE",
        "C:/Games/StarCitizen/LIVE",
    ]

    @classmethod
    def find_game(cls) -> Optional[Path]:
        """Try to auto-detect game installation"""
        print(f"{Colors.CYAN}🔍 Searching for Star Citizen installation...{Colors.END}")

        for path_str in cls.COMMON_PATHS:
            path = Path(path_str)
            if cls.is_valid_game_path(path):
                print(f"{Colors.GREEN}✓ Found: {path}{Colors.END}")
                return path

        print(f"{Colors.YELLOW}⚠️  Could not auto-detect game installation{Colors.END}")
        return None

    @staticmethod
    def is_valid_game_path(path: Path) -> bool:
        """Check if path looks like a valid SC installation"""
        if not path.exists():
            return False

        # Check for expected directories
        data_dir = path / "data"
        if not data_dir.exists():
            return False

        return True

    @staticmethod
    def get_localization_path(game_path: Path) -> Path:
        """Get the localization directory path"""
        return game_path / "data" / "Localization" / "english"


class INIParser:
    """Robust INI parser with error recovery"""

    @staticmethod
    def parse(file_path: Path) -> Dict[str, str]:
        """Parse INI file into key-value dict"""
        data = {}
        line_num = 0

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig strips BOM
                for line in f:
                    line_num += 1
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith(('#', ';')):
                        continue

                    # Parse key=value
                    if '=' in line:
                        key, _, value = line.partition('=')
                        key = key.strip()
                        value = value.strip()

                        if key:  # Only add if key is not empty
                            data[key] = value

        except UnicodeDecodeError as e:
            print(f"{Colors.RED}❌ Error: File is not UTF-8 encoded at line {line_num}{Colors.END}")
            raise

        return data

    @staticmethod
    def write(file_path: Path, data: Dict[str, str], preserve_structure: bool = False):
        """Write INI file as UTF-8 without BOM"""
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write as UTF-8 without BOM
        with open(file_path, 'w', encoding='utf-8', newline='\r\n') as f:
            for key, value in data.items():
                f.write(f"{key}={value}\n")


class TranslationValidator:
    """Validate translations for common issues"""

    @staticmethod
    def validate(translation: Translation, original_value: str) -> List[ValidationResult]:
        """Run all validation checks"""
        results = []

        # Check variable placeholders
        results.extend(TranslationValidator._check_variables(translation, original_value))

        # Check length
        results.extend(TranslationValidator._check_length(translation, original_value))

        # Check special characters
        results.extend(TranslationValidator._check_special_chars(translation))

        # Check encoding
        results.extend(TranslationValidator._check_encoding(translation))

        return results

    @staticmethod
    def _check_variables(trans: Translation, original: str) -> List[ValidationResult]:
        """Check if variable placeholders match"""
        results = []

        # Find variables like {var}, %s, %d, etc.
        original_vars = set(re.findall(r'\{[^}]+\}|%[sd]', original))
        translated_vars = set(re.findall(r'\{[^}]+\}|%[sd]', trans.translated))

        if original_vars != translated_vars:
            missing = original_vars - translated_vars
            extra = translated_vars - original_vars

            msg = f"Variable mismatch in '{trans.key}'"
            if missing:
                msg += f"\n  Missing: {missing}"
            if extra:
                msg += f"\n  Extra: {extra}"

            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message=msg,
                key=trans.key
            ))

        return results

    @staticmethod
    def _check_length(trans: Translation, original: str) -> List[ValidationResult]:
        """Check if translation is suspiciously longer than original"""
        results = []

        if len(trans.translated) > len(original) * 1.5:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"'{trans.key}' is much longer ({len(trans.translated)} vs {len(original)} chars) - may not fit in UI",
                key=trans.key
            ))

        return results

    @staticmethod
    def _check_special_chars(trans: Translation) -> List[ValidationResult]:
        """Check for problematic characters"""
        results = []

        # Check for newlines
        if '\\n' in trans.translated or '\n' in trans.translated:
            results.append(ValidationResult(
                level=ValidationLevel.INFO,
                message=f"'{trans.key}' contains newlines - verify formatting",
                key=trans.key
            ))

        return results

    @staticmethod
    def _check_encoding(trans: Translation) -> List[ValidationResult]:
        """Check if translation can be encoded as UTF-8"""
        results = []

        try:
            trans.translated.encode('utf-8')
        except UnicodeEncodeError as e:
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message=f"'{trans.key}' contains character that can't be encoded: {e}",
                key=trans.key
            ))

        return results


class BackupManager:
    """Manage backups of game files"""

    def __init__(self, backup_dir: Path):
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, file_path: Path) -> Path:
        """Create timestamped backup of file"""
        if not file_path.exists():
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(file_path, backup_path)

        # Keep only last 5 backups
        self._cleanup_old_backups(file_path.stem, keep=5)

        return backup_path

    def _cleanup_old_backups(self, file_stem: str, keep: int = 5):
        """Remove old backups, keeping only the most recent N"""
        backups = sorted(
            self.backup_dir.glob(f"{file_stem}_*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        for old_backup in backups[keep:]:
            old_backup.unlink()

    def list_backups(self) -> List[Path]:
        """List all available backups"""
        return sorted(
            self.backup_dir.glob("*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

    def restore(self, backup_path: Path, target_path: Path):
        """Restore from backup"""
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        shutil.copy2(backup_path, target_path)


class TranslationMerger:
    """Core merge logic"""

    def __init__(self, game_path: Path):
        self.game_path = game_path
        self.backup_manager = BackupManager(Path("backups"))
        self.validator = TranslationValidator()

    def merge(self,
              source_file: Path,
              translations: List[Translation],
              output_file: Path,
              validate: bool = True) -> Tuple[Dict[str, str], List[ValidationResult]]:
        """
        Merge translations into source file

        Returns:
            (merged_data, validation_results)
        """
        # Parse source file
        print(f"{Colors.CYAN}📖 Reading source file: {source_file.name}{Colors.END}")
        source_data = INIParser.parse(source_file)
        print(f"   Found {len(source_data)} keys")

        # Validate translations
        all_validation_results = []
        if validate:
            print(f"{Colors.CYAN}🔍 Validating translations...{Colors.END}")
            for trans in translations:
                original = source_data.get(trans.key, "")
                results = self.validator.validate(trans, original)
                all_validation_results.extend(results)

        # Apply translations
        merged_data = source_data.copy()
        applied = 0
        not_found = []

        for trans in translations:
            if trans.key in merged_data:
                merged_data[trans.key] = trans.translated
                applied += 1
            else:
                not_found.append(trans.key)

        print(f"{Colors.GREEN}✓ Applied {applied} translations{Colors.END}")

        if not_found:
            print(f"{Colors.YELLOW}⚠️  {len(not_found)} keys not found in source:{Colors.END}")
            for key in not_found[:5]:  # Show first 5
                print(f"   - {key}")
            if len(not_found) > 5:
                print(f"   ... and {len(not_found) - 5} more")

        # Write merged file
        print(f"{Colors.CYAN}💾 Writing merged file: {output_file.name}{Colors.END}")
        INIParser.write(output_file, merged_data)

        return merged_data, all_validation_results

    def apply_to_game(self, merged_file: Path, game_file_name: str = "global.ini"):
        """Apply merged file to game directory"""
        loc_dir = GameDetector.get_localization_path(self.game_path)
        target_file = loc_dir / game_file_name

        # Create backup
        print(f"{Colors.CYAN}💾 Creating backup...{Colors.END}")
        if target_file.exists():
            backup_path = self.backup_manager.create_backup(target_file)
            print(f"{Colors.GREEN}✓ Backup saved: {backup_path.name}{Colors.END}")

        # Ensure directory exists
        loc_dir.mkdir(parents=True, exist_ok=True)

        # Copy merged file to game
        print(f"{Colors.CYAN}📋 Copying to game directory...{Colors.END}")
        shutil.copy2(merged_file, target_file)
        print(f"{Colors.GREEN}✓ Applied to: {target_file}{Colors.END}")


class TranslationProject:
    """Manage translation projects"""

    def __init__(self, project_file: Path):
        self.project_file = project_file
        self.translations: List[Translation] = []
        self.metadata = {
            "name": "Untitled Project",
            "author": "",
            "version": "1.0.0",
            "game_version": "",
            "description": ""
        }

    def load(self):
        """Load project from JSON file"""
        if not self.project_file.exists():
            return

        with open(self.project_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.metadata = data.get('metadata', self.metadata)

        translations_data = data.get('translations', [])
        self.translations = [Translation(**t) for t in translations_data]

    def save(self):
        """Save project to JSON file"""
        data = {
            "metadata": self.metadata,
            "translations": [t.to_dict() for t in self.translations]
        }

        with open(self.project_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_translation(self, translation: Translation):
        """Add or update a translation"""
        # Remove existing translation with same key
        self.translations = [t for t in self.translations if t.key != translation.key]
        self.translations.append(translation)

    def get_statistics(self) -> Dict[str, int]:
        """Get project statistics"""
        categories = {}
        for trans in self.translations:
            categories[trans.category] = categories.get(trans.category, 0) + 1

        return {
            "total": len(self.translations),
            "categories": categories
        }


def print_validation_results(results: List[ValidationResult]):
    """Pretty print validation results"""
    if not results:
        print(f"{Colors.GREEN}✓ All validations passed!{Colors.END}")
        return

    errors = [r for r in results if r.level == ValidationLevel.ERROR]
    warnings = [r for r in results if r.level == ValidationLevel.WARNING]
    info = [r for r in results if r.level == ValidationLevel.INFO]

    if errors:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Errors ({len(errors)}):{Colors.END}")
        for result in errors:
            print(f"{Colors.RED}   {result.message}{Colors.END}")

    if warnings:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Warnings ({len(warnings)}):{Colors.END}")
        for result in warnings:
            print(f"{Colors.YELLOW}   {result.message}{Colors.END}")

    if info:
        print(f"\n{Colors.CYAN}ℹ️  Info ({len(info)}):{Colors.END}")
        for result in info:
            print(f"{Colors.CYAN}   {result.message}{Colors.END}")


def demo_usage():
    """Demonstrate the tool usage"""
    Colors.strip_if_no_tty()

    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("=" * 60)
    print("  Star Citizen Localization Tool - Proof of Concept")
    print("=" * 60)
    print(f"{Colors.END}\n")

    # Try to detect game
    game_path = GameDetector.find_game()
    if not game_path:
        game_path = Path("C:/Program Files/Roberts Space Industries/StarCitizen/LIVE")
        print(f"{Colors.YELLOW}Using default path: {game_path}{Colors.END}")

    print()

    # Create example project
    print(f"{Colors.BOLD}1. Creating translation project{Colors.END}")
    project = TranslationProject(Path("example_project.json"))
    project.metadata["name"] = "ASOP Terminal Improvements"
    project.metadata["author"] = "Demo User"
    project.metadata["description"] = "Makes ASOP terminals clearer"

    # Add some example translations
    project.add_translation(Translation(
        key="ui_asop_retrieval",
        original="Retrieve Ship",
        translated="Get Your Ship Back",
        category="asop",
        comment="Clearer action description"
    ))

    project.add_translation(Translation(
        key="ui_asop_stored",
        original="Ship in Hangar",
        translated="Chillin' in Storage",
        category="asop",
        comment="More casual tone"
    ))

    # Example with variable - should pass validation
    project.add_translation(Translation(
        key="ui_welcome_message",
        original="Welcome {player_name}!",
        translated="Greetings {player_name}!",
        category="ui"
    ))

    # Example that will fail validation (missing variable)
    project.add_translation(Translation(
        key="ui_error_message",
        original="Error: {error_code}",
        translated="Something went wrong!",  # Missing {error_code}
        category="ui"
    ))

    project.save()
    stats = project.get_statistics()
    print(f"{Colors.GREEN}✓ Project created with {stats['total']} translations{Colors.END}")
    print(f"   Categories: {', '.join(f'{k}({v})' for k, v in stats['categories'].items())}")
    print()

    # Validate translations
    print(f"{Colors.BOLD}2. Validating translations{Colors.END}")
    validator = TranslationValidator()
    all_results = []

    for trans in project.translations:
        results = validator.validate(trans, trans.original)
        all_results.extend(results)

    print_validation_results(all_results)
    print()

    # Show what merge would do (without actual game files)
    print(f"{Colors.BOLD}3. Merge preview{Colors.END}")
    print(f"{Colors.CYAN}Changes to be applied:{Colors.END}")
    print("─" * 60)

    for trans in project.translations:
        print(f"\n{Colors.BOLD}[{trans.category}] {trans.key}{Colors.END}")
        print(f"{Colors.RED}  - {trans.original}{Colors.END}")
        print(f"{Colors.GREEN}  + {trans.translated}{Colors.END}")
        if trans.comment:
            print(f"{Colors.CYAN}    # {trans.comment}{Colors.END}")

    print("\n" + "─" * 60)
    print()

    # Show backup management
    print(f"{Colors.BOLD}4. Backup management{Colors.END}")
    backup_mgr = BackupManager(Path("backups"))
    print(f"{Colors.GREEN}✓ Backup directory: {backup_mgr.backup_dir.absolute()}{Colors.END}")
    print(f"   Configured to keep last 5 backups")
    print()

    # Summary
    print(f"{Colors.BOLD}{Colors.GREEN}")
    print("=" * 60)
    print("  Demo Complete!")
    print("=" * 60)
    print(f"{Colors.END}")
    print(f"\nThis POC demonstrates:")
    print(f"  ✓ Game auto-detection")
    print(f"  ✓ Translation project management")
    print(f"  ✓ Comprehensive validation")
    print(f"  ✓ Backup management")
    print(f"  ✓ UTF-8 without BOM handling")
    print(f"  ✓ Clear error reporting")
    print(f"\nProject saved to: example_project.json")


if __name__ == "__main__":
    demo_usage()
