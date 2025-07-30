import logging
import os
import re
import warnings
from typing import Dict

import pyperclip
from dotenv import find_dotenv
from dotenv import load_dotenv


load_dotenv(find_dotenv("../.env"))
load_dotenv(find_dotenv(".env"))
# flake8: noqa: E402
from mdbt.ai_core import AiCore


# Have to load env before import openai package.
warnings.simplefilter(action="ignore", category=FutureWarning)
logging.getLogger("snowflake.connector").setLevel(logging.WARNING)


class BuildUnitTestDataAI(AiCore):

    def __init__(self):
        super().__init__(model="o3-mini")

    def main(self, model_name: str):

        file_path = self.get_file_path(model_name)
        # Extract the folder immediately after 'models'. Not sure I need to use this just yet, holding on to it for
        # later.
        layer_name = file_path.split("/")[1][:2]
        sub_folder = file_path.split("/")[2]
        file_name = os.path.splitext(os.path.basename(file_path))[0]

        test_file_path = (
            f"tests/unit_tests/{layer_name}/{sub_folder}/test_{file_name}.sql"
        )

        input_sql_file_name = file_path

        input_sql = self.read_file(input_sql_file_name)

        models_in_model_file = self.extract_model_names(input_sql)

        sample_data = self._get_sample_data_from_snowflake(models_in_model_file)

        prompt = self.build_prompt(
            self.prompts.build_unit_test_prompt.format(model_name=model_name),
            model_name,
            input_sql,
            sample_data,
        )

        print(f"##################\n{prompt}\n##################")

        messages = [
            {
                "role": "user",
                "content": "You are helping to build unit tests for DBT (database build tools) models.\n"
                + prompt,
            },
        ]

        response = self.send_message(messages)

        output = self._remove_first_and_last_line_from_string(response)
        print(output)

        clip_or_file = input(
            f"1. to copy to clipboard\n2, to write to file ({test_file_path}"
        )

        if clip_or_file == "1":
            print("Output copied to clipboard")
            pyperclip.copy(output)
        elif clip_or_file == "2":
            # Check if file exists and ask if it should be overwritten.
            if os.path.exists(test_file_path):
                overwrite = input(f"File {test_file_path} exists. Overwrite? (y/n)")
                if overwrite.lower() == "y":
                    with open(test_file_path, "w") as file:
                        file.write(output)
                    print(f"Output written to {test_file_path}")
            else:
                with open(test_file_path, "w") as file:
                    file.write(output)
                print(f"Output written to {test_file_path}")

    def _remove_first_and_last_line_from_string(self, s: str) -> str:
        return "\n".join(s.split("\n")[1:-1])

    @staticmethod
    def extract_model_names(dbt_script):
        # Regular expression to find all occurrences of {{ ref('model_name') }}
        pattern = r"\{\{\s*ref\('([^']+)'\)\s*\}\}"
        # Find all matches in the script
        model_names = re.findall(pattern, dbt_script)
        return model_names

    @staticmethod
    def build_prompt(
        prompt_template: str,
        model_name: str,
        model_sql,
        sample_models_and_data: Dict[str, str],
    ):
        sample_str = ""
        for model_name, sample_data in sample_models_and_data.items():
            sample_str += f"""{model_name}: \n{sample_data}\n"""

        output = f"""
The model name we are building the test for is {model_name}. In the example, this says "model_name". Put this value in that same place.'
{prompt_template}

The SQL for the model is:
{model_sql}

Here is sample data for each input model. This just represents a random sample. Use it to create realistic test data, but try to build the test input data so that it tests the logic found within the model, regardless of the particular combination of sample data. Imagine that certain flags might be true or false, even if that flag is always true or false in the sample data.

{sample_str}

"""
        return output


if __name__ == "__main__":
    BuildUnitTestDataAI().main("avg_client_rev_per_year")
