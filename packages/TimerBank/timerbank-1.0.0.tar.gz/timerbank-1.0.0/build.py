#!/usr/bin/env python3
"""Build script for SimpleTimerBank desktop application.

This script automates the process of building a standalone executable
using PyInstaller. It handles cleanup, building, and basic validation.
It supports two modes:
  --mode=dir  (default): Fast-starting directory-based build.
  --mode=file : Slow-starting single-file build for distribution.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List


def run_command(cmd: List[str], description: str) -> bool:
    """Run a command and return success status.
    
    Parameters
    ----------
    cmd : list[str]
        Command and arguments to execute.
    description : str
        Description of what the command does.
        
    Returns
    -------
    bool
        True if command succeeded, False otherwise.
    """
    print(f"🔨 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8')
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {' '.join(cmd)}")
        print(f"   Exit code: {e.returncode}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False


def clean_build_artifacts() -> None:
    """Remove previous build artifacts."""
    artifacts = ["build", "dist", "*.spec.bak"]
    
    print("🧹 Cleaning previous build artifacts...")
    for pattern in artifacts:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"   Removed directory: {path}")


def build_executable(mode: str) -> bool:
    """Build the standalone executable using PyInstaller.
    
    Parameters
    ----------
    mode : str
        Build mode, either 'dir' or 'file'.
        
    Returns
    -------
    bool
        True if build succeeded, False otherwise.
    """
    spec_file = "onedir.spec" if mode == 'dir' else "onefile.spec"
    
    if not Path(spec_file).exists():
        print(f"❌ {spec_file} not found. Run this script from the project root.")
        return False
    
    clean_build_artifacts()
    
    # The spec file now controls everything.
    cmd = ["uv", "run", "pyinstaller", spec_file]
    
    if mode == 'file':
        print("📦 Building in single-file mode (slower startup, for distribution)")
    else:
        print("📁 Building in one-folder mode (fast startup, for development)")
    
    success = run_command(cmd, f"Building executable with {spec_file}")
    
    if success:
        print("\n🎉 Build completed successfully!")
        if mode == 'file':
            exe_path = Path(f"dist/SimpleTimerBank.exe")
            print(f"   Executable: {exe_path}")
        else:
            exe_path = Path(f"dist/SimpleTimerBank/SimpleTimerBank.exe")
            print(f"   Executable located in: {exe_path.parent}")
        return True
    
    return False


def main() -> int:
    """Main build function.
    
    Returns
    -------
    int
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(description="SimpleTimerBank Build Script")
    parser.add_argument(
        '--mode', 
        type=str,
        choices=['dir', 'file'],
        default='dir',
        help="Build mode: 'dir' for a fast-starting folder, 'file' for a single executable."
    )
    args = parser.parse_args()
    
    print("🚀 SimpleTimerBank Build Script")
    print("=" * 40)
    
    if build_executable(args.mode):
        print("\n✅ Build process completed successfully!")
        return 0
    else:
        print("\n❌ Build process failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 