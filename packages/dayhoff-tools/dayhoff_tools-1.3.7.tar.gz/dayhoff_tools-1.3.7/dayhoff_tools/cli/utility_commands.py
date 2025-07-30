"""CLI commands common to all repos."""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import toml
import typer
import yaml

# Import cloud helper lazily inside functions to avoid heavy deps at module load


def _warn_if_gcp_default_sa(force_prompt: bool = False) -> None:
    """Warn the user when the active gcloud principal is the default VM service
    account.  See detailed docstring later in file (duplicate for early
    availability)."""

    from dayhoff_tools.cli import cloud_commands as _cc

    try:
        impersonation = _cc._get_current_gcp_impersonation()
        user = _cc._get_current_gcp_user()
        active = impersonation if impersonation != "None" else user
        short = _cc._get_short_name(active)

        # Determine if user creds are valid
        auth_valid = _cc._is_gcp_user_authenticated()
    except Exception:
        # If any helper errors out, don't block execution
        return

    problem_type = None  # "default_sa" | "stale"
    if short == "default VM service account":
        problem_type = "default_sa"
    elif not auth_valid:
        problem_type = "stale"

    if problem_type is None:
        return  # Everything looks good

    YELLOW = getattr(_cc, "YELLOW", "\033[0;33m")
    BLUE = getattr(_cc, "BLUE", "\033[0;36m")
    RED = getattr(_cc, "RED", "\033[0;31m")
    NC = getattr(_cc, "NC", "\033[0m")

    if problem_type == "default_sa":
        msg_body = (
            f"You are currently authenticated as the *default VM service account*.\n"
            f"   This will block gsutil/DVC access to private buckets (e.g. warehouse)."
        )
    else:  # stale creds
        msg_body = (
            f"Your GCP credentials appear to be *expired/stale*.\n"
            f"   Re-authenticate to refresh the access token."
        )

    print(
        f"{YELLOW}⚠  {msg_body}{NC}\n"
        f"{YELLOW}   Run {BLUE}dh gcp login{YELLOW} or {BLUE}dh gcp use-devcon{YELLOW} before retrying.{NC}",
        file=sys.stderr,
    )

    if force_prompt and sys.stdin.isatty() and sys.stdout.isatty():
        import questionary

        if not questionary.confirm("Proceed anyway?", default=False).ask():
            print(f"{RED}Aborted due to unsafe GCP credentials.{NC}", file=sys.stderr)
            raise SystemExit(1)


def test_github_actions_locally():
    """Run the script test_pytest_in_github_actions_container.sh.sh."""
    script_path = ".devcontainer/scripts/test_pytest_in_github_actions_container.sh"

    try:
        subprocess.check_call(["bash", script_path])
        print("Script ran successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running the script: {e}")


def get_ancestry(filepath: str) -> None:
    """Take a .dvc file created from import, and generate an ancestry entry
    that can be manually copied into other .dvc files."""
    with open(filepath, "r") as file:
        assert filepath.endswith(".dvc"), "ERROR: Not a .dvc file"
        ancestor_content = yaml.safe_load(file)

        error_msg = "Unexpected file structure. Are you sure this is a .dvc file generated from `dvc import`?"
        assert "deps" in ancestor_content, error_msg

        error_msg = "Please only reference data imported from main branches."
        assert "rev" not in ancestor_content["deps"][0]["repo"], error_msg

        ancestor_info = {
            "name": os.path.basename(ancestor_content["outs"][0]["path"]),
            "file_md5_hash": ancestor_content["outs"][0]["md5"],
            "size": ancestor_content["outs"][0]["size"],
            "repo_url": ancestor_content["deps"][0]["repo"]["url"],
            "repo_path": ancestor_content["deps"][0]["path"],
            "commit_hash": ancestor_content["deps"][0]["repo"]["rev_lock"],
        }
        print()
        yaml.safe_dump(
            [ancestor_info], sys.stdout, default_flow_style=False, sort_keys=False
        )


