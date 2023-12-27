"""

Demo flask app for testing our Loadbalancer, loadbalancer will route requests to multiple backend servers running this app
"""
import os

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def sample():
    if request.method == "GET":
        return jsonify(
            message=f'This is the {os.environ["APP"]} application.',
            server=request.base_url,
            custom_header=request.headers.get("MyCustomHeader", None),
            host_header=request.headers.get("Host", request.base_url),
            custom_params=request.args.get("MyCustomParam", None),
            query_strings=request.query_string.decode("utf-8"),
            cookies=request.cookies if request.cookies else None,
        )
    else:
        return jsonify(
            message=f'This is the {os.environ["APP"]} application.',
            server=request.base_url,
            custom_header=request.headers.get("MyCustomHeader", None),
            host_header=request.headers.get("Host", request.base_url),
            custom_params=request.args.get("MyCustomParam", None),
            query_strings=request.query_string.decode("utf-8"),
            json_data=request.json if request.json else None,
            cookies=request.cookies if request.cookies else None,
        )


@app.route("/healthcheck")
def healthcheck():
    return "OK"


@app.route("/v1")
def v1():
    return "This is V1"


@app.route("/v2")
def v2():
    return "This is V2"


if __name__ == "__main__":
    app.run(host="0.0.0.0")
