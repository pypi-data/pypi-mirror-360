class Prompts:

    @property
    def dbt_docs_gte_l3_prompt(self):
        return """
You will help build DBT documentation YML files for a given SQL query. Sometimes you will be asked to generate a description from scratch, other times you will be asked to fill in missing columns that exist in the model, but not in the documentation.

These models are built for Marki Microwave, a RF semicoductor company that designed and built RF and microwave components. The models are built to help the company understand their business better. The models are built in DBT and are used to generate reports and dashboards. For acronyms, or other terminology, consider in context of the RF semiconductor industry. 

Primary DBT Guidelines:

    3. Include a config block for each model:
        a. Set `materialized` to `table`
        b. Do not include a `sort` key.
    4. For long descriptions, use the following format so the lines are not too long:
        ```
        - name: replacement_plan_id
          description: >
            Identifier for the replacement plan if applicable. A replacement plan is defined as a plan that
            started within 5 days before, or up to 30 days after the end date of the prior plan and is not
            an add-on plan.
        ```
    5. If you find a column that is in the existing documentation, but not in the model, comment it out with a `#` at the start of each line.
    6. Only return the YML documentation file contents. Do not provide an explanation.
    7. Always place a new line between the end of the `description` line and the start of the next column name identified by `- name:`.
    8. If updating and existing file, do not replace or modify existing descriptions, data_tests:, or config blocks. Only add new ones, and comment out descriptions that don't exist in the SQL.  use data_tests:, not tests:
    9. Reorder or order the column descriptions in the YML file in the same order they appear in the SQL query. If you are modifying an existing YML file, still re-order the elements, don't comment out the old element location and put a new element in.
    10. If modifying an existing YML, leave the value of materialized as is. Do not change it to `table` if it is `view` or vice versa.
    11. Use lowercase for all column names, metric, and dimension names. The sample data will come back with uppercase column names, but the YML file should have lowercase names.
   
    12. If there is an primary key ID column as the first field, then add a
       ```
       data_tests:
         - unique
         - not_null
       ```

      If the first column is not a primary key ID column, then use a "unique_combination_of_columns" test like this:
        ```
        data_tests:
          - dbt_utils.unique_combination_of_columns:
              combination_of_columns:
                - month_at
                - network_name
        ```



Full example output:
```
version: 2

models:
  - name: appointment_revenue_mrpv_metrics
    description: >
      This model provides Medical Revenue Per Vist (MRPV) metrics. It includes filterable dimensions by first appt/rev
      veterinarian, location, and network.

    config:
      materialized: table

    columns:
      - name: order_at
        description: "The date associated with the order."
        data_tests:
          - not_null

      - name: location_id
        description: "The identifier for the location where the order was placed."

      - name: location_name
        description: "The name of the location where the order was placed."

      - name: network_name
        description: "The name of the network associated with the order."
        
      - name: medical_revenue
        description: "Total revenue from medical services."

      - name: medical_appointment_count
        description: "Count of medical appointments."

```

This is a CSV data sample from the model:
        """

    @property
    def dbt_docs_lte_l2_prompt(self):
        return """
You will help build DBT documentation YML files for a given SQL query. Sometimes you will be asked to generate a description from scratch, other times you will be asked to fill in missing columns that exist in the model, but not in the documentation.

These models are built for Marki Microwave, a RF semicoductor company that designed and built RF and microwave components. The models are built to help the company understand their business better. The models are built in DBT and are used to generate reports and dashboards. For acronyms, or other terminology, consider in context of the RF semiconductor industry. 

Primary DBT Guidelines:

    3. Include a config block for each model:
        a. Set `materialized` to `view`
        b. Do not include a `sort` key.
        c. If the model name ends in `_mat` set materialized to `table`.
    4. Add data_tests: `unique` and `not_null` to the primary key only. Do not add data_tests: to any other columns. use data_tests:, not tests:
    5. For long descriptions, use the following format so the lines are not too long:
        ```
        - name: replacement_plan_id
          description: >
            Identifier for the replacement plan if applicable. A replacement plan is defined as a plan that
            started within 5 days before, or up to 30 days after the end date of the prior plan and is not
            an add-on plan.
        ```
    6. If you find a column that is in the existing documentation, but not in the model, comment it out with a `#` at the start of each line.
    7. Only return the YML documentation file contents. Do not provide an explanation.
    8. Always place a new line between the end of the `description` line and the start of the next column name identified by `- name:`.
    9. Do not replace or modify existing descriptions, data_tests:, or config blocks. Only add new ones, and comment out descriptions that don't exist in the SQL.
    10. Reorder or order the column descriptions in the YML file in the same order they appear in the SQL query. If you are modifying an existing YML file, still re-order the elements, don't comment out the old element location and put a new element in.
    11. If modifying an existing YML, leave the value of materialized as is. Do not change it to `table` if it is `view` or vice versa.
    12. Use lowercase for all column names, metric, and dimension names. The sample data will come back with uppercase column names, but the YML file should have lowercase names.


Full example output:
```
version: 2

models:
  - name: stg_vs_example
    description: >
      This is an example description that is longer than one line. It is a good example of how to write a long
      description using the > character.

    config:
      materialized: table

    columns:
      - name: order_at
        description: "The date associated with the order."

      - name: location_id
        description: "The identifier for the location where the order was placed."

      - name: location_name
        description: "The name of the location where the order was placed."

      - name: network_name
        description: "The name of the network associated with the order."

      - name: medical_revenue
        description: "Total revenue from medical services."

      - name: medical_appointment_count
        description: "Count of medical appointments."
```
This is a CSV data sample from the model:
        """

    @property
    def build_unit_test_prompt(self):

        return """
You will help build mockup input and expected output data for DBT unit data_tests: using the EqualExperts/dbt_unit_testing package. The input and expect data will be in a CSV type format using | as a seperator between fields.

The user will pass a SQL DBT model that looks like this as input:
```
select
    date(o.order_item_at)   as revenue_day_at
  , o.location_id
  , o.is_medical_revenue
  , o.is_plan_payment
  , o.location_name
  , o.product_type_name
  , sum(o.total_before_tax) as revenue_sum

from {{ dbt_unit_testing.ref('fct_order_items_mat') }} o
group by revenue_day_at
       , location_id
       , is_medical_revenue
       , is_plan_payment
       , location_name
       , product_type_name
```

You will return data that looks like this.
Use this line for the dbt_unit_tests.test (name is filled in) `{{% call dbt_unit_testing.test('{model_name}', '{model_name} unit test') %}}` :

```
{{{{ config(tags=['unit-test']) }}}}

--depends-on: {{{{ ref('fct_appointments') }}}}

{{% call dbt_unit_testing.test('model_name', 'Description of Test') %}}

    {{% call dbt_unit_testing.mock_ref('fct_order_items_mat', options={{"input_format": "csv"}}) %}}

    ORDER_ITEM_AT                          |LOCATION_ID |IS_MEDICAL_REVENUE |IS_PLAN_PAYMENT |LOCATION_NAME | PRODUCT_TYPE_NAME    | TOTAL_BEFORE_TAX
    '2024-01-01 00:00:00.000000000 -08:00' |123         |TRUE               |TRUE            |'ABC123'      | 'Product 1'          | 25
    '2024-01-01 00:00:00.000000000 -08:00' |123         |TRUE               |FALSE           |'ABC123'      | 'Product 2'          | 25
    '2024-01-01 00:00:00.000000000 -08:00' |123         |FALSE              |FALSE           |'ABC123'      | 'Product 2'          | 25
    '2024-01-01 00:00:00.000000000 -08:00' |123         |TRUE               |TRUE            |'ABC123'      | 'Product 1'          | 25
    '2024-01-01 00:00:00.000000000 -08:00' |123         |TRUE               |FALSE           |'ABC123'      | 'Product 2'          | 25
    '2024-01-01 00:00:00.000000000 -08:00' |123         |FALSE              |FALSE           |'ABC123'      | 'Product 2'          | 25
    '2024-01-01 00:00:00.000000000 -08:00' |987         |TRUE               |TRUE            |'DEF123'      | 'Product 1'          | 25
    '2024-01-01 00:00:00.000000000 -08:00' |987         |TRUE               |FALSE           |'DEF123'      | 'Product 2'          | 25
    '2024-01-01 00:00:00.000000000 -08:00' |987         |FALSE              |FALSE           |'DEF123'      | 'Product 2'          | 25

    {{% endcall %}}

    {{% call dbt_unit_testing.expect({{"input_format": "csv"}}) %}}

    REVENUE_DAY_AT |LOCATION_ID |IS_MEDICAL_REVENUE |IS_PLAN_PAYMENT |LOCATION_NAME  |PRODUCT_TYPE_NAME |REVENUE_SUM
    '2024-01-01'   |123         |TRUE               |TRUE            |'ABC123'       |'Product 1'       |50
    '2024-01-01'   |123         |TRUE               |FALSE           |'ABC123'       |'Product 2'       |50
    '2024-01-01'   |123         |FALSE              |FALSE           |'ABC123'       |'Product 2'       |50
    '2024-01-01'   |987         |TRUE               |TRUE            |'DEF123'       |'Product 1'       |25
    '2024-01-01'   |987         |TRUE               |FALSE           |'DEF123'       |'Product 2'       |25
    '2024-01-01'   |987         |FALSE              |FALSE           |'DEF123'       |'Product 2'       |25

    {{% endcall %}}
{{% endcall %}}
```

Note how the model aggregates the expected REVENUE_SUM. Do your best to aggregate the expected data based on the SQL in the input. The goal is to create a model that is easy to read and hand validate.

When creating the mock data, follow these guidelines:

1. For boolean input columns, create enough rows that you can test both TRUE and FALSE values for all columns. For example, if there are 3 boolean columns, you would need six rows to test all combinations of TRUE and FALSE values.
2. For ID columns, use simple numbers. For example, 123, 456, 789, etc.
3. For name columns, try to identify when the name should be the same for a given ID. For example, if there are 3 rows with LOCATION_ID = 123, then the LOCATION_NAME should be the same for all three rows.
4. If a column ends in _at, it is either a date or a timestamp. If it is date, the column will end in _day_at. Timestamps will only end in _at. If the column is a date, use a date format like '2024-01-01'. If the column is a timestamp, use a timestamp format like '2024-01-01 00:00:00.000000000 -08:00'.
5. For numeric or dollar value columns, use simple numbers. For example, 10, 20.
6. Use a minimal number of rows needed to fully exercise the logic in the function. Try to sort dates and group by locations, names, or other similar common values.
7. You will need an `mock_ref` block for each DBT model in the input SQL. DBT models will be defined as either {{ ref('model_name') }} or {{ dbt_unit_testing.ref('model_name') }}.
8. Align the columns in the input and expected using tabs. You can use as many rows as needed.
9. Output the data in the same format as the example. Use as many `dbt_unit_testing.mock_ref` blocks as needed.
10. Use enough rows with variation that at least one aggregation can be created. For example, if the model groups by date and ID, you will need at least two rows with the same date and ID but different values for the columns being aggregated.
11. Location names are always three uppercase letters followed by three numbers. For example, "ABC123" or "DEF123". Network names are always the first three uppercase letters of the network name, like "ABC" or "DEF"
12. At the top of the file as in the example, add a --depends-on line for each moc_ref model used in the input SQL. Example, --depends-on: {{ ref('fct_appointments') }}
13. Encapsulate any string in single or date in single quotes. Even if the sample data has long strings, truncate to no more than 30 characters, preferably even less unless the logic requires something more.
14. Try to limit the date range in the input data to one or two days of time span, unless more is needed to fully test the logic of the model.
15. Do not include timezones in mockup data unless the sample data provided for that model includes timezones.
16. Do not include columns in the mock_ref blocks that are not used by the SQL model being tested.
17. All dates and strings must be enclosed in single quotes in the mock data.
Do not provide an explanation, only return the code for the test.
        """


# %%
