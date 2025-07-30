# Bump My Version Setup with Pre-Commit

## bump-my-version steps

### 1. Install `bump-my-version`
```bash
uv tool install bump-my-version

### 2. Create .bumpversion.toml file in the root directory

### 3. Run bump version with the following command
```bash
bump-my-version bump patch  # This command is for bumping the version for patch version. For minor or major version, simply remove the patch with major or minor.

## pre-commit hook steps

### 1. Install `pre-commit`
```bash
uv tool install pre-commit

### 2. Created .pre-commit-config.yaml file in the root directory

## version check script

### 1. Created a .hooks/check_bump.py file to check if the version bumping has occured or not.
### 2. Syncing of .bumpversion.toml with pyproject.toml. To do so, created a sync_bumpversion.py file to sync the changes.

## Step by step command for running the version bump and pre-commit and syncing

### 1. Bump the patch version
```bash
bump-my-version bump patch

### 2. Run pre-commit check
```bash
uv run pre-commit run --all-files

### 3. Sync .bumpversion.toml with updated version
```bash
uv run sync_bumpversion.py
