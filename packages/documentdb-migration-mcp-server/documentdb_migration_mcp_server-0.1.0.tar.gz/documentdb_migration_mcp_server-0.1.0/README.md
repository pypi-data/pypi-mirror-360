# DocumentDB Migration MCP Server

This MCP (Model Context Protocol) server provides tools for migrating data to DocumentDB. It wraps the existing DocumentDB migration tools into an MCP server interface, making them accessible through the MCP protocol.

## Features

- **Full Load Migration**: Migrate data from a source database to DocumentDB in a one-time operation
- **Filtered Full Load Migration**: Migrate data with filtering based on TTL
- **Change Data Capture (CDC)**: Continuously replicate changes from a source database to DocumentDB
- **Resume Token Management**: Get change stream resume tokens for CDC operations

## Installation

### Using uvx

```bash
uvx documentdb-migration-mcp-server@latest
```

### Using the installation script

```bash
./install.sh
```

## MCP Tools

### runFullLoad

Run a full load migration from source to target.

**Parameters:**
- `source_uri`: Source URI in MongoDB Connection String format
- `target_uri`: Target URI in MongoDB Connection String format
- `source_namespace`: Source Namespace as <database>.<collection>
- `target_namespace`: (Optional) Target Namespace as <database>.<collection>, defaults to source_namespace
- `boundaries`: Comma-separated list of boundaries for segmenting
- `boundary_datatype`: Datatype of boundaries (objectid, string, int)
- `max_inserts_per_batch`: Maximum number of inserts to include in a single batch
- `feedback_seconds`: Number of seconds between feedback output
- `dry_run`: Read source changes only, do not apply to target
- `verbose`: Enable verbose logging
- `create_cloudwatch_metrics`: Create CloudWatch metrics for monitoring
- `cluster_name`: Name of cluster for CloudWatch metrics

### runFilteredFullLoad

Run a filtered full load migration from source to target.

**Parameters:**
- `source_uri`: Source URI in MongoDB Connection String format
- `target_uri`: Target URI in MongoDB Connection String format
- `source_namespace`: Source Namespace as <database>.<collection>
- `target_namespace`: (Optional) Target Namespace as <database>.<collection>, defaults to source_namespace
- `boundaries`: Comma-separated list of boundaries for segmenting
- `boundary_datatype`: Datatype of boundaries (objectid, string, int)
- `max_inserts_per_batch`: Maximum number of inserts to include in a single batch
- `feedback_seconds`: Number of seconds between feedback output
- `dry_run`: Read source changes only, do not apply to target
- `verbose`: Enable verbose logging

### runCDC

Run a CDC (Change Data Capture) migration from source to target.

**Parameters:**
- `source_uri`: Source URI in MongoDB Connection String format
- `target_uri`: Target URI in MongoDB Connection String format
- `source_namespace`: Source Namespace as <database>.<collection>
- `target_namespace`: (Optional) Target Namespace as <database>.<collection>, defaults to source_namespace
- `start_position`: Starting position - 0 for all available changes, YYYY-MM-DD+HH:MM:SS in UTC, or change stream resume token
- `use_oplog`: Use the oplog as change data capture source (MongoDB only)
- `use_change_stream`: Use change streams as change data capture source (MongoDB or DocumentDB)
- `threads`: Number of threads (parallel processing)
- `duration_seconds`: Number of seconds to run before exiting, 0 = run forever
- `max_operations_per_batch`: Maximum number of operations to include in a single batch
- `max_seconds_between_batches`: Maximum number of seconds to await full batch
- `feedback_seconds`: Number of seconds between feedback output
- `dry_run`: Read source changes only, do not apply to target
- `verbose`: Enable verbose logging
- `create_cloudwatch_metrics`: Create CloudWatch metrics for monitoring
- `cluster_name`: Name of cluster for CloudWatch metrics

### getResumeToken

Get the current change stream resume token.

**Parameters:**
- `source_uri`: Source URI in MongoDB Connection String format
- `source_namespace`: Source Namespace as <database>.<collection>

## Requirements

- Python 3.10+
- PyMongo
- Boto3 (for CloudWatch metrics)
- MCP Server

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
