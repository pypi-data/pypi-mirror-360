# FlexMetric

FlexMetric is a lightweight, flexible, and extensible Prometheus exporter that allows you to securely expose system metrics, database query results, Python function outputs, and externally submitted metrics—via an optional Flask API with HTTPS support—as Prometheus-compatible metrics, all with minimal setup and maximum customization.

---

## Features

- Run shell commands and expose the results as Prometheus metrics.  
  ➔ **Harmful commands (e.g., file deletion, system shutdown) are blocked for safety.**
- Execute SQL queries (e.g., SQLite) and monitor database statistics.  
  ➔ **Potentially dangerous queries (e.g., `DROP`, `DELETE`, `TRUNCATE`) are not allowed.**
- Automatically discover and expose Python function outputs as metrics.
- Expose an optional **Flask API** (`/update_metric`) to receive external metrics dynamically.
- Modular and easy to extend—add your own custom integrations.
- Built-in Prometheus HTTP server (`/metrics`) with configurable port.
- **Supports HTTPS** to securely expose both metrics and API endpoints.
- **Input sanitization** is performed to ensure only safe commands and queries are executed.


---

## Installation

Install from PyPI:

```bash
pip install flexmetric
```
## Usage

Run FlexMetric from the command line:

```bash
flexmetric --commands --commands-config commands.yaml --port 8000
```

## Available Modes

FlexMetric supports multiple modes that can be used individually or combined to expose metrics:

| Mode            | Description                                                            | Required Configuration File(s)           |
|-----------------|------------------------------------------------------------------------|------------------------------------------|
| `--commands`     | Runs system commands and exports outputs as Prometheus metrics.         | `commands.yaml`                          |
| `--database`     | Executes SQL queries on databases and exports results.                 | `database.yaml` and `queries.yaml`       |
| `--functions`    | Discovers and runs user-defined Python functions and exports outputs.  | `executable_functions.txt`               |
| `--expose-api`   | Exposes a Flask API (`/update_metric`) to receive external metrics.     | *No configuration file required*         |
### Example of Using Multiple Modes Together

```bash
flexmetric --commands --commands-config commands.yaml --database --database-config database.yaml --queries-config queries.yaml
```

## Configuration File Examples

Below are example configurations for each supported mode.

## Using the Flask API in FlexMetric

To use the Flask API for submitting external metrics, you need to start the agent with the `--expose-api` flag along with the Flask host and port.

### Start FlexMetric with Flask API

```bash
flexmetric --expose-api --port <port> --host <host>
```

## Example: Running FlexMetric with Flask API

To run FlexMetric with both Prometheus metrics and the Flask API enabled:

```bash
flexmetric --expose-api --port 5000 --host 0.0.0.0
```

Prometheus metrics exposed at:
http://localhost:5000/metrics

Flask API exposed at:
http://localhost:5000/update_metric

### Submitting a Metric to the Flask API
```bash
curl -X POST http://localhost:5000/update_metric \
-H "Content-Type: application/json" \
-d '{
  "result": [
    { "label": "cpu_usage", "value": 42.5 }
  ],
  "labels": ["cpu"]
}'

```

### Using flex metrics in secure mode

```bash
flexmetric --port 5000 --host 0.0.0.0 --enable-https --ssl-cert=cert.pem --ssl-key=key.pem
```
Prometheus metrics exposed at:
https://localhost:5000/metrics

Flask API exposed at:
https://localhost:5000/update_metric

### Submitting a Metric to the Flask API
```bash
curl -k -X POST https://localhost:5000/update_metric \
-H "Content-Type: application/json" \
-d '{
  "result": [
    { "label": "cpu_usage", "value": 42.5 }
  ],
  "labels": ["cpu"]
}'

```

### commands.yaml

```yaml
commands:
  - name: disk_usage
    command: df -h
    main_label: disk_usage_filesystem_mount_point
    labels: ["filesystem", "mounted"]
    label_columns: [0, -1]
    value_column: 4
    timeout_seconds: 60
```
Example to select label_column and value_column

