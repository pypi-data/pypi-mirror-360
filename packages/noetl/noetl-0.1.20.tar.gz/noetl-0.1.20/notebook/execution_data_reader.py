#!/usr/bin/env python3
"""
NoETL Execution Data Reader

This script demonstrates how to read and analyze the execution data exported from NoETL agent runs.
The data is stored in a Parquet file at ./data/exports/execution_data.parquet.

Usage:
    python execution_data_reader.py [options]

Options:
    --input PATH         Path to the input Parquet file (default: ./data/exports/execution_data.parquet)
    --output-dir PATH    Directory to save output files (default: ./data/exports)
    --filter FILTER      SQL WHERE clause to filter events (e.g. "event_type = 'step_result'")
    --verbose            Enable verbose output
    --quiet              Suppress all output except errors
    --list-events        List all event types in the file and exit
    --list-steps         List all steps in the file and exit
    --format FORMAT      Output format for tables (text, csv, json) (default: text)
    --no-plots           Disable plot generation even if matplotlib is available
    --help               Show this help message and exit

Examples:
    python execution_data_reader.py --input ./my_data.parquet --output-dir ./analysis
    python execution_data_reader.py --filter "status = 'success'"
    python execution_data_reader.py --list-events
    python execution_data_reader.py --format json

Requirements:
    - duckdb
    - pandas
    - matplotlib (optional, for visualization)
"""

import duckdb
import pandas as pd
import json
import os
import sys
import argparse
from pathlib import Path

