import os
import re
import subprocess
from typing import Dict
from typing import List

import openai
from snowflake.connector import DatabaseError

from mdbt.core import Core
from mdbt.prompts import Prompts

# Have to load env before import openai package.
# flake8: noqa: E402


class AiCore(Core):

    def __init__(self, model: str = "gpt-4.1", test_mode: bool = False):
        super().__init__(test_mode=test_mode)
        self.model = model
        # Make sure you have OPENAI_API_KEY set in your environment variables.
        self.client = openai.OpenAI()

        self.prompts = Prompts()

    def send_message(self, _messages: List[Dict[str, str]]) -> object:
        print("Sending to API")
        completion = self.client.chat.completions.create(
            model=self.model, messages=_messages
        )
        return completion.choices[0].message.content

    @staticmethod
    def read_file(path: str) -> str:
        with open(path, "r") as file:
            return file.read()

    @staticmethod
    def is_file_committed(file_path):
        try:
            # Check the Git status of the file
            subprocess.run(
                ["git", "ls-files", "--error-unmatch", file_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            # If the file is tracked, check if it has any modifications
            status_result = subprocess.run(
                ["git", "status", "--porcelain", file_path], stdout=subprocess.PIPE
            )
            status_output = status_result.stdout.decode().strip()
            # If the output is empty, file is committed and has no modifications
            return len(status_output) == 0
        except subprocess.CalledProcessError:
            # The file is either untracked or does not exist
            return False

    def _get_sample_data_from_snowflake(self, model_names: List[str]) -> Dict[str, str]:
        """
        Compiles the target model to SQL, then breaks out each sub query and CTE into a separate SQL strings, executing
        each to get a sample of the data.
        Args:
            model_names: A list of target model names to pull sample data from.

        Returns:
            A dictionary of model names and their sample data in CSV format.
        """
        sample_results = {}
        for model_name in model_names:
            print(f"Getting sample data for {model_name}")
            args = ["--select", model_name]
            cmd = "compile"
            results = self.execute_dbt_command_capture(cmd, args)
            extracted_sql = self.extract_sql(results)
            sample_sql = self.build_sample_sql(extracted_sql)
            try:
                self._cur.execute(sample_sql)
            except DatabaseError as e:
                print(f"Error executing sample SQL for {model_name}")
                print(e)
                print("\n\n" + sample_sql + "\n\n")
                raise e
            tmp_df = self._cur.fetch_pandas_all()
            sample_results[model_name] = tmp_df.to_csv(index=False)
        print(f"Sample results: {sample_results}")
        return sample_results

    @staticmethod
    def build_sample_sql(sql: str) -> str:
        sql = f"""
            with tgt_table as (
                {sql}
            )
            select *
            from tgt_table
            sample (10 rows)
            """
        return sql

    @staticmethod
    def extract_sql(log):
        sql_lines = [line for line in log.splitlines() if not re.match(r"--\s.*", line)]

        keyword_line_index = 0
        for i, line in enumerate(sql_lines):
            if "Compiled node" in line:
                keyword_line_index = i + 1
                break

        sql_lines = sql_lines[keyword_line_index:]

        # Join the remaining lines and remove escape sequences
        sql = "\n".join(sql_lines).replace("\x1b[0m", "").strip()
        return sql
