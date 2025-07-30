from flask import Flask, request, jsonify, Response
from flexmetric.metric_process.expiring_queue import metric_queue
import argparse
from prometheus_client import generate_latest, REGISTRY, CONTENT_TYPE_LATEST

app = Flask(__name__)


@app.route('/metrics')
def metrics():
    return Response(generate_latest(REGISTRY), mimetype=CONTENT_TYPE_LATEST)


def add_update_metric_route():
    @app.route("/update_metric", methods=["POST"])
    def update_metric():
        try:
            data = request.get_json()

            # Validate top-level structure
            if not data or "result" not in data or "labels" not in data or "main_label" not in data:
                return jsonify({"status": "invalid structure"}), 400

            result = data["result"]
            labels = data["labels"]
            main_label = data["main_label"]

            # Validate types
            if not isinstance(result, list) or not isinstance(labels, list) or not isinstance(main_label, str):
                return jsonify({"status": "invalid types"}), 400

            for item in result:
                if "label" not in item or "value" not in item:
                    return jsonify({"status": "invalid result item"}), 400
                if not isinstance(item["label"], list):
                    return jsonify({"status": "label must be list"}), 400

                if len(item["label"]) != len(labels):
                    return jsonify({"status": "label count mismatch"}), 400

            # If everything is valid, queue the data
            metric_queue.put(data)
            print(metric_queue)

            return jsonify({"status": "success"}), 200

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500


def run_flask(host, port):
    app.run(host=host, port=port)
def secure_flask_run(args):
    app.run(host=args.host, port=args.port, ssl_context=(args.ssl_cert, args.ssl_key))