def import_from_warehouse_typer() -> None:
    """Import a file from warehouse.

    Emits an early warning if the active GCP credentials are the *default VM
    service account* because this will prevent DVC/gsutil from accessing the
    warehouse bucket.  The user can abort the command when running
    interactively.
    """

    # Early-exit guard for wrong GCP credentials
    _warn_if_gcp_default_sa(force_prompt=True)

    # Import only when the function is called
    import questionary
    from dayhoff_tools.warehouse import import_from_warehouse

    # Check if we're in Lightning Studio
    if _is_lightning_studio():
        # Lightning Studio behavior
        _check_dvc_initialized()
        _configure_studio_cache()

        # Ensure we're running from repo root using REPO_ROOT env var
        repo_root = os.environ.get("REPO_ROOT")
        if not repo_root:
            raise Exception(
                "REPO_ROOT environment variable not set. Make sure you're in a repo with an active UV virtual environment."
            )

        current_dir = os.getcwd()
        if current_dir != repo_root:
            raise Exception(
                f"This command must be run from the repo root. "
                f"Current directory: {current_dir}, Expected: {repo_root}"
            )
    else:
        # Original devcontainer behavior - ensure execution from root
        cwd = Path(os.getcwd())
        if cwd.parent.name != "workspaces" or str(cwd.parent.parent) != cwd.root:
            raise Exception(
                f"This command must be executed from the repo's root directory (/workspaces/reponame). Current directory: {cwd}"
            )

    # Use questionary for prompts instead of typer
    warehouse_path = questionary.text("Warehouse path:").ask()

    # Provide multiple-choice options for output folder
    output_folder_choice = questionary.select(
        "Output folder:",
        choices=["data/imports", "same_as_warehouse", "Custom path..."],
    ).ask()

    # If custom path is selected, ask for the path
    if output_folder_choice == "Custom path...":
        output_folder = questionary.text("Enter custom output folder:").ask()
    else:
        output_folder = output_folder_choice

    branch = questionary.text("Branch (default: main):", default="main").ask()

    final_path = import_from_warehouse(
        warehouse_path=warehouse_path,
        output_folder=output_folder,
        branch=branch,
    )


def add_to_warehouse_typer() -> None:
    """Add a new data file to warehouse and enrich its generated .dvc file.

    As with *dh wimport*, this command fails when the user is logged in with
    the default VM service account.  A guard therefore warns the user first
    and allows them to abort interactively.
    """

    # Early-exit guard for wrong GCP credentials
    _warn_if_gcp_default_sa(force_prompt=True)

    # Import only when the function is called
    import questionary
    from dayhoff_tools.warehouse import add_to_warehouse

    # Check if we're in Lightning Studio
    if _is_lightning_studio():
        # Lightning Studio behavior
        _check_dvc_initialized()
        _configure_studio_cache()

        # Ensure we're running from repo root using REPO_ROOT env var
        repo_root = os.environ.get("REPO_ROOT")
        if not repo_root:
            raise Exception(
                "REPO_ROOT environment variable not set. Make sure you're in a repo with an active UV virtual environment."
            )

        current_dir = os.getcwd()
        if current_dir != repo_root:
            raise Exception(
                f"This command must be run from the repo root. "
                f"Current directory: {current_dir}, Expected: {repo_root}"
            )
    else:
        # Original devcontainer behavior - ensure execution from root
        cwd = Path(os.getcwd())
        if cwd.parent.name != "workspaces" or str(cwd.parent.parent) != cwd.root:
            raise Exception(
                f"This command must be executed from the repo's root directory (/workspaces/reponame). Current directory: {cwd}"
            )

    # Prompt for the data file path
    warehouse_path = questionary.text("Data file to be registered:").ask()

    # Prompt for the ancestor .dvc file paths
    ancestor_dvc_paths = []
    print("\nEnter the path of all ancestor .dvc files (or hit Enter to finish).")
    print("These files must be generated by `dvc import` or `dh wimport`.")
    while True:
        ancestor_path = questionary.text("Ancestor path: ").ask()
        if ancestor_path:
            ancestor_dvc_paths.append(ancestor_path)
        else:
            print()
            break

    dvc_path = add_to_warehouse(
        warehouse_path=warehouse_path,
        ancestor_dvc_paths=ancestor_dvc_paths,
    )


