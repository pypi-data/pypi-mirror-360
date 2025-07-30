#!/usr/bin/env python3
"""
Build script for HBAT standalone Linux executables.

This script creates standalone Linux executables using PyInstaller and AppImage.
Run this from the project root directory on Linux.
"""

import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path


def install_dependencies():
    """Install build dependencies."""
    print("Installing build dependencies...")
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "pyinstaller>=5.0.0",
                "setuptools-scm>=6.2.0",
            ],
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        print("Failed to install dependencies")
        return False


def clean_build():
    """Clean previous build artifacts."""
    print("Cleaning previous builds...")
    paths_to_clean = ["build", "dist", "__pycache__"]

    for path in paths_to_clean:
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"  Removed {path}")


def build_gui():
    """Build GUI executable for Linux."""
    print("Building Linux GUI executable...")

    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name",
        "HBAT-GUI",
        "--add-data",
        "example_pdb_files:example_pdb_files",
        "--add-data",
        "example_presets:example_presets",
        "--add-data",
        "hbat.png:.",
        "--add-data",
        "README.md:.",
        "--hidden-import",
        "tkinter",
        "--hidden-import",
        "matplotlib.backends.backend_tkagg",
        "--hidden-import",
        "networkx",
        "--exclude-module",
        "PyQt5",
        "--exclude-module",
        "PyQt6",
        "--clean",
        "--distpath",
        "dist/linux",
        "hbat_gui.py",
    ]

    # Add icon if available
    if os.path.exists("hbat.png"):
        cmd.extend(["--icon", "hbat.png"])

    try:
        subprocess.run(cmd, check=True)
        print("✓ Linux GUI executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Linux GUI build failed: {e}")
        return False


def build_cli():
    """Build CLI executable for Linux."""
    print("Building Linux CLI executable...")

    cmd = [
        "pyinstaller",
        "--onefile",
        "--console",
        "--name",
        "hbat",
        "--add-data",
        "example_pdb_files:example_pdb_files",
        "--add-data",
        "example_presets:example_presets",
        "--hidden-import",
        "matplotlib",
        "--hidden-import",
        "networkx",
        "--clean",
        "--distpath",
        "dist/linux",
        "hbat_cli.py",
    ]

    try:
        subprocess.run(cmd, check=True)
        print("✓ Linux CLI executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Linux CLI build failed: {e}")
        return False


def create_appimage():
    """Create AppImage for better Linux distribution."""
    print("\nCreating AppImage...")

    # Create AppDir structure
    appdir = Path("HBAT.AppDir")
    if appdir.exists():
        shutil.rmtree(appdir)

    appdir.mkdir()
    (appdir / "usr" / "bin").mkdir(parents=True)
    (appdir / "usr" / "share" / "applications").mkdir(parents=True)
    (appdir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps").mkdir(
        parents=True
    )

    # Copy executables
    if os.path.exists("dist/linux/HBAT-GUI"):
        shutil.copy2("dist/linux/HBAT-GUI", appdir / "usr" / "bin" / "HBAT-GUI")
        os.chmod(appdir / "usr" / "bin" / "HBAT-GUI", 0o755)

    if os.path.exists("dist/linux/hbat"):
        shutil.copy2("dist/linux/hbat", appdir / "usr" / "bin" / "hbat")
        os.chmod(appdir / "usr" / "bin" / "hbat", 0o755)

    # Copy icon
    if os.path.exists("hbat.png"):
        shutil.copy2(
            "hbat.png",
            appdir
            / "usr"
            / "share"
            / "icons"
            / "hicolor"
            / "256x256"
            / "apps"
            / "hbat.png",
        )

    # Create desktop file
    desktop_content = """[Desktop Entry]
Name=HBAT
Comment=Hydrogen Bond Analysis Tool
Exec=HBAT-GUI
Icon=hbat
Type=Application
Categories=Science;Chemistry;
Terminal=false
"""

    with open(appdir / "usr" / "share" / "applications" / "hbat.desktop", "w") as f:
        f.write(desktop_content)

    # Create AppRun script
    apprun_content = """#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"

if [ "$1" = "cli" ]; then
    shift
    exec "${HERE}/usr/bin/hbat" "$@"
else
    exec "${HERE}/usr/bin/HBAT-GUI" "$@"
fi
"""

    with open(appdir / "AppRun", "w") as f:
        f.write(apprun_content)
    os.chmod(appdir / "AppRun", 0o755)

    # Download appimagetool if not present
    appimagetool = "appimagetool-x86_64.AppImage"
    if not os.path.exists(appimagetool):
        print("Downloading appimagetool...")
        try:
            urllib.request.urlretrieve(
                "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage",
                appimagetool,
            )
            os.chmod(appimagetool, 0o755)
        except Exception as e:
            print(f"Failed to download appimagetool: {e}")
            return False

    # Build AppImage
    try:
        env = os.environ.copy()
        env["ARCH"] = "x86_64"
        subprocess.run(
            [f"./{appimagetool}", "HBAT.AppDir", "dist/HBAT-x86_64.AppImage"],
            check=True,
            env=env,
        )
        shutil.rmtree(appdir)
        print("✓ AppImage created successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to create AppImage")
        return False


