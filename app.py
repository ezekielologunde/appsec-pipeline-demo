from flask import Flask, request
import subprocess

app = Flask(__name__)


@app.route("/ping")
def ping():
    """Ping a host and return the raw output.

    VULNERABLE ON PURPOSE (see README): builds a shell command by
    concatenating unsanitized user input, then runs it with shell=True.
    A request like /ping?host=127.0.0.1;cat+/etc/passwd executes the
    injected command. This is CWE-78 (OS Command Injection) and is the
    planted flaw this repo's CI pipeline is meant to catch.
    """
    host = request.args.get("host", "127.0.0.1")
    command = "ping -c 1 " + host
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout or result.stderr


@app.route("/")
def index():
    return "appsec-pipeline-demo: see README for what this app is and is not."


if __name__ == "__main__":
    app.run(debug=False)
