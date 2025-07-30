# `cdbt` - Cold Bore Capital Data Build Tools Helper
This is a command line tool created for Cold Bore Capitals data development team. It was only developed as an internal tool, not designed for public use, however anyone is welcome to use it. Please understand that this tool is not polished, and is highly specialized for the Cold Bore Capital workflow.

`cdbt` is a CLI (Command Line Interface) tool developed to enhance and manage DBT (Data Build Tool) builds, particularly focusing on state management and build optimizations. It provides functionalities to refresh, select, and test models efficiently, adding enhancements like conditional child or parent builds directly from the command line.

## Features
- **Full Refresh Control:** Toggle full refreshes on all models.
- **Selective Model Builds:** Use the DBT-style select strings to run specific models.
- **Failure Handling:** Customizable behavior on failures including fast failing options.
- **State Based Builds:** Enhanced state management for efficient DBT runs.
- **Real-Time Output:** Stream output in real-time for better monitoring.
- **Dynamic Build Commands:** Automatically include child or parent dependencies with flexible depth control.
- **AI-powered Documentation and Testing:** Automatically generate or update DBT YML files and unit test mock data.

## Installation

To install `cdbt` with pip, run the following command in your terminal:

```bash
pip install mdbt
```

To use the AI docs and unit test features, you need an `.env` file in the root of your project configured with the following:

```bash
OPENAI_API_KEY=<openai api key>
DATACOVES__MAIN__ACCOUNT=<snowflake account>
DATACOVES__MAIN__PASSWORD=<snowflake password>
DATACOVES__MAIN__ROLE=<snowflake role>
DATACOVES__MAIN__SCHEMA=<snowflake schema>
DATACOVES__MAIN__USER=<snowflake user>
DATACOVES__MAIN__WAREHOUSE=<snowflake warehouse>
```

Ensure that you have Python 3.8 or higher installed, as it is required for `cdbt` to function properly.

## Basic DBT Shadowed Commands
These commands act as a pass-through to DBT and are provided for convenience. They are not the primary focus of `cdbt`.

- `cdbt run`
- `cdbt test`
- `cdbt build`

## `trun` Run and Test Only

This command runs the `run` and `test` commands in sequence. It is useful for running both commands in a single step, without executing a snapshot and seed.

```bash
mdbt trun --select my_model
```

## `unittest` - Run the DBT Unit Tests

Executes the unit tests for selected or all models.

```bash
mdbt unittest --select my_model
```

## `clip-compile` Compile to Clipboard
`clip-compile` will compile the selected model and copy the SQL to the clipboard. This is useful for quickly copying the SQL to run in console.

Usage:

```bash
mdbt clip-compile --select my_model
```

## State Build Commands

### Important Notes

#### Auto Full Refresh

Both the `sbuild` and `pbuild` commands will scan the models to be built and automatically initiate a full refresh if an incrementally materialized model is found in the list (as per `dbt ls`). If you wish to force a `--full-refresh` for other reasons such as a column being added to a seed, add the `--full-refresh` flag.

#### State Build Commands with Parent and Child Modifiers

Both the `sbuild` and `pbuild` commands can include modifications to build parent or child dependencies by appending a `+` and an optional integer to the command.

- `+` or `+<number>` at the end of the command includes child dependencies up to the specified depth.
- `+<number>` at the beginning of the command includes parent dependencies up to the specified depth.

Example:

- `cdbt pbuild+` and `cdbt pbuild+3` will build all state based variance models along with all child models up to 3 levels deep, respectively.
- `cdbt 3+pbuild` will include parent models up to 3 levels up in the build.

### Production Build `pbuild`
This command initiates a state-based build based on the manifest.json file associated with the master branch. This will use the DBT macro provided by Datacoves `get_last_artifacts` to pull the artifacts from the Snowflake file stage and save to the `./logs` folder. Then comparison is made against this file. This file is updated during the production deployment CI process.

```bash
mdbt pbuild
```

### Local State Build `sbuild`
Initiates a production state build.

**Error Handling:**

If an error occurs during an `sbuild` operation, the manifest file copied to the `_artifacts` location will be moved back to `target`. This avoids an issue where after executing a state-based build with a failure, the next build will not properly compare the state of the models.

```bash
mdbt sbuild
```

## Git-based Build `gbuild`
This command builds models based on Git changes from production to the current branch.

```bash
mdbt gbuild
```

## AI DBT Docs Build
The command `cdbt build-docs --select model_name` will automatically build or update the DBT YML file for a selected model.

```bash
mdbt build-docs --select my_model
```

## AI Build DBT Unit Test Mock Data
The command `cdbt build-unit --select model_name` will automatically build or update the DBT YML file for a selected model.

```bash
mdbt build-unit --select my_model
```

## Additional Commands

### `lightdash`
Start a Lightdash preview for a model or all models.

```bash
mdbt lightdash --name preview_name --select model_name
```

### `format`
Format models using sqlfluff.

```bash
mdbt format --select model_name
```

### `clean-stg`
Clean files in the L1_stg folders.

```bash
mdbt clean-stg --select model_name
```

### `clean-clip`
Clean and sort a series of select statements from your clipboard and put back to clipboard.

```bash
mdbt clean-clip
```

### `pop-yaml`
Build the YAML PoP macro columns for a given model targeted in the select statement.

```bash
mdbt pop-yaml --select model_name
```

### `ma-yaml`
Build the YAML Moving Average macro columns for a given model targeted in the select statement.

```bash
mdbt ma-yaml --select model_name
```

### `pre-commit`
Run pre-commit hooks.

```bash
mdbt pre-commit
```

## License
Copyright 2024 Cold Bore Capital

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
