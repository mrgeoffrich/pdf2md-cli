---
name: release
description: Create a new versioned release of pdf2md. Bumps the version in __init__.py, commits, tags, and pushes to trigger the GitHub Actions release workflow that builds binaries for Linux, macOS, and Windows. Use when the user says "release", "cut a release", "new version", "publish", "bump version and release", or wants to create a GitHub release.
arguments:
  - name: version
    description: "The version to release (e.g. 0.2.0). If 'patch', 'minor', or 'major', auto-bumps accordingly."
    required: true
---

# Release Workflow

You are creating a new release of pdf2md. This will bump the version, commit, tag, and push to trigger the GitHub Actions release workflow that builds standalone binaries for all platforms.

## Steps

### 1. Validate preconditions

Before anything else, check that the release can proceed safely:

- Run `git status` to confirm the working tree is clean (no uncommitted changes). If dirty, stop and tell the user they need to commit or stash first.
- Run `git log origin/main..HEAD` to check for unpushed commits. If there are any, stop and ask the user if they want to push first.
- Run the test suite with `source .venv/bin/activate && pytest -v`. If tests fail, stop and report the failures.

### 2. Determine the new version

Read the current version from `pdf2md/__init__.py` (it's in the format `__version__ = "X.Y.Z"`).

The user provides a `$ARGUMENTS` value which is one of:
- An explicit semver like `0.2.0` — use it directly
- `patch` — bump Z (e.g. 0.1.0 -> 0.1.1)
- `minor` — bump Y, reset Z (e.g. 0.1.0 -> 0.2.0)
- `major` — bump X, reset Y and Z (e.g. 0.1.0 -> 1.0.0)

Confirm the version with the user before proceeding: "This will release v{new_version} (current: {old_version}). Proceed?"

### 3. Bump the version

Edit `pdf2md/__init__.py` to update `__version__` to the new version string.

### 4. Commit and tag

```bash
git add pdf2md/__init__.py
git commit -m "Bump version to {new_version}"
git tag v{new_version}
```

### 5. Push commit and tag

```bash
git push && git push origin v{new_version}
```

The tag push triggers the release workflow in `.github/workflows/release.yml`, which builds binaries for Linux x86_64, macOS arm64, and Windows x86_64, then creates a GitHub release with all three attached.

### 6. Report

Tell the user:
- The version that was released
- Link to the release: `https://github.com/mrgeoffrich/pdf2md-cli/releases/tag/v{new_version}`
- Link to the workflow run: `https://github.com/mrgeoffrich/pdf2md-cli/actions`
- Remind them that binaries will be available on the release page once the workflow completes (usually a few minutes)
