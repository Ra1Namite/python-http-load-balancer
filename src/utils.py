import yaml

from src.models import Server


def load_configuration(path):
    with open(path) as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    return config


def transform_backends_from_config(config):
    register = {}
    for entry in config.get("hosts", []):
        register.update(
            {entry["host"]: [Server(endpoint) for endpoint in entry["servers"]]}
        )
    for entry in config.get("paths", []):
        register.update(
            {entry["path"]: [Server(endpoint) for endpoint in entry["servers"]]}
        )
    return register


def get_healthy_server(host, register):
    return least_connections([server for server in register[host] if server.healthy])


def healthcheck(register):
    for host in register:
        for server in register[host]:
            server.healthcheck_and_update_status()
    return register


def process_rules(config, host, rules, modify):
    """
    manipulate headers, query parameters, post data, cookies
    """
    modify_options = {
        "header": "header_rules",
        "param": "param_rules",
        "json_data": "json_data_rules",
        "cookie": "cookie_rules",
    }

    matched_entry = None
    for entry in config.get("hosts", []):
        if host == entry["host"]:
            matched_entry = entry
            break
    if matched_entry is None:
        return rules
    header_rules = matched_entry.get(modify_options[modify], {})
    for instruction, modify_headers in header_rules.items():
        if instruction == "add":
            rules.update(modify_headers)
        if instruction == "remove":
            for key in modify_headers.keys():
                if key in rules:
                    rules.pop(key)

    return rules


def process_multiple_rules(config, host, headers, param_args, cookies, json_body=None):
    """
    process multiple fields at same time
    """
    headers = process_rules(config, host, {k: v for k, v in headers.items()}, "header")
    params = process_rules(config, host, {k: v for k, v in param_args.items()}, "param")
    cookies = process_rules(config, host, {k: v for k, v in cookies.items()}, "cookie")
    if json_body:
        json_body = process_rules(config, host, json_body, "json_data")
    return {
        "headers": headers,
        "params": params,
        "cookies": cookies,
        "json_body": json_body,
    }


def process_rewrite_rules(config, host, path):
    """
    manipulate urls
    """
    for entry in config.get("hosts", []):
        if host == entry["host"]:
            rewrite_rules = entry.get("rewrite_rules", {})
            for current_path, new_path in rewrite_rules["replace"].items():
                return path.replace(current_path, new_path)


def least_connections(servers):
    """
    least connection load balancing algorithm
    """
    if not servers:
        return None
    return min(servers, key=lambda x: x.open_connections)


def process_firewall_rules_flag(config, host, client_ip=None, path=None):
    """
    process firewall rules
    """
    for entry in config.get("hosts", []):
        if host == entry["host"]:
            firewall_rules = entry.get("firewall_rules", {})
            if client_ip in firewall_rules.get("ip_reject", []):
                return False
            if path in firewall_rules.get("path_reject", []):
                return False
    return True
