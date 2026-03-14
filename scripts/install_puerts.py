#!/usr/bin/env python3
"""
Puerts Plugin and V8 Engine Installer

Automatically downloads and installs the Puerts plugin for Unreal Engine 5,
including the V8 JavaScript engine.

Usage:
    python scripts/install_puerts.py
"""

import os
import sys
import subprocess
import urllib.request
import tarfile
import tempfile
import shutil
from pathlib import Path
from urllib.error import URLError

# Configuration
PUERTS_REPO = "https://github.com/Tencent/puerts.git"
V8_VERSION = "9.4.146.24"
V8_RELEASE_TAG = f"V8_{V8_VERSION}_240430"
V8_DOWNLOAD_URL = f"https://github.com/puerts/backend-v8/releases/download/{V8_RELEASE_TAG}/v8_bin_{V8_VERSION}.tgz"


def print_step(num: int, message: str) -> None:
    """Print a step header with consistent formatting."""
    print(f"\n{'='*60}")
    print(f"Step {num}: {message}")
    print('='*60)


def run_command(cmd: list, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=check)
    if result.stdout:
        print(result.stdout)
    return result


def find_project_root() -> tuple:
    """
    Find the project root directory by searching for .uproject file.

    Returns:
        tuple: (project_root_path, project_name) or (None, None)
    """
    current = Path.cwd()

    for parent in [current, *current.parents]:
        uproject_files = list(parent.glob("*.uproject"))
        if uproject_files:
            return parent, uproject_files[0].stem

    return None, None


def clone_puerts() -> Path:
    """
    Clone Puerts repository to a temporary directory.

    Returns:
        Path: Temporary directory path, or None if failed
    """
    print_step(1, "Cloning Puerts Repository")

    temp_dir = Path(tempfile.gettempdir()) / "puerts_clone"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    try:
        run_command(["git", "clone", "--depth", "1", PUERTS_REPO, str(temp_dir)])
        print(f"OK: Puerts cloned to {temp_dir}")
        return temp_dir
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Clone failed - {e}")
        return None


def copy_puerts_plugin(puerts_src: Path, project_root: Path) -> bool:
    """
    Copy Puerts plugin from cloned repository to project.

    Args:
        puerts_src: Source directory containing Puerts
        project_root: Project root directory

    Returns:
        bool: True if successful, False otherwise
    """
    print_step(2, "Copying Puerts Plugin to Project")

    puerts_unreal = puerts_src / "unreal" / "Puerts"

    if not puerts_unreal.exists():
        print(f"ERROR: Puerts plugin directory not found: {puerts_unreal}")
        return False

    plugins_dir = project_root / "Plugins"
    plugins_dir.mkdir(exist_ok=True)

    puerts_dst = plugins_dir / "Puerts"

    if puerts_dst.exists():
        print(f"Removing existing plugin directory: {puerts_dst}")
        shutil.rmtree(puerts_dst)

    try:
        shutil.copytree(puerts_unreal, puerts_dst)
        print(f"OK: Puerts plugin copied to {puerts_dst}")
        return True
    except Exception as e:
        print(f"ERROR: Copy failed - {e}")
        return False


def check_v8_installed(v8_dir: Path) -> tuple:
    """
    Check if V8 is already installed (supports multiple directory structures).

    Args:
        v8_dir: V8 directory path

    Returns:
        tuple: (is_installed, (v8_h, v8_lib, v8_dll)) or (False, None)
    """
    v8_h = v8_dir / "Inc" / "v8.h"
    if not v8_h.exists():
        return False, None

    possible_lib_paths = [
        v8_dir / "Win64" / "v8.dll.lib",
        v8_dir / "Lib" / "Win64DLL" / "v8.dll.lib",
        v8_dir / "Lib" / "Win64" / "v8.dll.lib",
    ]

    possible_dll_paths = [
        v8_dir / "Win64" / "v8.dll",
        v8_dir / "Lib" / "Win64DLL" / "v8.dll",
        v8_dir / "Bin" / "Win64" / "v8.dll",
    ]

    v8_lib = None
    v8_dll = None

    for path in possible_lib_paths:
        if path.exists():
            v8_lib = path
            break

    for path in possible_dll_paths:
        if path.exists():
            v8_dll = path
            break

    if v8_lib and v8_dll:
        return True, (v8_h, v8_lib, v8_dll)

    return False, None


