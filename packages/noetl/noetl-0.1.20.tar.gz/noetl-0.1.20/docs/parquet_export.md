# Parquet Export in NoETL

This document explains how the NoETL agent exports execution data to Parquet files and how to properly read these files.

## Overview

The NoETL agent can export execution data to Parquet files for later analysis. This data includes:
- Step execution details
- Input and output data for each step
- Execution times
- Error information (if any)

## Exporting Execution Data

To export execution data, use the `--export` option when running the agent:

```bash
python noetl/agent/agent007.py -f ./catalog/playbooks/weather_example.yaml --export ./data/exports/execution_data.parquet
```

This will run the playbook and export the execution data to the specified Parquet file.

## Reading Execution Data

You can read the exported Parquet file using various tools:

### Using DuckDB

```python
import duckdb

# Connect to an in-memory DuckDB database
con = duckdb.connect(":memory:")

# Read the Parquet file
df = con.execute("SELECT * FROM read_parquet('./data/exports/execution_data.parquet')").fetchdf()

# Print the first few rows
print(df.head())
```

### Using Polars

```python
import polars as pl

# Read the Parquet file
df = pl.read_parquet("./data/exports/execution_data.parquet")

# Print the first few rows
print(df.head())
```

### Using the Execution Data Reader

The project includes a script to analyze execution data:

```bash
python notebook/execution_data_reader.py --input ./data/exports/execution_data.parquet
```

## Troubleshooting

If you encounter issues reading the Parquet file, try the following:

1. **Check file permissions**: Ensure you have read permissions for the file.
2. **Check file existence**: Verify that the file exists at the specified path.
3. **Check file integrity**: If the file is corrupted, try re-running the agent with the `--export` option.
4. **Check dependencies**: Ensure you have the required dependencies installed:
   - duckdb
   - polars
   - pyarrow

### Common Errors

#### "No magic bytes found at end of file"

This error indicates that the Parquet file is corrupted or was not properly written. This can happen if:
- The agent process was terminated before the file was completely written
- There was an error during the writing process
- The disk ran out of space

**Solution**: Re-run the agent with the `--export` option to generate a new Parquet file.

#### "File not found"

This error indicates that the file does not exist at the specified path.

**Solution**: Check the path and ensure the file exists. If not, re-run the agent with the `--export` option.

## Implementation Details

The NoETL agent uses the following approach to export execution data:

1. Retrieves data from the event_log table using DuckDB
2. Converts it to a Polars DataFrame
3. Writes the DataFrame to a Parquet file using Polars' `write_parquet` method with:
   - "snappy" compression for better compatibility
   - PyArrow backend for better reliability
4. Verifies that the file was written correctly

The export process includes comprehensive error handling to ensure that corrupted files are not left behind if an error occurs.