FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt
COPY app.py config.py .

# FIXED: the original image ran as root by default (Semgrep
# dockerfile.security.missing-user finding - see git history). Run as an
# unprivileged user instead.
RUN useradd --create-home --shell /usr/sbin/nologin appuser
USER appuser

EXPOSE 5000
CMD ["python", "app.py"]