def delete_local_branch(branch_name: str, folder_path: str):
    """Delete a local Git branch after fetching with pruning.

    Args:
        branch_name: Name of the branch to delete
        folder_path: Path to the git repository folder
    """
    try:
        # Store current working directory
        original_dir = os.getcwd()

        # Change to the specified directory
        os.chdir(folder_path)
        print(f"Changed to directory: {folder_path}")

        # Delete the specified branch
        delete_branch_cmd = ["git", "branch", "-D", branch_name]
        subprocess.run(delete_branch_cmd, check=True)
        print(f"Deleted branch: {branch_name}")

        # Fetch changes from the remote repository and prune obsolete branches
        fetch_prune_cmd = ["git", "fetch", "-p"]
        subprocess.run(fetch_prune_cmd, check=True)
        print("Fetched changes and pruned obsolete branches")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running Git commands: {e}")
    finally:
        # Always return to the original directory
        os.chdir(original_dir)


def get_current_version_from_toml(file_path="pyproject.toml"):
    """Reads the version from a pyproject.toml file."""
    try:
        with open(file_path, "r") as f:
            content = f.read()
        version_match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
        if version_match:
            return version_match.group(1)
        else:
            raise ValueError(f"Could not find version string in {file_path}")
    except FileNotFoundError:
        raise FileNotFoundError(f"{file_path} not found.")
    except Exception as e:
        raise e


