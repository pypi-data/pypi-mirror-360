"""new_python-project: Main module.

© Reuben Thomas <rrt@sc3d.org> 2025.

Released under the GPL version 3, or (at your option) any later version.
"""

import argparse
import importlib.metadata
import importlib.resources
import os
import os.path
import pwd
import shutil
import subprocess
import sys
import tomllib
import warnings
from contextlib import chdir
from typing import Any

from .warnings_util import simple_warning


VERSION = importlib.metadata.version("new_python_project")


def main(argv: list[str] = sys.argv[1:]) -> None:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description="Python project creator.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"""%(prog)s {VERSION}
© 2025 Reuben Thomas <rrt@sc3d.org>
https://github.com/rrthomas/new-python-project
Distributed under the GNU General Public License version 3, or (at
your option) any later version. There is no warranty.""",
    )
    parser.add_argument(
        "--noprompt",
        action="store_true",
        help="do not prompt; use default values for details",
    )
    parser.add_argument(
        "--github",
        action="store_true",
        help="create a GitHub project",
    )
    parser.add_argument(
        "project_dir",
        metavar="DIRECTORY",
        help="directory in which to create project",
    )
    parser.add_argument(
        "project_data",
        metavar="TOML-FILE",
        nargs="?",
        help="TOML file containing project information",
    )
    warnings.showwarning = simple_warning(parser.prog)
    args = parser.parse_args(argv)

    def input_with_default(prompt: str, default: str) -> str:
        if args.noprompt:
            return default
        response = input(f"{prompt} [{default}]: ")
        return response or default

    # Load information from TOML file if supplied
    project = {}
    if args.project_data:
        with open(args.project_data, "rb") as f:
            toml_data = tomllib.load(f)
        if "project" not in toml_data:
            raise ValueError(f"no 'project' section found in {args.project_data}")
        project: dict[str, Any] = toml_data["project"]

    # Get missing info about the project
    if "name" not in project:
        project["name"] = input_with_default(
            "Name of project", os.path.basename(args.project_dir)
        )
    project["slug"] = project["name"].lower().replace(" ", "-")
    if "description" not in project:
        project["description"] = input_with_default(
            "Short description of project", "FILL ME IN"
        )
    if "authors" not in project:
        project["authors"] = [{}]
        project["authors"][0]["name"] = input_with_default(
            "Author", pwd.getpwuid(os.getuid()).pw_gecos.split(",")[0]
        )
        project["authors"][0]["email"] = input_with_default(
            "Email", os.environ.get("EMAIL", "")
        )
    use_github = args.github or "github_user" in project
    if use_github and "github_user" not in project:
        gh_command = shutil.which("gh")
        if gh_command is None:
            default_github_user = os.getlogin()
        else:
            default_github_user = (
                subprocess.check_output(["gh", "api", "user", "--jq", ".login"])
                .decode("utf-8")
                .replace("\n", "")
            )
        project["github_user"] = input_with_default(
            "GitHub user",
            default_github_user,
        )
    if "home_page" not in project:
        if use_github:
            default_url = (
                f"https://github.com/{project['github_user']}/{project['slug']}"
            )
        else:
            default_url = f"https://{project['slug']}.example.net"
        project["home_page"] = input_with_default(
            "Project home page",
            default_url,
        )

    # Template the project
    with importlib.resources.as_file(importlib.resources.files()) as fspath:
        template_dir = os.path.join(fspath, "template")
        subprocess_env = os.environ.copy()
        subprocess_env.update(
            {
                "PROJECT_NAME": project["name"],
                "PROJECT_HOME_PAGE": project["home_page"],
                "AUTHOR": project["authors"][0]["name"],
                "EMAIL": project["authors"][0]["email"],
                "DESCRIPTION": project["description"],
            }
        )
        if use_github:
            subprocess_env["GITHUB_USER"] = project["github_user"]
        subprocess.check_call(
            ["nancy", "--process-hidden", template_dir, args.project_dir],
            env=subprocess_env,
        )

    # Create the project's git repo and make initial commit
    subprocess.check_call(["git", "init", args.project_dir])
    with chdir(args.project_dir):
        subprocess.check_call(["git", "add", "."])
        subprocess.check_call(
            ["git", "commit", "-m", "Initial commit (by new-python-project)"]
        )

        # Create GitHub project if desired
        if args.github:
            subprocess.check_call(
                [
                    "gh",
                    "repo",
                    "create",
                    project["name"],
                    "--description",
                    project["description"],
                    "--public",
                    "--source=.",
                    "--remote=upstream",
                    "--push",
                ]
            )
