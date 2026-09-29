import ipaddress
import re
import subprocess

from flask import Flask, request

app = Flask(__name__)

# RFC 1123 hostname: labels of letters/digits/hyphens, up to 253 chars total.
_HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$"
)


def _is_safe_host(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return bool(_HOSTNAME_RE.match(value))


@app.route("/ping")
def ping():
    """Ping a host and return the raw output.

    FIXED: the original version built a shell command by concatenating
    unsanitized user input and ran it with shell=True (CWE-78, OS command
    injection - see git history for the planted, vulnerable version this
    replaced). This version validates the input against a strict
    IP-address/hostname allowlist pattern and calls subprocess with
    shell=False and an argument list, so there is no shell to inject into.
    """
    host = request.args.get("host", "127.0.0.1")
    if not _is_safe_host(host):
        return "invalid host", 400
    result = subprocess.run(
        ["ping", "-c", "1", host], shell=False, capture_output=True, text=True
    )
    return result.stdout or result.stderr


@app.route("/")
def index():
    return "appsec-pipeline-demo: see README for what this app is and is not."


if __name__ == "__main__":
    app.run(debug=False)
