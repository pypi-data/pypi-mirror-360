import tomllib
import re
from pathlib import Path

# Load version from pyproject.toml
with open("pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)
    new_version = pyproject["project"]["version"]

# Load bumpversion config
bump_path = Path(".bumpversion.toml")
content = bump_path.read_text(encoding="utf-8")

# Replace current_version line
new_content = re.sub(
    r'current_version\s*=\s*".*?"',
    f'current_version = "{new_version}"',
    content
)

# Save the updated config
bump_path.write_text(new_content, encoding="utf-8")
print(f"✅ Updated .bumpversion.toml to current_version = {new_version}")
