#!/usr/bin/env python3
"""
Script to check and create missing __init__.py files
Run from project root: python3 fix_init_files.py
"""

from pathlib import Path

# Project root
ROOT = Path.cwd()

# Directories that need __init__.py
directories = [
    "code",
    "code/algorithms",
    "code/gui",
    "code/heartofitall",
    "code/utilities"
]

print("=" * 60)
print("CHECKING AND CREATING __init__.py FILES")
print("=" * 60)
print(f"Project root: {ROOT}\n")

created = []
existing = []
missing_dirs = []

for dir_path in directories:
    full_path = ROOT / dir_path
    init_file = full_path / "__init__.py"

    # Check if directory exists
    if not full_path.exists():
        print(f"✗ Directory missing: {dir_path}")
        missing_dirs.append(dir_path)
        continue

    # Check if __init__.py exists
    if init_file.exists():
        print(f"✓ {dir_path}/__init__.py already exists")
        existing.append(dir_path)
    else:
        # Create __init__.py
        init_file.touch()
        print(f"✓ Created {dir_path}/__init__.py")
        created.append(dir_path)

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Existing __init__.py files: {len(existing)}")
print(f"Created __init__.py files: {len(created)}")
print(f"Missing directories: {len(missing_dirs)}")

if missing_dirs:
    print(f"\n⚠️  WARNING: These directories don't exist:")
    for d in missing_dirs:
        print(f"  - {d}")
    print("\nMake sure your project structure is correct!")

if created:
    print(f"\n✓ Created {len(created)} new __init__.py files")

print("\n" + "=" * 60)
print("Next step: Run the diagnostic test")
print("  python3 diagnostic_test_improved.py")
print("=" * 60)