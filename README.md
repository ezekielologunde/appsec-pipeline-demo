# appsec-pipeline-demo

A tiny Flask app with two deliberately planted, documented flaws, wired into a
CI security pipeline (SAST, secret scanning, dependency/container scanning)
that catches both and fails the build.

## What this is

A small, honest demonstration of an application-security CI pipeline, built
to close a real, named skill gap (see the project owner's `gaps-to-close.md`),
not a claim of production security-engineering experience. Everything here is
real: the app, the planted flaws, and the CI runs. Nothing about scale or
prior production use is implied beyond what this README says.

## What this is not

Not a production application, not deployed anywhere, not a claim of
professional CI/CD or DevSecOps experience beyond exactly what's shown in
this repo's commit history and Actions runs.

## The planted flaws

1. **OS command injection (CWE-78)** — `app.py`'s `/ping` route builds a
   shell command by concatenating unsanitized user input and runs it with
   `shell=True`. `/ping?host=127.0.0.1;id` executes the injected command.
2. **Hardcoded secret** — `config.py` contains a randomly generated,
   high-entropy string literal assigned to `THIRD_PARTY_API_KEY`. It was
   never registered to any real service and there is nothing to revoke.
   Deliberately generic rather than shaped like a specific vendor's key
   (e.g. AWS's `AKIA...` prefix): GitHub's server-side push protection
   blocks any push containing a string matching a *known provider's*
   secret pattern, even one that is fake and clearly documented as such,
   because it can't tell fake from real from the pattern alone. A generic
   high-entropy secret still gets caught by Gitleaks' entropy-based
   `generic-api-key` rule locally and in CI, without tripping GitHub's own
   platform-level scanner - itself a useful thing to know: the two layers
   (repo-level Gitleaks in this pipeline, and GitHub's platform-level push
   protection) catch different things and neither replaces the other.

## The pipeline (`.github/workflows/security.yml`)

- **SAST — Semgrep** (`semgrep --config auto --error .`): flags the
  command-injection pattern in `app.py` and fails the build.
- **Secret scanning — Gitleaks**: flags the high-entropy key literal in
  `config.py` and fails the build.
- **Dependency & container scanning — Trivy**: builds the Docker image and
  scans it for HIGH/CRITICAL OS and dependency vulnerabilities, failing the
  build above that threshold.

## Evidence trail

- The initial commit ships both flaws; the first Actions run is
  expected to **fail** on Semgrep and Gitleaks (Trivy also fails
  independently on a container running as root and the same secret baked
  into the image layer).
- The fix commit addresses all of it: the subprocess call is
  rewritten with `shell=False`, an argument list, and an allowlist regex on
  the input; the hardcoded key is replaced with environment-variable loads
  (`.env.example` documents the variable names, never real values); the
  Dockerfile runs as an unprivileged user; the workflow's third-party
  Actions are pinned to commit SHAs instead of mutable tags (a Semgrep
  finding on the workflow file itself). The next Actions run is expected to
  **pass**.
- Trivy also flagged two HIGH-severity CVEs vendored inside `pip`'s own
  bundled dependencies on the base image (not this app's code, not
  independently upgradable via `requirements.txt`) — investigated and
  recorded as accepted risk in `.trivyignore` with the reasoning, rather
  than silently raising the severity threshold to hide them.
- Both runs stay visible in the repo's Actions history as the actual
  evidence — this README does not restate pass/fail results that could go
  stale.
- Note: `git log` still contains the original hardcoded key in the initial
  commit's history. It was never a live credential, so there is nothing to
  rotate, but this is a deliberate illustration of a real lesson: deleting a
  secret in a later commit does not remove it from git history — a real
  leaked credential must be rotated/revoked at the source, not just deleted
  from the latest commit.

## Running locally

```bash
pip install -r requirements.txt
python app.py
```
