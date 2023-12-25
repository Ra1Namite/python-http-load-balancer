
import requests
from flask import Flask, request

from utils import (get_healthy_server, healthcheck, load_configuration,
                   process_rules, transform_backends_from_config)

loadbalancer = Flask(__name__)

config = load_configuration("loadbalancer.yaml")
register = transform_backends_from_config(config)


@loadbalancer.route("/")
@loadbalancer.route("/<path>")
def router(path="/"):
    updated_register = healthcheck(register)
    host_header = request.headers["Host"]
    for entry in config["hosts"]:
        if host_header == entry["host"]:
            healthy_server = get_healthy_server(entry["host"], updated_register)
            if not healthy_server:
                return "No backend servers available.", 503
            headers = process_rules(
                config,
                host_header,
                {k: v for k, v in request.headers.items()},
                "header",
            )
            params = process_rules(
                config, host_header, {k: v for k, v in request.args.items()}, "param"
            )

            response = requests.get(
                f"http://{healthy_server.endpoint}", headers=headers, params=params
            )
            return response.content, response.status_code
    for entry in config["paths"]:
        if ("/" + path) == entry["path"]:
            healthy_server = get_healthy_server(entry["path"], updated_register)
            if not healthy_server:
                return "No backend servers available.", 503

            response = requests.get(f"http://{healthy_server.endpoint}")
            return response.content, response.status_code

    return "Not Found", 404