def create_deb_package():
    """Create .deb package for Debian/Ubuntu."""
    print("\nCreating .deb package...")

    # Create debian package structure
    debdir = Path("hbat-deb")
    if debdir.exists():
        shutil.rmtree(debdir)

    # Create directory structure
    (debdir / "DEBIAN").mkdir(parents=True)
    (debdir / "usr" / "bin").mkdir(parents=True)
    (debdir / "usr" / "share" / "applications").mkdir(parents=True)
    (debdir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps").mkdir(
        parents=True
    )

    # Copy executables
    if os.path.exists("dist/linux/HBAT-GUI"):
        shutil.copy2("dist/linux/HBAT-GUI", debdir / "usr" / "bin" / "hbat-gui")
        os.chmod(debdir / "usr" / "bin" / "hbat-gui", 0o755)

    if os.path.exists("dist/linux/hbat"):
        shutil.copy2("dist/linux/hbat", debdir / "usr" / "bin" / "hbat")
        os.chmod(debdir / "usr" / "bin" / "hbat", 0o755)

    # Copy icon
    if os.path.exists("hbat.png"):
        shutil.copy2(
            "hbat.png",
            debdir
            / "usr"
            / "share"
            / "icons"
            / "hicolor"
            / "256x256"
            / "apps"
            / "hbat.png",
        )

    # Create desktop file
    desktop_content = """[Desktop Entry]
Name=HBAT
Comment=Hydrogen Bond Analysis Tool
Exec=hbat-gui
Icon=hbat
Type=Application
Categories=Science;Chemistry;
Terminal=false
"""

    with open(debdir / "usr" / "share" / "applications" / "hbat.desktop", "w") as f:
        f.write(desktop_content)

    # Create control file
    control_content = """Package: hbat
Version: 1.0.0
Section: science
Priority: optional
Architecture: amd64
Maintainer: HBAT Team
Description: Hydrogen Bond Analysis Tool
 A comprehensive tool for analyzing hydrogen bonds in molecular structures.
"""

    with open(debdir / "DEBIAN" / "control", "w") as f:
        f.write(control_content)

    # Build .deb package
    try:
        subprocess.run(
            ["dpkg-deb", "--build", "hbat-deb", "dist/hbat_1.0.0_amd64.deb"], check=True
        )
        shutil.rmtree(debdir)
        print("✓ .deb package created successfully")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Failed to create .deb package (dpkg-deb not found)")
        if debdir.exists():
            shutil.rmtree(debdir)
        return False


def main():
    """Main build function."""
    print("HBAT Linux Build Script")
    print("=" * 40)

    # Check we're in the right directory
    if not os.path.exists("hbat_gui.py"):
        print("Error: Please run this script from the HBAT project root directory")
        return 1

    # Check if running on Linux
    if sys.platform != "linux":
        print("Warning: This script is designed for Linux.")
        print("Cross-compilation may not work properly.")

    # Install dependencies
    if not install_dependencies():
        return 1

    # Clean previous builds
    clean_build()

    # Build executables
    gui_success = build_gui()
    cli_success = build_cli()

    if not (gui_success or cli_success):
        print("All builds failed!")
        return 1

    # Try to create packages
    appimage_success = create_appimage()
    deb_success = create_deb_package()

    print("\n" + "=" * 40)
    print("Build Summary")
    print("=" * 40)

    if gui_success:
        print("✓ GUI: dist/linux/HBAT-GUI")
    else:
        print("✗ GUI build failed")

    if cli_success:
        print("✓ CLI: dist/linux/hbat")
    else:
        print("✗ CLI build failed")

    if appimage_success:
        print("✓ AppImage: dist/HBAT-x86_64.AppImage")
    else:
        print("✗ AppImage creation skipped/failed")

    if deb_success:
        print("✓ DEB Package: dist/hbat_1.0.0_amd64.deb")
    else:
        print("✗ DEB package creation skipped/failed")

    print("\nUsage:")
    if gui_success:
        print("  GUI: ./dist/linux/HBAT-GUI")
    if cli_success:
        print("  CLI: ./dist/linux/hbat")
    if appimage_success:
        print("  AppImage: ./dist/HBAT-x86_64.AppImage")

    return 0


if __name__ == "__main__":
    sys.exit(main())
