# Build stage: Python 3.12.12-trixie
FROM docker.io/library/python:3.14.0-trixie@sha256:6098c3241d19532bdb439d8c211e3e1c6cfa93c512fbd9118fa0b3d02a418a3e AS build-python

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:0.9.5@sha256:f459f6f73a8c4ef5d69f4e6fbbdb8af751d6fa40ec34b39a1ab469acd6e289b7 /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependencies and pre-built wheel
COPY dist/*.whl /app/dist/

RUN --mount=type=cache,target=/root/.cache \
    uv venv && \
    uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_md-3.8.0/en_core_web_md-3.8.0-py3-none-any.whl && \
    uv pip install dist/*.whl

# runtime stage: Python 3.12.12-slim-trixie
FROM docker.io/library/python:3.14.0-slim-trixie@sha256:4ed33101ee7ec299041cc41dd268dae17031184be94384b1ce7936dc4e5dead3

ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN addgroup --system --gid 1001 appuser && adduser --system --uid 1001 --no-create-home --ingroup appuser appuser

WORKDIR /app
COPY --from=build-python /app /app

ENV PATH="/app/.venv/bin:$PATH"
# Set the user to 'appuser'
USER appuser

CMD ["private-assistant-intent-engine"]
