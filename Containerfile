# Build stage: Python 3.13.9-trixie
FROM docker.io/library/python:3.14.0-trixie@sha256:d88b1201e20b36976ff9d779cf1705cfa3598540a81bc31f0eee70a1e1f318e3 AS build-python

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:0.9.11@sha256:5aa820129de0a600924f166aec9cb51613b15b68f1dcd2a02f31a500d2ede568 /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependencies and pre-built wheel
COPY dist/*.whl /app/dist/

RUN --mount=type=cache,target=/root/.cache \
    uv venv && \
    uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_md-3.8.0/en_core_web_md-3.8.0-py3-none-any.whl && \
    uv pip install dist/*.whl

# runtime stage: Python 3.13.9-slim-trixie
FROM docker.io/library/python:3.14.0-slim-trixie@sha256:0aecac02dc3d4c5dbb024b753af084cafe41f5416e02193f1ce345d671ec966e

ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN addgroup --system --gid 1001 appuser && adduser --system --uid 1001 --no-create-home --ingroup appuser appuser

WORKDIR /app
COPY --from=build-python /app /app

ENV PATH="/app/.venv/bin:$PATH"
# Set the user to 'appuser'
USER appuser

CMD ["private-assistant-intent-engine"]
