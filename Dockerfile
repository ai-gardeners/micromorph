FROM ghcr.io/astral-sh/uv:python3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app
COPY pyproject.toml README.md LICENSE micromorph.py ./

# Copy project files
COPY pyproject.toml README.md LICENSE micromorph.py ./

RUN apk add --no-cache git \
    && uv pip install --no-cache --python $(which python3) -e . \
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