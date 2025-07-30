import os
import subprocess
import sys

from click.core import Context

from mdbt.core import Core


class PrecommitFormat(Core):

    def __init__(self, test_mode=False):
        super().__init__(test_mode=test_mode)

    def pre_commit(self, ctx):
        args = ["pre-commit", "run", "--all-files"]

        try:
            subprocess.run(args, check=True)
        except subprocess.CalledProcessError as e:
            self.handle_cmd_line_error(e)

    def format(self, ctx: Context, select, all=False, main=False):
        """
        Scan for files that have changed since the last commit and pass them to sqlfluff fix command for cleanup.

        Args:
            ctx: Context object.
        """
        print("Scanning for changed files since last commit.")
        # Set the env path to the .sqlfluffignore
        os.environ["SQLFLUFF_CONFIG"] = "../.sqlfluffignore"
        try:
            if main:
                # Check against main.
                result = subprocess.run(
                    ["git", "diff", "--name-only", "main"],
                    stdout=subprocess.PIPE,
                    text=True,
                    check=True,
                )
            else:
                # Check against last commit.
                result = subprocess.run(
                    ["git", "diff", "--name-only"],
                    stdout=subprocess.PIPE,
                    text=True,
                    check=True,
                )
            changed_files = result.stdout.splitlines()
        except subprocess.CalledProcessError as e:
            print(f'Failure while running git command: {" ".join(e.cmd)}')
            print(e.stderr)
            print(e.stdout)
            sys.exit(e.returncode)

        # Filter SQL files
        sql_files = [file for file in changed_files if file.endswith(".sql")]

        # Filter out any files that are not in the models directory
        sql_files = [file for file in sql_files if "models" in file]

        if not sql_files and not all:
            print("No SQL files have changed since the last commit.")
            return

        if all:
            sql_files = ["./models"]

        for sql_file in sql_files:
            try:
                print(f"Running sqlfluff fix on {sql_file}")
                subprocess.run(
                    ["sqlfluff", "fix", sql_file, "--config", "../.sqlfluff"],
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                print(f"Failure while running sqlfluff fix command on {sql_file}")
                print(e.stderr)
                print(e.stdout)
                # Optionally, we might not want to exit immediately but continue fixing other files
                # sys.exit(e.returncode)

        print("Sqlfluff fix completed for all changed SQL files.")
