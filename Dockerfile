FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Copy only what's needed to build
COPY pyproject.toml README.md LICENSE micromorph.py ./

RUN apk add --no-cache git \
    && pip install --no-cache-dir --no-compile . \
    && pip uninstall -y setuptools wheel \
    && rm -rf /usr/local/lib/python3.13/site-packages/googleapiclient/discovery_cache \
    && find /usr/local/lib/python3.13/site-packages -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local/lib/python3.13/site-packages -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true \
    && rm -rf /root/.cache \
    && rm -rf /var/cache/apk/* \
    && rm -rf /usr/local/lib/python3.13/site-packages/beartype \
    && rm -rf /usr/local/lib/python3.13/site-packages/docutils \
    && rm -rf /usr/local/lib/python3.13/site-packages/pygments/lexers \
    && rm -rf /usr/local/lib/python3.13/site-packages/pydantic/v1 \
    && rm -rf /usr/local/lib/python3.13/site-packages/pyasn1_modules