```bash
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   20G   28G  42% /
/dev/sdb1       100G   10G   85G  10% /data
```
## Fields description

| Field             | Description                                                                                                                |
|-------------------|----------------------------------------------------------------------------------------------------------------------------|
| `name`            | A **nickname** you give to this check. It's just for your reference to know what this command is doing (e.g., `"disk_usage"`). |
| `command`         | The **actual shell command** to run (e.g., `"df -h"`). It fetches the data you want to monitor.                             |
| `main_label`      | The **metric name** that will appear in Prometheus. This is what you will query to see the metric values.                  |
| `labels`          | A list of **label names** used to describe different dimensions of the metric (e.g., `["filesystem", "mounted"]`).         |
| `label_columns`   | A list of **column indexes** from the command’s output to extract the label values (e.g., `[0, -1]` for first and last column). |
| `value_column`    | The **column index** from the command's output to extract the **numeric value** (the actual metric value, e.g., disk usage). |
| `timeout_seconds` | Maximum time (in seconds) to wait for the command to complete. If it exceeds this time, the command is aborted.             |

## Database mode

```yaml
databases:
  - name: mydb
    db_type: sqlite
    db_connection: /path/to/my.db
````
```yaml
commands:
  - name: user_count
    database: userdb
    query: "SELECT COUNT(*) FROM users;"
    main_label: database_user_count
    labels: ["database_name", "table_name"]
    label_values: ["userdb", "users"]
```
## Functions mode

executable_functions.txt 
```
function_name_1
function_name_2
```

## Python Function Output Format

When using the `--functions` mode, each Python function you define is expected to return a dictionary in the following format:

```python
{
    'result': [
        { 'label': [label_value1, label_value2, ...], 'value': numeric_value }
    ],
    'labels': [label_name1, label_name2, ...],
    'main_label': 'your_main_metric_name'
}
```

### Explanation:

| Key     | Description                                                               |
|--------|---------------------------------------------------------------------------|
| `result` | A list of dictionaries, each containing a `label` and a corresponding numeric `value`. |
| `labels` | A list of label names (used as Prometheus labels).                        |


## Command-Line Options

The following command-line options are available when running FlexMetric:

| Option              | Description                                              | Default                    |
|---------------------|----------------------------------------------------------|----------------------------|
| `--port`             | Port for the Prometheus metrics server (`/metrics`)      | `8000`                     |
| `--commands`         | Enable commands mode                                      |                            |
| `--commands-config`  | Path to commands YAML file                                | `commands.yaml`            |
| `--database`         | Enable database mode                                      |                            |
| `--database-config`  | Path to database YAML file                                | `database.yaml`            |
| `--queries-config`   | Path to queries YAML file                                 | `queries.yaml`             |
| `--functions`        | Enable Python functions mode                              |                            |
| `--functions-file`   | Path to functions file                                    | `executable_functions.txt` |
| `--expose-api`       | Enable Flask API mode to receive external metrics         |                            |
| `--flask-port`       | Port for the Flask API (`/update_metric`)                 | `5000`                     |
| `--flask-host`       | Hostname for the Flask API                                | `0.0.0.0`                  |
| `--enable-https`     | Enable HTTPS for the Flask API                            |                            |
| `--ssl-cert`         | Path to SSL certificate file (`cert.pem`)                 |                            |
| `--ssl-key`          | Path to SSL private key file (`key.pem`)                  |                            |

### Example Command:

```bash
flexmetric --commands --commands-config commands.yaml --port 8000
```
## Example Prometheus Output

Once FlexMetric is running, the `/metrics` endpoint will expose metrics in the Prometheus format.

Example output:
```bash
disk_usage_gauge{path="/"} 45.0
```

Each metric includes labels and numeric values that Prometheus can scrape and visualize.

---

## Future Enhancements

The following features are planned or under consideration to improve FlexMetric:

- Support for additional databases such as PostgreSQL and MySQL.
- Enhanced support for more complex scripts and richer label extraction.