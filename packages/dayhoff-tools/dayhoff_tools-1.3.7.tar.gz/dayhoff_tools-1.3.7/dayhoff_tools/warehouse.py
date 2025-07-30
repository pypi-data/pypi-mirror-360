import os
import subprocess
from datetime import datetime
from io import StringIO
from pathlib import Path
from zoneinfo import ZoneInfo

from ruamel.yaml import YAML


def human_readable_size(size_bytes):
    """Convert size in bytes to a human-readable format"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def format_yaml_with_meta_spacing(yaml_str: str) -> str:
    """
    Format YAML content with blank lines between top-level sections and meta subsections.
    Avoids adding duplicate blank lines.
    """
    lines = yaml_str.split("\n")
    formatted_lines = []
    in_meta = False
    meta_depth = 0
    last_line_blank = True  # Start true to avoid adding blank line at the beginning

    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line == "meta:":
            in_meta = True
            meta_depth = 0
            if not last_line_blank:
                formatted_lines.append("")  # Add a blank line before 'meta:' if needed
            formatted_lines.append(line)
            if (
                i + 1 < len(lines) and lines[i + 1].strip()
            ):  # Check if next line is not blank
                formatted_lines.append(
                    ""
                )  # Add a blank line after 'meta:' only if needed
            last_line_blank = True
        elif in_meta:
            if stripped_line and not line.startswith("  "):
                in_meta = False
                if not last_line_blank:
                    formatted_lines.append(
                        ""
                    )  # Add a blank line before leaving 'meta' if needed
                formatted_lines.append(line)
                last_line_blank = False
            else:
                current_depth = len(line) - len(line.lstrip())
                if current_depth == 2 and meta_depth >= 2 and not last_line_blank:
                    formatted_lines.append(
                        ""
                    )  # Add a blank line before new top-level category in meta if needed
                formatted_lines.append(line)
                meta_depth = current_depth
                last_line_blank = not stripped_line
        else:
            if stripped_line and not line.startswith(" ") and not last_line_blank:
                formatted_lines.append(
                    ""
                )  # Add a blank line before top-level keys if needed
            formatted_lines.append(line)
            last_line_blank = not stripped_line

    return "\n".join(formatted_lines).rstrip() + "\n"


def update_dvc_files(directory):
    """Traverse directory and update .dvc files with human-readable size, preserving existing formatting"""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".dvc"):
                file_path = Path(root) / file
                with open(file_path, "r") as f:
                    dvc_content = yaml.load(f)

                if "outs" in dvc_content and dvc_content["outs"]:
                    size_bytes = dvc_content["outs"][0].get("size", 0)
                    human_size = human_readable_size(size_bytes)

                    if "meta" not in dvc_content:
                        dvc_content["meta"] = {}

                    # Create a new ordered dict with 'size' as the first item
                    new_meta = {"size": human_size}
                    new_meta.update(dvc_content["meta"])
                    dvc_content["meta"] = new_meta

                # Convert the updated content to a string and format it
                string_stream = StringIO()
                yaml.dump(dvc_content, string_stream)
                formatted_content = format_yaml_with_meta_spacing(
                    string_stream.getvalue()
                )

                with open(file_path, "w") as f:
                    f.write(formatted_content)

                print(f"Updated {file_path}")


def import_from_warehouse(
    warehouse_path: str,
    output_folder: str = "same_as_warehouse",
    branch: str = "main",
    logger=None,
) -> str:
    """Import a file from warehouse, or update if it exists already.

    Args:
        warehouse_path (str): The relative path to a .dvc file in the
                warehouse submodule of the current repo.
                eg, 'warehouse/data/toy/2seqs.fasta.dvc'
        output_folder (str): A folder where the file will be imported.
                eg, 'data/raw/'. Defaults to the same folder as the
                original location in warehouse.
        branch (str): The branch of warehouse to import from.

    Returns: The path to the imported/updated file.
    """
    assert warehouse_path.startswith(
        "warehouse"
    ), "expected the relative path to start with 'warehouse'"
    assert warehouse_path.endswith(
        ".dvc"
    ), "expected the relative path to end with '.dvc'"

    if branch != "main":
        if logger:
            logger.warning("You should usually import data from main.")
        else:
            print("WARNING: You should usually import data from main.\n")

    # Remove extra slashes
    if output_folder.endswith("/"):
        output_folder = output_folder[:-1]

    # The core path is the same within warehouse and in the
    # local data folder where the file will be imported by default
    core_path = warehouse_path[len("warehouse/") : -len(".dvc")]
    filename = core_path.split("/")[-1]

    command = [
        "dvc",
        "import",
        "https://github.com/dayhofflabs/warehouse",
        core_path,
    ]

    if output_folder == "same_as_warehouse":
        final_path = core_path
        final_folder = "/".join(final_path.split("/")[:-1])
    else:
        final_folder = output_folder
        final_path = final_folder + "/" + filename

    os.makedirs(final_folder, exist_ok=True)
    command += ["--out", final_path, "--rev", branch]

    if os.path.exists(final_path):
        # Update existing file.  This re-writes if it doesn't match origin,
        # and also updates the .dvc file.
        if logger:
            logger.info(
                "File already exists. Will `dvc update` instead of `dvc import`."
            )
        else:
            print(f"File already exists. Will `dvc update` instead of `dvc import`.")
        subprocess.run(
            ["dvc", "update", final_path + ".dvc", "--rev", branch], check=True
        )
    else:
        if logger:
            logger.info(f"Importing from warehouse: {final_path}")
        else:
            print(f"Importing from warehouse: {final_path}")
        subprocess.run(command, check=True)

    # Copy meta section from warehouse_path to final_path.dvc
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    # Read the original warehouse .dvc file
    with open(warehouse_path, "r") as f:
        warehouse_content = yaml.load(f)

    # Read the newly created/updated .dvc file
    final_dvc_path = final_path + ".dvc"
    with open(final_dvc_path, "r") as f:
        final_dvc_content = yaml.load(f)

    # Copy the meta section if it exists in the warehouse file
    if "meta" in warehouse_content:
        final_dvc_content["meta"] = warehouse_content["meta"]

    # Convert the updated content to a string and format it
    string_stream = StringIO()
    yaml.dump(final_dvc_content, string_stream)
    formatted_content = format_yaml_with_meta_spacing(string_stream.getvalue())

    # Write the formatted content back to the file
    with open(final_dvc_path, "w") as f:
        f.write(formatted_content)

    if logger:
        logger.info(f"Updated {final_dvc_path} with meta section from {warehouse_path}")
    else:
        print(f"Updated {final_dvc_path} with meta section from {warehouse_path}")

    return final_path


def add_to_warehouse(
    warehouse_path: str,
    ancestor_dvc_paths: list[str],
) -> str:
    """Upload a file to warehouse, using `dvc add`, and edit its .dvc file
    to add information about ancestors.
    Args:
        warehouse_path (str): The relative path (in warehouse) where the new
                                data file should go.
        ancestor_dvc_paths (list[str]): A list of all the paths to the frozen
                        .dvc files that were produced when importing the
                        ancestors to this file.
    Returns: The path to the new .dvc file.
    Raises:
        ValueError: If the function is executed outside of the repo's root directory.
        ValueError: If an ancestor .dvc file is not frozen.
    """

    print(f"Uploading to Warehouse: {warehouse_path}")
    assert warehouse_path.startswith(
        "warehouse/"
    ), "expected the relative path to start with 'warehouse/'"
    warehouse_path = warehouse_path.replace("warehouse/", "")

    # Process each ancestor .dvc file
    ancestors = []
    yaml_loader = YAML()
    yaml_loader.preserve_quotes = True
    yaml_loader.indent(mapping=2, sequence=4, offset=2)
    for path in ancestor_dvc_paths:
        assert path.endswith(".dvc"), "ERROR: Not a .dvc file"
        with open(path, "r") as file:
            ancestor_content = yaml_loader.load(file)

            # Check if the .dvc file is frozen
            if (
                "frozen" not in ancestor_content
                or ancestor_content["frozen"] is not True
            ):
                raise ValueError(
                    f"Error: Not a frozen .dvc file generated by 'dvc import': {path}"
                )

            ancestor_info = {
                "name": os.path.basename(ancestor_content["outs"][0]["path"]),
                "file_md5_hash": ancestor_content["outs"][0]["md5"],
                "repo_url": ancestor_content["deps"][0]["repo"]["url"],
                "repo_path": ancestor_content["deps"][0]["path"],
                "commit_hash": ancestor_content["deps"][0]["repo"]["rev_lock"],
            }

            # Add the optional "git_branch" field if available
            if "rev" in ancestor_content["deps"][0]["repo"]:
                ancestor_info["git_branch"] = ancestor_content["deps"][0]["repo"]["rev"]

            ancestors.append(ancestor_info)

    # Change the working directory to the warehouse folder
    os.chdir("warehouse")

    # Configure DVC cache for Lightning Studio if needed
    if os.path.exists("/teamspace/studios/this_studio"):
        studio_cache_dir = "/teamspace/studios/this_studio/.dvc_cache"
        os.makedirs(studio_cache_dir, exist_ok=True)
        try:
            result = subprocess.run(
                ["dvc", "cache", "dir"], capture_output=True, text=True, check=True
            )
            current_cache = result.stdout.strip()
            if current_cache != studio_cache_dir:
                subprocess.run(
                    ["dvc", "cache", "dir", studio_cache_dir, "--local"], check=True
                )
                print(
                    f"✅ Configured warehouse DVC cache for Lightning Studio: {studio_cache_dir}"
                )
        except subprocess.CalledProcessError:
            subprocess.run(
                ["dvc", "cache", "dir", studio_cache_dir, "--local"], check=True
            )

    # Add and push the data file
    subprocess.run(["dvc", "add", warehouse_path], check=True)

    # Read the generated .dvc file
    dvc_file_path = f"{warehouse_path}.dvc"
    with open(dvc_file_path, "r") as file:
        dvc_content = yaml_loader.load(file)

    # Add the ancestors' information
    dvc_content["ancestors"] = ancestors

    # Get the human-readable size
    size_bytes = dvc_content["outs"][0]["size"]
    human_size = human_readable_size(size_bytes)

    # Write this, plus more metadata, back to the .dvc file
    today = datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d")

    # Use ruamel.yaml's ScalarString for block-style literal formatting
    from ruamel.yaml.scalarstring import LiteralScalarString

    description = LiteralScalarString("MISSING_METADATA\nMISSING_METADATA")

    yaml_content = {
        "outs": dvc_content["outs"],
        "meta": {
            "size": human_size,
            "date_created": today,
            "author": "MISSING_METADATA",
            "description": description,
            "transformation_source_code": [
                "MISSING_METADATA",
            ],
            "ancestors": dvc_content["ancestors"],
        },
    }

    # Convert the updated content to a string and format it
    string_stream = StringIO()
    yaml_loader.dump(yaml_content, string_stream)
    formatted_content = format_yaml_with_meta_spacing(string_stream.getvalue())

    # Write the formatted content back to the file
    with open(dvc_file_path, "w") as file:
        file.write(formatted_content)

    # Point the user to the updated .dvc file
    print(f"\033[92m\n\nMade .dvc file: {dvc_file_path}\033[0m")
    print(
        f"\033[92mRemember to manually fill out the missing metadata fields.\n\033[0m"
    )

    subprocess.run(["dvc", "push"], check=True)
    os.chdir("..")

    return "warehouse/" + dvc_file_path


def get_from_warehouse(
    warehouse_path: str,
    output_folder: str = "same_as_warehouse",
    branch: str = "main",
    logger=None,
) -> str:
    """`dvc get` a file from warehouse.

    Args:
        warehouse_path (str): The relative path to a .dvc file in the
                warehouse submodule of the current repo.
                eg, 'warehouse/data/toy/2seqs.fasta.dvc'
        output_folder (str): A folder where the file will be imported.
                eg, 'data/raw/'. Defaults to the same folder as the
                original location in warehouse.
        branch (str): The branch of warehouse to import from.

    Returns: The path to the imported/updated file.
    Raises:
        ValueError: If the function is executed outside of the repo's root directory.
    """

    assert warehouse_path.startswith(
        "warehouse"
    ), "expected the relative path to start with 'warehouse'"
    assert warehouse_path.endswith(
        ".dvc"
    ), "expected the relative path to end with '.dvc'"

    if branch != "main":
        if logger:
            logger.warning("You should usually import data from main.")
        else:
            print("WARNING: You should usually import data from main.\n")

    # Remove extra slashes
    if output_folder.endswith("/"):
        output_folder = output_folder[:-1]

    # The core path is the same within warehouse and in the
    # local data folder where the file will be imported by default
    core_path = warehouse_path[len("warehouse/") : -len(".dvc")]
    filename = core_path.split("/")[-1]

    command = [
        "dvc",
        "get",
        "https://github.com/dayhofflabs/warehouse",
        core_path,
    ]

    if output_folder == "same_as_warehouse":
        final_path = core_path
        final_folder = "/".join(final_path.split("/")[:-1])
    else:
        final_folder = output_folder
        final_path = final_folder + "/" + filename

    os.makedirs(final_folder, exist_ok=True)
    command += ["--out", final_path, "--rev", branch]

    if os.path.exists(final_path):
        # Update existing file.  This re-writes if it doesn't match origin,
        # and also updates the .dvc file.
        if logger:
            logger.info("File already exists. Will exit without changing.")
        else:
            print(f"File already exists. Will exit without changing.")
    else:
        if logger:
            logger.info(f"Getting from warehouse: {final_path}")
        else:
            print(f"Getting from warehouse: {final_path}")
        subprocess.run(command, check=True)

    return final_path
