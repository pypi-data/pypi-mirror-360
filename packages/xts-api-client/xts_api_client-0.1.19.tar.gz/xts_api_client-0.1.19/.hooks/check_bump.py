import sys
from pathlib import Path

pyproject = Path("pyproject.toml")
bumpfile = Path(".bumpversion.toml")

if not pyproject.exists() or not bumpfile.exists():
    print("Required files not found.")
    sys.exit(1)

old_version = ""
for line in bumpfile.read_text().splitlines():
    if line.strip().startswith("current_version"):
        old_version = line.split("=")[1].strip().strip('"')

if old_version and old_version in pyproject.read_text():
    print("❌ Version not bumped yet!")
    sys.exit(1)
else:
    print("✅ Version has been bumped.")
    sys.exit(0)
