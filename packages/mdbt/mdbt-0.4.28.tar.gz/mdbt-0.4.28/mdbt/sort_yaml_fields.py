# Using this instead of the default as it preserves the order of keys in the dictionary.
import os
import sys
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import pyperclip
from dotenv import find_dotenv
from dotenv import load_dotenv
from ruamel.yaml import YAML

from mdbt.ai_core import AiCore
from mdbt.main import MDBT

load_dotenv(find_dotenv("../.env"))
load_dotenv(find_dotenv(".env"))

# Modify the dumper to not sort keys and to use ordered dict format


class SortYAML(AiCore):
    def __init__(self):
        super().__init__()
        self.yaml = YAML(typ="rt")
        self.yaml.preserve_quotes = True
        self.yaml.explicit_start = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)

    def main(
        self,
        select: Optional[str] = None,
        all_files: Optional[bool] = False,
        overwrite: Optional[bool] = False,
    ):
        models = self._get_models(select, all_files)
        if len(models) > 1 and not overwrite:
            raise ValueError(
                "Multiple models found. Default copy to clipboard only works with one model. Use the --overwrite flag "
                "if processing more than one model at a time."
            )
        if not models:
            raise ValueError(f"No models found for select '{select}'")

        for model in models:
            original_file_path = model["original_file_path"]
            model_name = model["name"]
            schema_file, table_name = self._get_schema_path_and_table(
                original_file_path=original_file_path, model_name=model_name
            )
            schema_data = self.read_yml(schema_file)
            db_columns = self.get_db_columns(table_name)
            updated_schema = self.reorganize_columns(schema_data, db_columns)

            if overwrite:
                with open(schema_file, "w") as stream:
                    self.yaml.dump(
                        updated_schema, stream, transform=self.clean_top_line
                    )
                self.yaml.dump(
                    updated_schema, sys.stdout, transform=self.clean_top_line
                )
                print(f"Schema file '{schema_file}' updated")
            else:
                self.save_yml_to_clipboard(updated_schema)

    def _get_models(self, select: str, all_files: bool) -> List[Dict[str, Any]]:
        mmw = MDBT()
        if not all_files:
            args = [
                "--select",
                select,
                "--exclude",
                "resource_type:test resource_type:seed resource_type:snapshot resource_type:source",
            ]
        else:
            args = [
                "--exclude",
                "resource_type:test resource_type:seed resource_type:snapshot resource_type:source",
            ]
        ls_json = mmw.dbt_ls_to_json(args)

        return ls_json

    @staticmethod
    def _get_schema_path_and_table(
        original_file_path: str, model_name: str
    ) -> Tuple[str, str]:
        schema_file = original_file_path[:-3] + "yml"
        schema = os.environ.get("DEV_SCHEMA")
        if not schema:
            raise ValueError("DEV_SCHEMA environment variable is not set")
        database = os.environ.get("DEV_DATABASE")
        if not database:
            raise ValueError("DEV_DATABASE environment variable is not set")
        table_name = f"{database}.{schema}.{model_name}"
        print(f"Schema file: {schema_file}")
        print(f"Table name: {table_name}")
        return schema_file, table_name

    def read_yml(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, "r") as stream:
            return self.yaml.load(stream)

    def save_yml_to_clipboard(self, data: Dict[str, Any]):
        # Convert yaml to string. This yaml class is a pain in the ass to get it to return a string. This is sort of
        # a hack where it will send the string data to the copy_to_clip function which saves it to the clipboard.
        # It honestly seems like the guy who wrote this class never considered any need beyond dumping to the stdout.
        self.yaml.dump(data, sys.stdout, transform=self.copy_to_clip)
        print("Sorted YAML schema copied to clipboard!")

    def copy_to_clip(self, string_yaml: str) -> str:
        # Remove the first line of the string
        string_yaml = self.clean_top_line(string_yaml)
        pyperclip.copy(string_yaml)
        print("Sorted YAML schema copied to clipboard!")
        return string_yaml

    def clean_top_line(self, string_yaml: str) -> str:
        str_lines = string_yaml.split("\n")
        string_yaml = "\n".join(str_lines[1:])
        return string_yaml

    def get_db_columns(self, table_name: str) -> list:
        self._cur.execute(f"SELECT * FROM {table_name} LIMIT 0")
        return [desc[0].lower() for desc in self._cur.description]

    def reorganize_columns(
        self, schema_data: Dict[str, Any], db_columns: list
    ) -> Dict[str, Any]:
        if "models" not in schema_data or not schema_data["models"]:
            raise ValueError("YML schema does not contain any models")
        model = schema_data["models"][0]  # Assuming a single model for simplicity
        columns = model.get("columns", [])
        col_dict = {col["name"]: col for col in columns}

        sorted_columns = [col_dict[col] for col in db_columns if col in col_dict]

        model["columns"] = sorted_columns
        schema_data["models"][0] = model
        return schema_data


if __name__ == "__main__":
    y = SortYAML()
    y.main(select=None, all_files=True, overwrite=True)
