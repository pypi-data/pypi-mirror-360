import yaml
import sqlite3
import re


def read_yaml_file(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def get_database_config(databases, db_name):
    for db in databases:
        if db["name"] == db_name:
            return db
    raise ValueError(
        f"[ERROR] Database config for '{db_name}' not found in database.yaml."
    )


def execute_sqlite_query(db_path, query):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()
        return float(result[0]) if result and result[0] is not None else None
    except Exception as e:
        print(f"[ERROR] SQLite query failed on {db_path}: {e}")
        return None


def is_safe_query(query):
    # Remove leading spaces and brackets
    cleaned_query = query.strip().lower()
    # Match only queries that start with "select"
    return re.match(r"^\(*\s*select", cleaned_query) is not None


def process_database_queries(queries_file, databases_file):
    # Get queries from queries file
    queries_config = read_yaml_file(queries_file)
    # Get database from database file
    databases_config = read_yaml_file(databases_file)

    commands = queries_config.get("commands", [])
    databases = databases_config.get("databases", [])

    all_results = []

    for cmd in commands:
        try:
            db_conf = get_database_config(databases, cmd["database"])

            if db_conf["db_type"] != "sqlite":
                print(
                    f"[WARN] Unsupported database type: {db_conf['db_type']} in command {cmd['name']}"
                )
                continue

            db_path = db_conf["db_connection"]
            query = cmd["query"]
            labels = cmd.get('labels', [])
            label_values = cmd.get('label_values', [])
            main_label = cmd.get('main_label', 'default_db_metric')

            # check if query is safe
            if is_safe_query(query):
                value = execute_sqlite_query(db_path, query)
            else:
                print(f"[WARN] Unsupported query type: {query}")
                return None

            if not isinstance(label_values, list):
                label_values = [label_values]

            result = {
                'result': [{
                    'label': label_values,
                    'value': value
                }],
                'labels': labels,
                'main_label': main_label
            }
            all_results.append(result)
        except Exception as e:
            print(
                f"[ERROR] Processing command '{cmd.get('name', 'unknown')}' failed: {e}"
            )
    return all_results
