import subprocess

import pyperclip
from dotenv import find_dotenv
from dotenv import load_dotenv

from mdbt.ai_core import AiCore
from mdbt.prompts import Prompts

load_dotenv(find_dotenv("../.env"))
load_dotenv(find_dotenv(".env"))


class BuildDBTDocs(AiCore):
    """
    # Make sure you have OPENAI_API_KEY set in your environment variables.
    """

    def __init__(self):
        super().__init__()

    def main(self, model_name, sys_context, is_new=False):
        if model_name.endswith(".sql"):
            model_name = model_name[:-4]
        if not is_new:
            print(
                """
            1) Build new DBT documentation.
            2) Check existing DBT documentation against model for missing definitions.
            """
            )
            mode = int(input())
        else:
            mode = 1
        print("Getting file.")
        sql_file_path = self.get_file_path(model_name)

        if "l4" in sql_file_path.lower() or "l3" in sql_file_path.lower():
            system_instructions = Prompts().dbt_docs_gte_l3_prompt
        else:
            system_instructions = Prompts().dbt_docs_lte_l2_prompt

        if sys_context:
            system_instructions += f"\nContext about system docs are generated for: \n{sys_context}\n"

        sample_data = self._get_sample_data_from_snowflake([model_name])

        system_instructions = system_instructions + sample_data[model_name]

        # Might bring this back in the future.
        extra_info = ""

        if mode == 1:
            # Build new documentation
            user_input = self.build_user_msg_mode_1(sql_file_path, extra_info)
            yml_file_path = sql_file_path.replace(".sql", ".yml")
        elif mode == 2:
            # Check existing documentation
            yml_file_path = sql_file_path[:-4] + ".yml"
            user_input = self.build_user_msg_mode_2(
                sql_file_path, yml_file_path, extra_info
            )
        else:
            print(mode)
            raise ValueError("Invalid mode")

        messages = [
            {"role": "user", "content": system_instructions + "\n" + user_input}
        ]

        assistant_responses = []
        result = self.send_message(messages)
        assistant_responses.append(result)

        messages.append({"role": "assistant", "content": assistant_responses[0]})
        print(assistant_responses[0])
        output = assistant_responses[0]
        # Check for ``` at end of output (str) and remove
        # Remove trailing markdown code fences if present
        lines = output.split('\n')
        if lines and '```' in lines[-1].strip():
            lines = lines[:-1]
        elif len(lines) > 1 and '```' in lines[-2].strip():
            # Remove the second-to-last line if it's a code fence
            lines.pop(-2)
        output = '\n'.join(lines)
        if not is_new:
            clip_or_file = input(
                f"1. to copy to clipboard\n2, to write to file ({yml_file_path}\n:"
            )
        else:
            clip_or_file = "2"

        if clip_or_file == "1":
            print("Output copied to clipboard")
            pyperclip.copy(output)
        elif clip_or_file == "2":
            if mode == 2:
                # Make a backup of the current YML file.
                self.backup_existing_yml_file(yml_file_path)
            output = assistant_responses[0].split("\n")
            # output = output[1:-1]
            output = output[1:]
            output = "\n".join(output)
            with open(yml_file_path, "w") as file:
                file.write(output)
            if not self.is_file_committed(yml_file_path):
                if not is_new:
                    commit_file = input("Press 1 to add to git, any other key to byapss: ")
                else:
                    commit_file = "1"

                if commit_file == "1":
                    subprocess.run(["git", "add", yml_file_path])

    @staticmethod
    def backup_existing_yml_file(yml_file_path):
        with open(yml_file_path, "r") as file:
            yml_content = file.read()
        with open(yml_file_path + ".bak", "w") as file:
            file.write(yml_content)

    def build_user_msg_mode_1(self, _sql_file_path: str, extra_info: str) -> str:
        self.read_file(_sql_file_path)
        model_name = _sql_file_path.split("/")[-1].split(".")[0]
        prompt_str = f"Build new DBT documentation for the following SQL query with model name {model_name}"
        if len(extra_info):
            prompt_str += f"\n{extra_info}"

        return prompt_str

    def build_user_msg_mode_2(
        self, _sql_file_path: str, _yml_file_path: str, extra_info: str
    ) -> str:
        self.read_file(_sql_file_path)
        yml = self.read_file(_yml_file_path)
        model_name = _sql_file_path.split("/")[-1].split(".")[0]
        prompt_str = f"Check for missing columns in the following DBT documentation for the following SQL query with model name {model_name}. Identify any columns in the DBT documentation that do not exist in the SQL and comment them out."
        if len(extra_info):
            prompt_str += f"\n {extra_info}"
        prompt_str += f"\nYML File Contents:\n{yml}"

        return prompt_str


if __name__ == "__main__":
    BuildDBTDocs().main("revenue_by_dvm")
