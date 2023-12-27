import requests
from flask import Flask, request

from .utils import (get_healthy_server, healthcheck, load_configuration,
                    process_firewall_rules_flag, process_multiple_rules,
                    process_rewrite_rules, transform_backends_from_config)

loadbalancer = Flask(__name__)

config = load_configuration("load_balancer/loadbalancer.yaml")
register = transform_backends_from_config(config)


@loadbalancer.route("/", methods=["GET", "POST"])
@loadbalancer.route("/<path>")
def router(path="/"):
    updated_register = healthcheck(register)
    host_header = request.headers["Host"]
    if not process_firewall_rules_flag(
        config, host_header, request.environ["REMOTE_ADDR"], f"/{path}"
    ):
        return "Forbidden", 403

    for entry in config["hosts"]:
        if host_header == entry["host"]:
            healthy_server = get_healthy_server(entry["host"], updated_register)
            if not healthy_server:
                return "No backend servers available.", 503
            try:
                json_body = request.get_json(force=True)
            except Exception:
                json_body = None
            result = process_multiple_rules(
                config=config,
                host=host_header,
                headers=request.headers,
                param_args=request.args,
                cookies=request.cookies,
                json_body=json_body,
            )
            rewrite_path = ""
            if path == "v1":
                rewrite_path = process_rewrite_rules(config, host_header, path)
            healthy_server.open_connections += 1
            if request.method == "GET":
                response = requests.get(
                    f"http://{healthy_server.endpoint}/{rewrite_path}",
                    headers=result["headers"],
                    params=result["params"],
                    cookies=result["cookies"],
                )

            else:
                response = requests.post(
                    f"http://{healthy_server.endpoint}",
                    headers=result["headers"],
                    params=result["params"],
                    json=result["json_body"],
                    cookies=result["cookies"],
                )

            healthy_server.open_connections -= 1
            return response.content, response.status_code
    for entry in config["paths"]:
        if ("/" + path) == entry["path"]:
            healthy_server = get_healthy_server(entry["path"], updated_register)
            if not healthy_server:
                return "No backend servers available.", 503
            healthy_server.open_connections += 1

            response = requests.get(f"http://{healthy_server.endpoint}")
            healthy_server.open_connections -= 1
            return response.content, response.status_code

    return "Not Found", 404
