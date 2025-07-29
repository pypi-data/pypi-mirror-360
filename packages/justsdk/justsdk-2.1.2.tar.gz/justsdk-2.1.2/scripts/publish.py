#!/usr/bin/env python3
"""
Handles version bumping and publishing to PyPI
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Literal

VersionType = Literal["patch", "minor", "major"]

ROOT_DIR = Path(__file__).parent.parent
INIT_FILE = ROOT_DIR / "src" / "justsdk" / "__init__.py"
PYPROJECT_FILE = ROOT_DIR / "pyproject.toml"
LOCK_FILE = ROOT_DIR / "uv.lock"


def get_current_version() -> str:
    content = INIT_FILE.read_text()
    match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError("Could not find version in __init__.py")
    return match.group(1)


def parse_version(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")
    return tuple(int(part) for part in parts)


def bump_version(current: str, bump_type: VersionType) -> str:
    major, minor, patch = parse_version(current)

    if bump_type == "patch":
        patch += 1
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "major":
        major += 1
        minor = 0
        patch = 0

    return f"{major}.{minor}.{patch}"


def update_version_in_file(file_path: Path, old_version: str, new_version: str) -> None:
    content = file_path.read_text()

    if file_path == INIT_FILE:
        pattern = r'(__version__ = ["\'])([^"\']+)(["\'])'
        replacement = rf"\g<1>{new_version}\g<3>"
    elif file_path == PYPROJECT_FILE:
        pattern = r'(version = ["\'])([^"\']+)(["\'])'
        replacement = rf"\g<1>{new_version}\g<3>"
    else:
        raise ValueError(f"Unknown file type: {file_path}")

    updated_content = re.sub(pattern, replacement, content)

    if updated_content == content:
        print(f"⚠️ Warning: No version found to update in {file_path}")
        return

    file_path.write_text(updated_content)
    print(f"✅ Updated {file_path.name}: {old_version} -> {new_version}")


def run_command(
    cmd: list[str], check: bool = True, env: dict = None
) -> subprocess.CompletedProcess:
    print(f"🔧 Running: {' '.join(cmd)}")
    import os

    final_env = os.environ.copy()
    if env:
        final_env.update(env)

    result = subprocess.run(
        cmd, capture_output=True, text=True, check=False, env=final_env
    )

    if result.returncode != 0 and check:
        print(f"❌ Command failed: {' '.join(cmd)}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)

    return result


def update_lock_file(dry_run: bool = False) -> None:
    if dry_run:
        print("🏃 [DRY RUN] Would update uv.lock file")
        return

    print("🔒 Updating uv.lock file...")
    run_command(["uv", "lock", "--upgrade-package", "justsdk"])

    if LOCK_FILE.exists():
        print("✅ Lock file updated successfully")
    else:
        print("⚠️ Warning: Lock file not found after update")


def git_operations(
    version: str,
    dry_run: bool = False,
    force: bool = False,
    skip_clean_check: bool = False,
) -> None:
    if dry_run:
        print(f"🏃 [DRY RUN] Would create git tag: v{version}")
        return

    run_command(["uv", "run", "ruff", "format"])

    if not force and not skip_clean_check:
        result = run_command(["git", "status", "--porcelain"])
        if result.stdout.strip():
            print("❌ Git repository has uncommitted changes")
            print("Please commit or stash changes before publishing")
            print("Or use --force to commit changes automatically")
            sys.exit(1)
    elif force and not skip_clean_check:
        result = run_command(["git", "status", "--porcelain"])
        uncommitted_files = [
            line[3:] for line in result.stdout.strip().split("\n") if line.strip()
        ]
        other_files = [
            f
            for f in uncommitted_files
            if not any(
                f.endswith(p.name) for p in [INIT_FILE, PYPROJECT_FILE, LOCK_FILE]
            )
        ]

        if other_files:
            print("📝 Auto-committing pending changes...")
            for file in other_files:
                run_command(["git", "add", file])
            run_command(["git", "commit", "-m", "chore: prepare for version bump"])

    run_command(["git", "add", str(INIT_FILE)])

    if PYPROJECT_FILE.exists():
        run_command(["git", "add", str(PYPROJECT_FILE)])

    if LOCK_FILE.exists():
        run_command(["git", "add", str(LOCK_FILE)])
        print("✅ Staged uv.lock file")

    run_command(["git", "commit", "-m", f"bump: version {version}"])
    run_command(["git", "tag", f"v{version}"])
    run_command(["git", "push"])
    run_command(["git", "push", "--tags"])

    print(f"✅ Created git tag: v{version}")


def build_and_publish(dry_run: bool = False, test_pypi: bool = False) -> None:
    if dry_run:
        print("🏃 [DRY RUN] Would build and publish package")
        return

    dist_dir = ROOT_DIR / "dist"
    if dist_dir.exists():
        run_command(["rm", "-rf", str(dist_dir)])

    run_command(["uv", "build"])

    publish_cmd = ["uv", "publish"]

    if test_pypi:
        publish_cmd.extend(["--publish-url", "https://test.pypi.org/legacy/"])
        print("📦 Publishing to TestPyPI...")
    else:
        print("📦 Publishing to PyPI...")

    import os

    publish_env = {}

    username = os.getenv("TWINE_USERNAME")
    password = os.getenv("TWINE_PASSWORD")

    if username and password:
        publish_cmd.extend(["--username", username, "--password", password])
        print("🔑 Using provided credentials")
        publish_env = {"TWINE_USERNAME": username, "TWINE_PASSWORD": password}
    else:
        print("🔓 No credentials provided, attempting trusted publishing")

    run_command(publish_cmd, env=publish_env)

    if test_pypi:
        print("✅ Published to TestPyPI")
        print(
            "🧪 Test installation: pip install --index-url https://test.pypi.org/simple/ justsdk"
        )
    else:
        print("✅ Published to PyPI")
        print("🎉 Installation: pip install justsdk")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Publish justsdk to PyPI")
    parser.add_argument(
        "bump_type", choices=["patch", "minor", "major"], help="Type of version bump"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--test-pypi", action="store_true", help="Publish to TestPyPI instead of PyPI"
    )
    parser.add_argument(
        "--no-git", action="store_true", help="Skip git operations (tag and push)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Auto-commit any pending changes before version bump",
    )
    parser.add_argument(
        "--skip-clean-check",
        action="store_true",
        help="Skip git clean check (useful for CI environments)",
    )

    args = parser.parse_args()

    print(f"🚀 Publishing justsdk ({args.bump_type} version bump)")

    current_version = get_current_version()
    new_version = bump_version(current_version, args.bump_type)

    print(f"📝 Version: {current_version} -> {new_version}")

    if args.dry_run:
        print("🏃 [DRY RUN] No changes will be made")

    if not args.dry_run:
        update_version_in_file(INIT_FILE, current_version, new_version)
        update_version_in_file(PYPROJECT_FILE, current_version, new_version)
        update_lock_file(args.dry_run)

    if not args.no_git:
        git_operations(new_version, args.dry_run, args.force, args.skip_clean_check)

    build_and_publish(args.dry_run, args.test_pypi)

    if not args.dry_run:
        print(f"🎉 Successfully published justsdk v{new_version}!")


if __name__ == "__main__":
    main()
