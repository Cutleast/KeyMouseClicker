"""
This script builds the DICK.exe and packs
all its dependencies in one folder.
"""

import os
import shutil
from pathlib import Path

DIST_FOLDER = Path("main.dist").resolve()
APPNAME="KeyMouseClicker"
VERSION="1.0"
AUTHOR="Cutleast"
LICENSE="Attribution-NonCommercial-NoDerivatives 4.0 International"
UNUSED_FILES = [
    DIST_FOLDER / "qt6svg.dll",
    DIST_FOLDER / "qt6datavisualization.dll",
    DIST_FOLDER / "qt6network.dll",
    DIST_FOLDER / "qt6pdf.dll",
    DIST_FOLDER / "PySide6" / "QtNetwork.pyd",
    DIST_FOLDER / "PySide6" / "QtDataVisualization.pyd",
    DIST_FOLDER / "libcrypto-1_1.dll"
]

print("Compiling resources...")
os.system("pyside6-rcc.exe .\\src\\assets.qrc -o .\\src\\assets.py")

print("Building with nuitka...")
cmd = f'nuitka \
--msvc="latest" \
--standalone \
--enable-plugin=pyside6 \
--remove-output \
--disable-console \
--company-name="{AUTHOR}" \
--product-name="{APPNAME}" \
--file-version="{VERSION}" \
--product-version="{VERSION}" \
--file-description="{APPNAME}" \
--copyright="{LICENSE}" \
--nofollow-import-to=tkinter \
--windows-icon-from-ico="./src/assets/icon.ico" \
--output-filename="KeyMouseClicker.exe" \
"./src/main.py"'
os.system(cmd)

print("Deleting unused files...")
for file in UNUSED_FILES:
    if not file.is_file():
        continue
    os.remove(file)
    print(f"Removed '{file.name}'.")

print("Copying license...")
shutil.copyfile("LICENSE", DIST_FOLDER / "license.txt")

print("Done!")