def build_and_upload_wheel(bump_part: str = "patch"):
    """Build a Python wheel and upload to PyPI using UV.

    Automatically increments the version number in pyproject.toml before building
    based on the bump_part argument ('major', 'minor', 'patch').

    Expects PyPI authentication to be configured via the environment variable:
    - UV_PUBLISH_TOKEN

    Args:
        bump_part (str): The part of the version to bump. Defaults to 'patch'.
    """
    if bump_part not in ["major", "minor", "patch"]:
        print(
            f"Error: Invalid bump_part '{bump_part}'. Must be 'major', 'minor', or 'patch'."
        )
        return

    # ANSI color codes
    BLUE = "\033[94m"
    RESET = "\033[0m"

    # --- Authentication Setup ---
    token = os.environ.get("UV_PUBLISH_TOKEN")

    if not token:
        print("Error: PyPI authentication not configured.")
        print(
            "Please set the UV_PUBLISH_TOKEN environment variable with your PyPI API token."
        )
        return

    # Build the command with token authentication
    # IMPORTANT: Mask token for printing
    publish_cmd_safe_print = ["uv", "publish", "--token", "*****"]
    publish_cmd = ["uv", "publish", "--token", token]
    print("Using UV_PUBLISH_TOKEN for authentication.")

    pyproject_path = "pyproject.toml"
    current_version = None  # Initialize in case the first try block fails

    try:
        # --- Clean dist directory ---
        dist_dir = Path("dist")
        if dist_dir.exists():
            print(f"Removing existing build directory: {dist_dir}")
            shutil.rmtree(dist_dir)
        # --- End Clean dist directory ---

        # --- Version Bumping Logic ---
        current_version = get_current_version_from_toml(pyproject_path)
        print(f"Current version: {current_version}")

        try:
            major, minor, patch = map(int, current_version.split("."))
        except ValueError:
            print(
                f"Error: Could not parse version '{current_version}'. Expected format X.Y.Z"
            )
            return

        if bump_part == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_part == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1

        new_version = f"{major}.{minor}.{patch}"
        print(f"Bumping {bump_part} version to: {new_version}")

        # Read pyproject.toml
        with open(pyproject_path, "r") as f:
            content = f.read()

        # Replace the version string
        pattern = re.compile(
            f'^version\s*=\s*"{re.escape(current_version)}"', re.MULTILINE
        )
        new_content, num_replacements = pattern.subn(
            f'version = "{new_version}"', content
        )

        if num_replacements == 0:
            print(
                f"Error: Could not find 'version = \"{current_version}\"' in {pyproject_path}"
            )
            return  # Exit before build/publish if version wasn't updated
        if num_replacements > 1:
            print(
                f"Warning: Found multiple version lines for '{current_version}'. Only the first was updated."
            )

        # Write the updated content back
        with open(pyproject_path, "w") as f:
            f.write(new_content)
        print(f"Updated {pyproject_path} with version {new_version}")
        # --- End Version Bumping Logic ---

        # Build wheel and sdist
        build_cmd = ["uv", "build"]
        # Print command in blue
        print(f"Running command: {BLUE}{' '.join(build_cmd)}{RESET}")
        subprocess.run(build_cmd, check=True)

        # Upload using uv publish with explicit arguments
        # Print masked command in blue
        print(f"Running command: {BLUE}{' '.join(publish_cmd_safe_print)}{RESET}")
        subprocess.run(
            publish_cmd,  # Use the actual command with token
            check=True,
        )

        print(f"Successfully built and uploaded version {new_version} to PyPI")

    except FileNotFoundError:
        print(f"Error: {pyproject_path} not found.")
        # No version change happened, so no rollback needed
    except subprocess.CalledProcessError as e:
        print(f"Error during build/upload: {e}")
        # Attempt to roll back version change only if it was bumped successfully
        if current_version and new_version:
            try:
                print(
                    f"Attempting to revert version in {pyproject_path} back to {current_version}..."
                )
                with open(pyproject_path, "r") as f:
                    content_revert = f.read()
                # Use new_version in pattern for reverting
                pattern_revert = re.compile(
                    f'^version\s*=\s*"{re.escape(new_version)}"', re.MULTILINE
                )
                reverted_content, num_revert = pattern_revert.subn(
                    f'version = "{current_version}"', content_revert
                )
                if num_revert > 0:
                    with open(pyproject_path, "w") as f:
                        f.write(reverted_content)
                    print(f"Successfully reverted version in {pyproject_path}.")
                else:
                    print(
                        f"Warning: Could not find version {new_version} to revert in {pyproject_path}."
                    )
            except Exception as revert_e:
                print(
                    f"Warning: Failed to revert version change in {pyproject_path}: {revert_e}"
                )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Also attempt rollback here if version was bumped
        if current_version and "new_version" in locals() and new_version:
            try:
                print(
                    f"Attempting to revert version in {pyproject_path} back to {current_version} due to unexpected error..."
                )
                # (Same revert logic as above)
                with open(pyproject_path, "r") as f:
                    content_revert = f.read()
                pattern_revert = re.compile(
                    f'^version\s*=\s*"{re.escape(new_version)}"', re.MULTILINE
                )
                reverted_content, num_revert = pattern_revert.subn(
                    f'version = "{current_version}"', content_revert
                )
                if num_revert > 0:
                    with open(pyproject_path, "w") as f:
                        f.write(reverted_content)
                    print(f"Successfully reverted version in {pyproject_path}.")
                else:
                    print(
                        f"Warning: Could not find version {new_version} to revert in {pyproject_path}."
                    )
            except Exception as revert_e:
                print(
                    f"Warning: Failed to revert version change in {pyproject_path}: {revert_e}"
                )


# --- Dependency Management Commands ---


