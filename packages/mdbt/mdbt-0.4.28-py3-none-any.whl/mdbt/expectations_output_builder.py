import os

import yaml

from mdbt.core import Core


class ExpectationsOutputBuilder(Core):

    def __init__(self, test_mode=False):
        super().__init__(test_mode=test_mode)

    def main(self, select):
        args = ["--output-keys", "name resource_type original_file_path"]
        if select:
            args += ["--select", select]
        model_data = self.dbt_ls_to_json(args)
        for model in model_data:
            if model.get("resource_type") == "model":
                yaml_file_path = model.get("original_file_path")[:-4] + ".yml"
                database = os.environ.get("DEV_DATABASE")
                schema = os.environ.get("DEV_SCHEMA")
                model_name = model.get("name")
                self.process_yaml(yaml_file_path, database, schema, model_name)

    def process_yaml(self, yaml_file_path, database, schema, model_name):
        with open(yaml_file_path, "r") as f:
            yaml_content = yaml.safe_load(f)

        model = yaml_content.get("models", [])[0]
        columns = model.get("columns", [])
        print(f"*********\nStarting model: {model_name}\n*********")
        for column in columns:
            column_name = column.get("name")
            data_tests = column.get("data_tests", [])

            for data_test in data_tests:
                if isinstance(data_test, dict):
                    for expectation_name, expectation_params in data_test.items():
                        # fmt: off
                        expectation_pattern = "dbt_expectations.expect_column_sum_to_be_between"
                        # fmt: on
                        if expectation_name == expectation_pattern:
                            min_value = expectation_params.get("min_value")
                            max_value = expectation_params.get("max_value")
                            row_condition = expectation_params.get("row_condition", "")

                            # Build SQL query
                            sql = f"""
                            SELECT SUM({column_name}) AS current_value
                                 , {min_value} AS expected_lower
                                 , {max_value} AS expected_higher
                                 , iff(current_value between expected_lower and expected_higher, '\033[92m Pass\033[0m', '\033[91m Fail\033[0m') AS result
                            FROM {database}.{schema}.{model_name}
                            """

                            if row_condition:
                                sql += f" WHERE {row_condition}"

                            # Execute the query
                            self._cur.execute(sql)
                            results_df = self._cur.fetch_pandas_all()

                            # Print the results
                            print(f"Model: {model_name}")
                            print(f"Column: {column_name}")
                            print(f"Condition: {row_condition}")
                            print(results_df.to_string(index=False))
                            print("\n")


if __name__ == "__main__":
    builder = ExpectationsOutputBuilder()
    builder.main(select="appointment_revenue_mrpv_metrics")