def download_v8(puerts_plugin_dir: Path) -> bool:
    """
    Download and extract V8 engine.

    Args:
        puerts_plugin_dir: Puerts plugin directory

    Returns:
        bool: True if successful, False otherwise
    """
    print_step(3, f"Downloading V8 Engine {V8_VERSION}")

    v8_dir = puerts_plugin_dir / "ThirdParty" / f"v8_{V8_VERSION}"
    v8_dir.mkdir(parents=True, exist_ok=True)

    installed, v8_files = check_v8_installed(v8_dir)
    if installed:
        v8_h, v8_lib, v8_dll = v8_files
        print("OK: V8 engine already installed and complete")
        print(f"  - {v8_h.relative_to(v8_dir.parent)}")
        print(f"  - {v8_lib.relative_to(v8_dir.parent)}")
        print(f"  - {v8_dll.relative_to(v8_dir.parent)}")
        return True

    tgz_path = v8_dir / f"v8_bin_{V8_VERSION}.tgz"

    try:
        print("Downloading V8 engine...")
        print(f"URL: {V8_DOWNLOAD_URL}")

        with urllib.request.urlopen(V8_DOWNLOAD_URL) as response:
            total_size = response.getheader('Content-Length')
            if total_size:
                total_size = int(total_size)
                downloaded = 0
                chunk_size = 8192
                with open(tgz_path, 'wb') as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgress: {percent:.1f}%", end='', flush=True)
                print()

        print(f"OK: Downloaded {tgz_path.name}")

        print("Extracting V8 engine...")
        with tarfile.open(tgz_path, 'r:gz') as tar:
            tar.extractall(v8_dir)

        print(f"OK: Extracted to {v8_dir}")

        # Fix nested directory structure
        nested_dir = v8_dir / f"v8_{V8_VERSION}"
        if nested_dir.exists() and nested_dir.is_dir():
            print("Detected nested directory, fixing...")
            for item in nested_dir.iterdir():
                dest = v8_dir / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                shutil.move(str(item), str(dest))
            shutil.rmtree(nested_dir)
            print("OK: Fixed nested directory")

        tgz_path.unlink()
        print("OK: Removed archive")

        installed, v8_files = check_v8_installed(v8_dir)
        if not installed:
            print(f"ERROR: Incomplete download - missing files")
            print(f"  Check directory: {v8_dir}")
            return False

        v8_h, v8_lib, v8_dll = v8_files
        print("OK: V8 engine verification passed")
        print(f"  - {v8_h.relative_to(v8_dir.parent)}")
        print(f"  - {v8_lib.relative_to(v8_dir.parent)}")
        print(f"  - {v8_dll.relative_to(v8_dir.parent)}")
        return True

    except URLError as e:
        print(f"ERROR: Download failed - {e}")
        print("\nManual download link:")
        print(V8_DOWNLOAD_URL)
        return False
    except Exception as e:
        print(f"ERROR: Extraction failed - {e}")
        return False


def cleanup_files() -> bool:
    """
    Clean up temporary files.

    Returns:
        bool: True if successful
    """
    print_step(4, "Cleaning Up")

    temp_dir = Path(tempfile.gettempdir()) / "puerts_clone"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        print(f"OK: Removed temporary files")

    return True


def main() -> int:
    """Main entry point."""
    print("="*60)
    print("Puerts Plugin Installer")
    print("="*60)

    project_root, project_name = find_project_root()

    if not project_root:
        print("ERROR: .uproject file not found")
        print("Please run this script from your UE project root directory")
        return 1

    print(f"\nDetected project: {project_name}")
    print(f"Project root: {project_root}")

    puerts_src = clone_puerts()
    if not puerts_src:
        return 1

    if not copy_puerts_plugin(puerts_src, project_root):
        return 1

    puerts_plugin_dir = project_root / "Plugins" / "Puerts"

    if not download_v8(puerts_plugin_dir):
        print("\n" + "="*60)
        print("WARNING: Installation Incomplete!")
        print("="*60)
        print("\nV8 engine download failed. This is a required component.")
        print("\nManual download:")
        print(f"  URL: {V8_DOWNLOAD_URL}")
        print(f"  Extract to: {puerts_plugin_dir / 'ThirdParty' / f'v8_{V8_VERSION}'}")
        print("\nOr re-run this script:")
        print("  python scripts/install_puerts.py")
        return 1

    cleanup_files()

    print("\n" + "="*60)
    print("OK: Installation Complete!")
    print("="*60)
    print(f"\nPuerts plugin: {puerts_plugin_dir}")
    print(f"V8 engine: {puerts_plugin_dir / 'ThirdParty' / f'v8_{V8_VERSION}'}")
    print("\nNext steps:")
    print("1. Open your project in UE Editor")
    print("2. Click 'Yes' if prompted to recompile")
    print("3. Continue with SKILL.md instructions")

    return 0


if __name__ == "__main__":
    sys.exit(main())