def install_dependencies(
    install_project: bool = typer.Option(
        False,
        "--install-project",
        "-p",
        help="Install the local project package itself (with 'full' extras) into the environment.",
    ),
):
    """Install dependencies based on pyproject.toml.

    Ensures uv.lock matches pyproject.toml and syncs the environment.
    When -p is used, installs the local project with its [full] optional dependencies.
    """
    # ANSI color codes
    BLUE = "\033[94m"
    RESET = "\033[0m"

    try:
        # Step 1: Ensure lock file matches pyproject.toml
        print("Ensuring lock file matches pyproject.toml...")
        lock_cmd = ["uv", "lock"]
        print(f"Running command: {BLUE}{' '.join(lock_cmd)}{RESET}")
        subprocess.run(lock_cmd, check=True, capture_output=True)

        if install_project:
            # Step 2a: Install the project with 'full' extras
            print("Installing the local project with 'full' extras...")
            # The .[full] syntax tells pip to install the current project ('.')
            # with its 'full' optional dependencies.
            pip_install_cmd = ["uv", "pip", "install", "-e", ".[full]"]
            print(f"Running command: {BLUE}{' '.join(pip_install_cmd)}{RESET}")
            subprocess.run(pip_install_cmd, check=True)

            print("Project installed with 'full' extras successfully.")
        else:
            # Original behavior: Sync environment without installing the project
            print(
                "Syncing environment with lock file (project itself will not be installed)..."
            )
            # --all-groups ensures all non-project dependencies (like dev) are installed
            sync_cmd = ["uv", "sync", "--all-groups", "--no-install-project"]
            print(f"Running command: {BLUE}{' '.join(sync_cmd)}{RESET}")
            subprocess.run(sync_cmd, check=True)
            print("Dependencies synced successfully (project not installed).")

    except subprocess.CalledProcessError as e:
        stderr_output = e.stderr.decode() if e.stderr else "No stderr output."
        print(f"Error occurred during dependency installation/sync: {e}")
        print(f"Stderr: {stderr_output}")
        if "NoSolution" in stderr_output:
            print(
                "\nHint: Could not find a compatible set of dependencies. Check constraints in pyproject.toml."
            )
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'uv' command not found. Is uv installed and in PATH?")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


