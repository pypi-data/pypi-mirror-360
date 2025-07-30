import json
import os
import subprocess
import sys

from click.core import Context

from mdbt.core import Core


class Lightdash(Core):

    def __init__(self, test_mode=False):
        super().__init__(test_mode=test_mode)

    def lightdash_start_preview(
        self, ctx: Context, select: str, preview_name: str, l43: bool
    ):
        # Check to make sure the LIGHTDASH_PROJECT env variable is set
        if not os.getenv("LIGHTDASH_PROJECT"):
            print(
                "LIGHTDASH_PROJECT environment variable not set. Set this key to the ID of the project you will "
                "promote charts to."
            )
            sys.exit(1)
        else:
            print(f"Building for LIGHTDASH_PROJECT: {os.getenv('LIGHTDASH_PROJECT')}")

        self._check_lightdash_for_updates()
        if not preview_name:
            # If no preview name, use the current name of the git branch
            result = subprocess.run(
                ["git", "branch", "--show-current"], stdout=subprocess.PIPE, text=True
            )
            preview_name = result.stdout.strip()

        args = ["lightdash", "start-preview", "--name", preview_name]

        if l43:
            args = args + ["-s", "tag:l3 tag:l4"]

        if select:
            args = args + ["--select", select]

        try:
            print(f'Running command: {" ".join(args)}')
            subprocess.run(args, check=True)
        except subprocess.CalledProcessError as e:
            self.handle_cmd_line_error(e)

    @staticmethod
    def _check_lightdash_for_updates():
        api_str = 'curl -s "https://app.lightdash.cloud/api/v1/health"'

        try:
            result = subprocess.run(
                api_str, shell=True, check=True, text=True, capture_output=True
            )
            # Convert to JSON
            result_json = json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Failure while running command: {api_str}")
            print(e.stderr)
            print(e.stdout)
            sys.exit(e.returncode)

        api_version = result_json["results"]["version"]

        result = subprocess.run(
            ["lightdash", "--version"], check=True, text=True, capture_output=True
        )

        current_version = result.stdout.strip()

        if api_version != current_version:
            print(
                f"API version {api_version} does not match current version {current_version}. Upgrading."
            )
            args = ["npm", "install", "-g", f"@lightdash/cli@{api_version}"]
            subprocess.run(args, check=True)
        else:
            print(
                f"API version {api_version} matches current version {current_version}."
            )
