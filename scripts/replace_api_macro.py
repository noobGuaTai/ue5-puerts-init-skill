#!/usr/bin/env python3
"""
Puerts Configuration Script

Automatically configures Puerts for your UE5 project:
1. Replaces API macro placeholder in MyGameInstance.h
2. Configures GameInstanceClass in DefaultEngine.ini
3. Copies minimal TypeScript type definitions to project

Usage:
    python scripts/replace_api_macro.py
"""

import os
import re
import sys
import shutil
from pathlib import Path


def find_project_root() -> tuple:
    """
    Find project root directory by searching for .uproject file.

    Returns:
        tuple: (project_root_path, project_name) or (None, None)
    """
    current = Path.cwd()

    for parent in [current, *current.parents]:
        uproject_files = list(parent.glob("*.uproject"))
        if uproject_files:
            return parent, uproject_files[0].stem

    return None, None


def get_api_macro_name(project_name: str) -> str:
    """
    Generate API macro name from project name.

    Args:
        project_name: Name of the project

    Returns:
        str: API macro name (e.g., "MYPROJECT_API")
    """
    return project_name.upper() + "_API"


def replace_in_file(filepath: Path, old_text: str, new_text: str) -> tuple:
    """
    Replace text in a file.

    Args:
        filepath: Path to the file
        old_text: Text to replace
        new_text: Replacement text

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if old_text not in content:
            return False, "Placeholder not found"

        new_content = content.replace(old_text, new_text)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True, "Replaced successfully"
    except Exception as e:
        return False, str(e)


def configure_gameinstance_class(project_root: Path, project_name: str) -> bool:
    """
    Configure GameInstanceClass in DefaultEngine.ini.

    Args:
        project_root: Project root directory
        project_name: Name of the project

    Returns:
        bool: True if successful, False otherwise
    """
    config_path = project_root / "Config" / "DefaultEngine.ini"

    if not config_path.exists():
        print(f"WARNING: Config file not found: {config_path}")
        return False

    backup_path = config_path.with_suffix('.ini.backup')
    try:
        shutil.copy2(config_path, backup_path)
        print(f"OK: Backed up config to {backup_path.name}")
    except Exception as e:
        print(f"ERROR: Backup failed - {e}")
        return False

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"ERROR: Failed to read config - {e}")
        return False

    pattern = rf'GameInstanceClass=/Script/{project_name}\.\w+'
    new_config = content
    modified = False

    match = re.search(pattern, new_config)
    if match:
        old_line = match.group(0)
        new_line = f'GameInstanceClass=/Script/{project_name}.MyGameInstance'
        new_config = new_config.replace(old_line, new_line)
        print(f"OK: Updated {old_line} -> {new_line}")
        modified = True
    else:
        if '[/Script/EngineSettings.GameMapsSettings]' in new_config:
            new_config = new_config.replace(
                '[/Script/EngineSettings.GameMapsSettings]',
                f'[/Script/EngineSettings.GameMapsSettings]\nGameInstanceClass=/Script/{project_name}.MyGameInstance'
            )
            print(f"OK: Added GameInstanceClass configuration")
            modified = True
        else:
            new_config += f"\n[/Script/EngineSettings.GameMapsSettings]\nGameInstanceClass=/Script/{project_name}.MyGameInstance\n"
            print(f"OK: Added GameInstanceClass configuration")
            modified = True

    if modified:
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(new_config)
            return True
        except Exception as e:
            print(f"ERROR: Failed to write config - {e}")
            shutil.copy2(backup_path, config_path)
            print("OK: Restored from backup")
            return False

    return False


def copy_type_definitions(project_root: Path) -> bool:
    """
    Copy minimal TypeScript type definitions from skill assets to project.

    Args:
        project_root: Project root directory

    Returns:
        bool: True if successful, False otherwise
    """
    script_dir = Path(__file__).parent.parent
    assets_typings = script_dir / "assets" / "typings"
    project_typing = project_root / "Typing"

    if not assets_typings.exists():
        print(f"WARNING: Type definitions not found: {assets_typings}")
        return False

    project_typing.mkdir(parents=True, exist_ok=True)

    copied = False
    for module in ["puerts", "ue"]:
        src = assets_typings / module
        dst = project_typing / module
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"OK: Copied {module}/ type definitions")
            copied = True
        else:
            print(f"WARNING: {module}/ type definitions not found")

    return copied


def copy_gameinstance_files(project_root: Path, project_name: str) -> bool:
    """
    Copy MyGameInstance template files to project source directory.

    Args:
        project_root: Project root directory
        project_name: Name of the project

    Returns:
        bool: True if successful, False otherwise
    """
    script_dir = Path(__file__).parent.parent
    assets_dir = script_dir / "assets"

    source_dir = project_root / "Source" / project_name
    public_dir = source_dir / "Public"
    private_dir = source_dir / "Private"

    # Create directories if they don't exist
    public_dir.mkdir(parents=True, exist_ok=True)
    private_dir.mkdir(parents=True, exist_ok=True)
    print(f"OK: Ensured directories exist: Public/ and Private/")

    # Copy header file
    header_src = assets_dir / "MyGameInstance.h"
    header_dst = public_dir / "MyGameInstance.h"
    if header_src.exists():
        shutil.copy2(header_src, header_dst)
        print(f"OK: Copied {header_src.name} to {public_dir.relative_to(project_root)}")
    else:
        print(f"WARNING: {header_src.name} not found in assets")
        return False

    # Copy source file
    cpp_src = assets_dir / "MyGameInstance.cpp"
    cpp_dst = private_dir / "MyGameInstance.cpp"
    if cpp_src.exists():
        shutil.copy2(cpp_src, cpp_dst)
        print(f"OK: Copied {cpp_src.name} to {private_dir.relative_to(project_root)}")
    else:
        print(f"WARNING: {cpp_src.name} not found in assets")
        return False

    return True


def main() -> int:
    """Main entry point."""
    print("="*60)
    print("Puerts Configuration Script")
    print("="*60)

    project_root, project_name = find_project_root()

    if not project_root:
        print("ERROR: .uproject file not found")
        print("Please run from your UE project root directory")
        return 1

    print(f"\nDetected project: {project_name}")
    print(f"Project root: {project_root}")

    api_macro = get_api_macro_name(project_name)
    print(f"API macro: {api_macro}")

    # Copy GameInstance files first (creates directories if needed)
    print("\nCopying GameInstance files...")
    if not copy_gameinstance_files(project_root, project_name):
        print("ERROR: Failed to copy GameInstance files")
        return 1

    header_path = project_root / "Source" / project_name / "Public" / "MyGameInstance.h"

    if not header_path.exists():
        print(f"ERROR: File not found: {header_path}")
        print("Please ensure MyGameInstance.h exists")
        return 1

    old_text = "YOURPROJECT_API"
    success, message = replace_in_file(header_path, old_text, api_macro)

    if success:
        print(f"OK: Replaced YOURPROJECT_API -> {api_macro} in {header_path.name}")

        print("\nConfiguring GameInstance class...")
        configure_gameinstance_class(project_root, project_name)

        print("\nCopying type definitions...")
        copy_type_definitions(project_root)

        print("\n" + "="*60)
        print("OK: Configuration Complete!")
        print("="*60)
        return 0
    else:
        print(f"ERROR: {message}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