def update_dependencies(
    update_all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Update all dependencies instead of just dayhoff-tools.",
    ),
):
    """Update dependencies to newer versions.

    Default Action (no flags): Updates only 'dayhoff-tools' package to latest,
                               updates pyproject.toml, and syncs.

    Flags:
    --all/-a: Updates all dependencies to latest compatible versions (`uv lock --upgrade`)
              and syncs the environment. Overrides the default.
    """
    # ANSI color codes
    BLUE = "\033[94m"
    RESET = "\033[0m"

    lock_file_path = Path("uv.lock")
    pyproject_path = Path("pyproject.toml")

    # Determine action based on flags
    lock_cmd = ["uv", "lock"]
    action_description = ""
    run_pyproject_update = False

    if update_all:
        lock_cmd.append("--upgrade")
        action_description = (
            "Updating lock file for all dependencies to latest versions..."
        )
    else:  # Default behavior: update dayhoff-tools
        lock_cmd.extend(["--upgrade-package", "dayhoff-tools"])
        action_description = (
            "Updating dayhoff-tools lock and pyproject.toml (default behavior)..."
        )
        run_pyproject_update = (
            True  # Only update pyproject if we are doing the dayhoff update
        )

    try:
        # Step 1: Run the update lock command
        print(action_description)
        print(f"Running command: {BLUE}{' '.join(lock_cmd)}{RESET}")
        subprocess.run(lock_cmd, check=True, capture_output=True)

        # Step 2: Update pyproject.toml only if doing the dayhoff update (default)
        if run_pyproject_update:
            print(f"Reading {lock_file_path} to find new dayhoff-tools version...")
            if not lock_file_path.exists():
                print(f"Error: {lock_file_path} not found after lock command.")
                return
            locked_version = None
            try:
                lock_data = toml.load(lock_file_path)
                for package in lock_data.get("package", []):
                    if package.get("name") == "dayhoff-tools":
                        locked_version = package.get("version")
                        break
            except toml.TomlDecodeError as e:
                print(f"Error parsing {lock_file_path}: {e}")
                return
            except Exception as e:
                print(f"Error reading lock file: {e}")
                return

            if not locked_version:
                print(
                    f"Error: Could not find dayhoff-tools version in {lock_file_path}."
                )
                return

            print(f"Found dayhoff-tools version {locked_version} in lock file.")
            print(f"Updating {pyproject_path} version constraint...")
            try:
                content = pyproject_path.read_text()

                package_name = "dayhoff-tools"
                package_name_esc = re.escape(package_name)

                # Regex to match the dependency line, with optional extras and version spec
                pattern = re.compile(
                    rf"^(\s*['\"]){package_name_esc}(\[[^]]+\])?(?:[><=~^][^'\"]*)?(['\"].*)$",
                    re.MULTILINE,
                )

                new_constraint_text = f">={locked_version}"

                def _repl(match: re.Match):
                    prefix = match.group(1)
                    extras = match.group(2) or ""
                    suffix = match.group(3)
                    return (
                        f"{prefix}{package_name}{extras}{new_constraint_text}{suffix}"
                    )

                new_content, num_replacements = pattern.subn(_repl, content)
                if num_replacements > 0:
                    pyproject_path.write_text(new_content)
                    print(
                        f"Updated dayhoff-tools constraint in {pyproject_path} to '{new_constraint_text}'"
                    )
                else:
                    print(
                        f"Warning: Could not find dayhoff-tools dependency line in {pyproject_path} to update constraint."
                    )
            except FileNotFoundError:
                print(f"Error: {pyproject_path} not found.")
                return
            except Exception as e:
                print(f"Error updating {pyproject_path}: {e}")
                print("Proceeding with sync despite pyproject.toml update error.")

        # Step 3: Sync environment
        print("Syncing environment with updated lock file...")
        # Always use --no-install-project for updates
        sync_cmd = ["uv", "sync", "--all-groups", "--no-install-project"]
        print(f"Running command: {BLUE}{' '.join(sync_cmd)}{RESET}")
        subprocess.run(sync_cmd, check=True)

        # Final status message
        if update_all:
            print("All dependencies updated and environment synced successfully.")
        else:  # Default case (dayhoff update)
            print(
                "dayhoff-tools updated, pyproject.toml modified, and environment synced successfully."
            )

    except subprocess.CalledProcessError as e:
        stderr_output = e.stderr.decode() if e.stderr else "No stderr output."
        print(f"Error occurred during dependency update/sync: {e}")
        print(f"Stderr: {stderr_output}")
        if "NoSolution" in stderr_output:
            print(
                "\nHint: Could not find a compatible set of dependencies. Check constraints in pyproject.toml."
            )
        elif "unrecognized arguments: --upgrade" in stderr_output:
            print(
                "\nHint: Your version of 'uv' might be too old to support '--upgrade'. Try updating uv."
            )
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'uv' command not found. Is uv installed and in PATH?")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


# ----------------------
# Lightning Studio Commands
# ----------------------


def _is_lightning_studio() -> bool:
    """Check if we're running in Lightning Studio environment."""
    return os.path.exists("/teamspace/studios/this_studio")


def _check_dvc_initialized() -> None:
    """Check if DVC is initialized in the current directory."""
    if not os.path.exists(".dvc"):
        raise Exception(
            "DVC is not initialized in this repository. Run 'dvc init' first."
        )


def _configure_studio_cache() -> None:
    """Configure DVC to use studio-level cache if not already configured."""
    studio_cache_dir = "/teamspace/studios/this_studio/.dvc_cache"

    # Create cache directory if it doesn't exist
    os.makedirs(studio_cache_dir, exist_ok=True)

    # Check current cache configuration
    try:
        result = subprocess.run(
            ["dvc", "cache", "dir"], capture_output=True, text=True, check=True
        )
        current_cache = result.stdout.strip()

        if current_cache != studio_cache_dir:
            print(
                f"Configuring DVC cache to use studio-level directory: {studio_cache_dir}"
            )
            # Use --local flag to save in .dvc/config.local (git-ignored)
            subprocess.run(
                ["dvc", "cache", "dir", studio_cache_dir, "--local"], check=True
            )
            print("✅ DVC cache configured for Lightning Studio (in .dvc/config.local)")
    except subprocess.CalledProcessError:
        # If cache dir command fails, try to set it anyway
        subprocess.run(["dvc", "cache", "dir", studio_cache_dir, "--local"], check=True)