# Try to import matplotlib for visualization
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Matplotlib not available. Visualizations will be skipped.")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="NoETL Execution Data Reader",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--input", 
        default=None,
        help="Path to the input Parquet file (default: ./data/exports/execution_data.parquet)"
    )

    parser.add_argument(
        "--output-dir", 
        default=None,
        help="Directory to save output files (default: ./data/exports)"
    )

    parser.add_argument(
        "--filter", 
        default=None,
        help="SQL WHERE clause to filter events (e.g. \"event_type = 'step_result'\")"
    )

    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--quiet", 
        action="store_true",
        help="Suppress all output except errors"
    )

    parser.add_argument(
        "--list-events", 
        action="store_true",
        help="List all event types in the file and exit"
    )

    parser.add_argument(
        "--list-steps", 
        action="store_true",
        help="List all steps in the file and exit"
    )

    parser.add_argument(
        "--format", 
        choices=["text", "csv", "json"],
        default="text",
        help="Output format for tables (text, csv, json) (default: text)"
    )

    parser.add_argument(
        "--no-plots", 
        action="store_true",
        help="Disable plot generation even if matplotlib is available"
    )

    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_args()

    # Set up logging based on verbosity
    verbose = args.verbose
    quiet = args.quiet

    def log(message, level="INFO"):
        """Log a message based on verbosity settings."""
        if quiet and level != "ERROR":
            return
        if not verbose and level == "DEBUG":
            return
        print(f"[{level}] {message}")

    # Set the path to the execution data Parquet file
    script_dir = Path(__file__).parent

    if args.input:
        parquet_file = Path(args.input)
    else:
        parquet_file = script_dir.parent / "data" / "exports" / "execution_data.parquet"

    # Set the output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = script_dir.parent / "data" / "exports"

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if the file exists
    if not parquet_file.exists():
        log(f"Error: File {parquet_file} not found.", "ERROR")
        log("Please run the NoETL agent with the --export option first.", "ERROR")
        log("Example: python noetl/agent/agent.py -f ./catalog/playbooks/weather_example.yaml --export ./data/exports/execution_data.parquet", "ERROR")
        return 1

    log(f"Found execution data file: {parquet_file}")

    # Connect to an in-memory DuckDB database
    con = duckdb.connect(":memory:")

    # Read the Parquet file into a DuckDB table
    con.execute(f"CREATE TABLE event_log AS SELECT * FROM read_parquet('{parquet_file}')")

    # Apply filter if provided
    if args.filter:
        log(f"Applying filter: WHERE {args.filter}", "DEBUG")
        con.execute(f"CREATE TABLE filtered_log AS SELECT * FROM event_log WHERE {args.filter}")
        con.execute("DROP TABLE event_log")
        con.execute("ALTER TABLE filtered_log RENAME TO event_log")

    # Handle special commands
    if args.list_events:
        event_types = con.execute("SELECT DISTINCT event_type, COUNT(*) as count FROM event_log GROUP BY event_type ORDER BY count DESC").fetchdf()
        if args.format == "text":
            log("\nEvent types in the execution data:")
            log(str(event_types))
        elif args.format == "csv":
            output_file = output_dir / "event_types.csv"
            event_types.to_csv(output_file, index=False)
            log(f"Event types exported to: {output_file}")
        elif args.format == "json":
            output_file = output_dir / "event_types.json"
            event_types.to_json(output_file, orient="records", indent=2)
            log(f"Event types exported to: {output_file}")
        return 0

    if args.list_steps:
        steps = con.execute("""
            SELECT DISTINCT node_name, node_type, COUNT(*) as event_count
            FROM event_log
            WHERE node_name IS NOT NULL
            GROUP BY node_name, node_type
            ORDER BY event_count DESC
        """).fetchdf()
        if args.format == "text":
            log("\nSteps in the execution data:")
            log(str(steps))
        elif args.format == "csv":
            output_file = output_dir / "steps.csv"
            steps.to_csv(output_file, index=False)
            log(f"Steps exported to: {output_file}")
        elif args.format == "json":
            output_file = output_dir / "steps.json"
            steps.to_json(output_file, orient="records", indent=2)
            log(f"Steps exported to: {output_file}")
        return 0

    # Get the schema of the table
    schema = con.execute("DESCRIBE event_log").fetchall()
    log("\nSchema of the event_log table:")
    for column in schema:
        log(f"- {column[0]}: {column[1]}")

    # Get the execution ID
    execution_id = con.execute("SELECT DISTINCT execution_id FROM event_log").fetchone()[0]
    log(f"\nExecution ID: {execution_id}")

    # Count the number of events by type
    event_counts = con.execute("""
        SELECT event_type, COUNT(*) as count
        FROM event_log
        GROUP BY event_type
        ORDER BY count DESC
    """).fetchdf()

    log("\nEvent counts by type:")
    if args.format == "text":
        log(str(event_counts))
    elif args.format == "csv":
        output_file = output_dir / "event_counts.csv"
        event_counts.to_csv(output_file, index=False)
        log(f"Event counts exported to: {output_file}")
    elif args.format == "json":
        output_file = output_dir / "event_counts.json"
        event_counts.to_json(output_file, orient="records", indent=2)
        log(f"Event counts exported to: {output_file}")

    # Get the execution timeline
    timeline = con.execute("""
        SELECT 
            event_type,
            node_name,
            status,
            timestamp,
            duration
        FROM event_log
        ORDER BY timestamp
        LIMIT 10
    """).fetchdf()

    log("\nExecution timeline (first 10 events):")
    if args.format == "text":
        log(str(timeline))
    elif args.format == "csv":
        output_file = output_dir / "timeline.csv"
        timeline.to_csv(output_file, index=False)
        log(f"Timeline exported to: {output_file}")
    elif args.format == "json":
        output_file = output_dir / "timeline.json"
        timeline.to_json(output_file, orient="records", indent=2)
        log(f"Timeline exported to: {output_file}")

    # Get step durations
    step_durations = con.execute("""
        SELECT 
            node_name,
            AVG(duration) as avg_duration,
            MIN(duration) as min_duration,
            MAX(duration) as max_duration,
            COUNT(*) as count
        FROM event_log
        WHERE event_type = 'step_result'
        GROUP BY node_name
        ORDER BY avg_duration DESC
    """).fetchdf()

    log("\nStep durations (in seconds):")
    if args.format == "text":
        log(str(step_durations))
    elif args.format == "csv":
        output_file = output_dir / "step_durations.csv"
        step_durations.to_csv(output_file, index=False)
        log(f"Step durations exported to: {output_file}")
    elif args.format == "json":
        output_file = output_dir / "step_durations.json"
        step_durations.to_json(output_file, orient="records", indent=2)
        log(f"Step durations exported to: {output_file}")

    # Visualize step durations if matplotlib is available
    if HAS_MATPLOTLIB and not step_durations.empty and not args.no_plots:
        plt.figure(figsize=(12, 6))
        plt.barh(step_durations['node_name'], step_durations['avg_duration'])
        plt.xlabel('Average Duration (seconds)')
        plt.ylabel('Step Name')
        plt.title('Average Step Execution Duration')
        plt.tight_layout()

        # Save the plot to a file
        plot_file = output_dir / "step_durations.png"
        plt.savefig(plot_file)
        log(f"\nStep duration plot saved to: {plot_file}")

        # Create a timeline plot
        if 'timestamp' in con.execute("DESCRIBE event_log").fetchdf()['column_name'].values:
            try:
                timeline_data = con.execute("""
                    SELECT 
                        event_type,
                        node_name,
                        timestamp,
                        duration
                    FROM event_log
                    WHERE event_type IN ('step_start', 'step_result')
                    ORDER BY timestamp
                """).fetchdf()

                if not timeline_data.empty:
                    plt.figure(figsize=(15, 8))

                    # Convert timestamp to datetime if it's a string
                    if isinstance(timeline_data['timestamp'].iloc[0], str):
                        timeline_data['timestamp'] = pd.to_datetime(timeline_data['timestamp'])

                    # Create a timeline plot
                    for event_type in ['step_start', 'step_result']:
                        subset = timeline_data[timeline_data['event_type'] == event_type]
                        if not subset.empty:
                            plt.scatter(
                                subset['timestamp'], 
                                subset['node_name'],
                                label=event_type,
                                alpha=0.7,
                                s=100
                            )

                    plt.xlabel('Time')
                    plt.ylabel('Step Name')
                    plt.title('Execution Timeline')
                    plt.legend()
                    plt.grid(True, linestyle='--', alpha=0.7)
                    plt.tight_layout()

                    # Save the plot to a file
                    timeline_plot_file = output_dir / "execution_timeline.png"
                    plt.savefig(timeline_plot_file)
                    log(f"\nExecution timeline plot saved to: {timeline_plot_file}")
            except Exception as e:
                log(f"Error creating timeline plot: {e}", "ERROR")

    # Get step results
    step_results = con.execute("""
        SELECT 
            node_name,
            status,
            output_result
        FROM event_log
        WHERE event_type = 'step_result'
        ORDER BY timestamp
    """).fetchdf()

    # Function to parse JSON strings
    def parse_json(json_str):
        if json_str and isinstance(json_str, str):
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return json_str
        return json_str

    # Parse output results
    step_results['parsed_output'] = step_results['output_result'].apply(parse_json)

    log("\nStep results:")
    if not quiet:
        for idx, row in step_results.iterrows():
            log(f"\nStep: {row['node_name']}")
            log(f"Status: {row['status']}")
            log(f"Output: {row['parsed_output']}")

    # Export step results
    if args.format == "csv":
        output_file = output_dir / "step_results.csv"
        # We can't easily save the parsed_output column to CSV, so we'll use the original
        step_results[['node_name', 'status', 'output_result']].to_csv(output_file, index=False)
        log(f"Step results exported to: {output_file}")
    elif args.format == "json":
        output_file = output_dir / "step_results.json"
        # For JSON, we can include the parsed output
        result_data = []
        for idx, row in step_results.iterrows():
            result_data.append({
                "node_name": row['node_name'],
                "status": row['status'],
                "output": row['parsed_output']
            })
        with open(output_file, 'w') as f:
            json.dump(result_data, f, indent=2, default=str)
        log(f"Step results exported to: {output_file}")

    # Find all errors in the execution
    errors = con.execute("""
        SELECT 
            event_type,
            node_name,
            timestamp,
            error
        FROM event_log
        WHERE status = 'error' OR error IS NOT NULL
        ORDER BY timestamp
    """).fetchdf()

    if errors.empty:
        log("\nNo errors found in the execution.")
    else:
        log("\nErrors found in the execution:")
        if args.format == "text":
            log(str(errors))
        elif args.format == "csv":
            output_file = output_dir / "errors.csv"
            errors.to_csv(output_file, index=False)
            log(f"Errors exported to: {output_file}")
        elif args.format == "json":
            output_file = output_dir / "errors.json"
            errors.to_json(output_file, orient="records", indent=2)
            log(f"Errors exported to: {output_file}")

    # Export execution summary
    summary = con.execute("""
        SELECT 
            (SELECT COUNT(*) FROM event_log) as total_events,
            (SELECT COUNT(DISTINCT node_name) FROM event_log WHERE event_type = 'step_start') as total_steps,
            (SELECT MIN(timestamp) FROM event_log) as start_time,
            (SELECT MAX(timestamp) FROM event_log) as end_time,
            (SELECT COUNT(*) FROM event_log WHERE status = 'error') as error_count
    """).fetchdf()

    log("\nExecution Summary:")
    if args.format == "text":
        log(str(summary))
    elif args.format == "csv":
        output_file = output_dir / "summary.csv"
        summary.to_csv(output_file, index=False)
        log(f"Summary exported to: {output_file}")
    elif args.format == "json":
        output_file = output_dir / "summary.json"
        summary.to_json(output_file, orient="records", indent=2)
        log(f"Summary exported to: {output_file}")

    # Create a comprehensive report file
    report_file = output_dir / "execution_report.md"
    with open(report_file, 'w') as f:
        f.write(f"# NoETL Execution Report\n\n")
        f.write(f"## Execution Summary\n\n")
        f.write(f"- **Execution ID**: {execution_id}\n")
        f.write(f"- **Start Time**: {summary['start_time'].iloc[0]}\n")
        f.write(f"- **End Time**: {summary['end_time'].iloc[0]}\n")
        f.write(f"- **Total Events**: {summary['total_events'].iloc[0]}\n")
        f.write(f"- **Total Steps**: {summary['total_steps'].iloc[0]}\n")
        f.write(f"- **Error Count**: {summary['error_count'].iloc[0]}\n\n")

        f.write(f"## Event Counts\n\n")
        f.write("| Event Type | Count |\n")
        f.write("| ---------- | ----- |\n")
        for idx, row in event_counts.iterrows():
            f.write(f"| {row['event_type']} | {row['count']} |\n")
        f.write("\n")

        f.write(f"## Step Durations\n\n")
        f.write("| Step Name | Avg Duration (s) | Min Duration (s) | Max Duration (s) | Count |\n")
        f.write("| --------- | ---------------- | ---------------- | ---------------- | ----- |\n")
        for idx, row in step_durations.iterrows():
            f.write(f"| {row['node_name']} | {row['avg_duration']:.4f} | {row['min_duration']:.4f} | {row['max_duration']:.4f} | {row['count']} |\n")
        f.write("\n")

        if not errors.empty:
            f.write(f"## Errors\n\n")
            f.write("| Event Type | Node Name | Timestamp | Error |\n")
            f.write("| ---------- | --------- | --------- | ----- |\n")
            for idx, row in errors.iterrows():
                f.write(f"| {row['event_type']} | {row['node_name']} | {row['timestamp']} | {row['error']} |\n")
            f.write("\n")

        f.write(f"## Generated Files\n\n")
        for file in output_dir.glob("*"):
            if file.name != "execution_report.md" and file.is_file():
                f.write(f"- [{file.name}]({file.name})\n")

    log(f"\nComprehensive report saved to: {report_file}")
    log("\nAnalysis complete!")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
