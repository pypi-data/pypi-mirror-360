import unittest
from unittest.mock import patch

import yaml

from mdbt.sort_yaml_fields import SortYAML


class SortYAMLTest(unittest.TestCase):

    def setUp(self):
        self.sort_yaml = SortYAML()

    def test_read_yml(self):
        yaml_content = """
        version: 2
        models:
          - name: test
            columns:
              - name: column1
                description: "desc1"
              - name: column2
                description: "desc2"
        """
        with patch("builtins.open", unittest.mock.mock_open(read_data=yaml_content)):
            result = self.sort_yaml.read_yml("dummy_path.yml")
        expected = yaml.safe_load(yaml_content)
        self.assertEqual(result, expected)

    def test_reorganize_columns(self):
        schema_data_str = """
version: 2
models:
  - name: test
    config:
        materialized: view
    columns:
      - name: column3
        description: "desc3"
        meta:
            dimension:
                hidden: false
            metrics:
                total_revenue:
                    type: sum
                    sql: "SQL_QUERY_HERE"
                    group_label: "Total Revenue"
      - name: column1
        description: "desc1"
      - name: column2
        description: "desc2"
        """

        schema_data = yaml.safe_load(schema_data_str)
        db_columns = ["column1", "column2", "column3"]
        expected_schema = {
            "version": 2,
            "models": [
                {
                    "name": "test",
                    "config": {"materialized": "view"},
                    "columns": [
                        {"name": "column1", "description": "desc1"},
                        {"name": "column2", "description": "desc2"},
                        {
                            "name": "column3",
                            "description": "desc3",
                            "meta": {
                                "dimension": {"hidden": False},
                                "metrics": {
                                    "total_revenue": {
                                        "type": "sum",
                                        "sql": "SQL_QUERY_HERE",
                                        "group_label": "Total Revenue",
                                    }
                                },
                            },
                        },
                    ],
                }
            ],
        }
        result = self.sort_yaml.reorganize_columns(schema_data, db_columns)

        self.assertEqual(result, expected_schema)


if __name__ == "__main__":
    unittest.main()
