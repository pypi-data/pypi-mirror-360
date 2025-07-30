import os
import shutil
import subprocess

from click.core import Context

from mdbt.core import Core


class Recce(Core):

    def __init__(self, test_mode=False):
        super().__init__(test_mode=test_mode)

    def recce(self, ctx: Context):
        print("Downloading production artifacts.")
        current_dir = os.getcwd()
        # Initialize variables
        target_path = None
        logs = None
        # Check if current directory ends with 'transform'
        if current_dir.endswith("transform"):
            target_path = os.path.join("target-base")
            logs = os.path.join("logs")
        elif os.path.isdir(os.path.join(current_dir, "transform")):
            target_path = os.path.join("transform", "target-base")
            logs = os.path.join("transform", "logs")
        else:
            raise FileNotFoundError(
                "No 'transform' directory found in the current execution directory."
            )
        os.makedirs(target_path, exist_ok=True)

        # Delete all files in target_path
        for file_name in os.listdir(target_path):
            file_path = os.path.join(target_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Pull artifacts from Snowflake. These are the latest production artifacts.
        try:
            if not self.test_mode:
                subprocess.run(
                    ["dbt", "run-operation", "get_last_artifacts"], check=True
                )
        except subprocess.CalledProcessError as e:
            self.handle_cmd_line_error(e)

        # Copy files from logs to target_path
        if os.path.isdir(logs):
            for file_name in os.listdir(logs):
                full_file_path = os.path.join(logs, file_name)
                if os.path.isfile(full_file_path):
                    shutil.copy(full_file_path, target_path)
        else:
            raise FileNotFoundError(
                f"'logs' directory not found at expected path: {logs}"
            )

        # Start recce server
        try:
            if not self.test_mode:
                subprocess.run(["dbt", "docs", "generate"], check=True)
                subprocess.run(["recce", "server"], check=True)
        except subprocess.CalledProcessError as e:
            self.handle_cmd_line_error(e)
