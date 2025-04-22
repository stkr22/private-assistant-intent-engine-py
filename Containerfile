# Build stage: Python 3.11.11-bookworm
FROM docker.io/library/python:3.11.11-bookworm@sha256:b337e1fd27dbacda505219f713789bf82766694095876769ea10c2d34b4f470b as build-python

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:0.5.20@sha256:a8d9b557b6cd6ede1842b0e03cd7ac26870e2c6b4eea4e10dab67cbd3145f8d9 /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy the application into the container.
COPY pyproject.toml README.md uv.lock /app/
COPY src /app/src

RUN --mount=type=cache,target=/root/.cache \
    cd /app && \
    uv sync \
      --frozen \
      --no-group dev \
      --group prod

# runtime stage: Python 3.11.11-slim-bookworm
FROM docker.io/library/python:3.11.11-slim-bookworm@sha256:081075da77b2b55c23c088251026fb69a7b2bf92471e491ff5fd75c192fd38e5

# Create non-root user
RUN addgroup --system --gid 1001 appuser && adduser --system --uid 1001 --no-create-home --ingroup appuser appuser

WORKDIR /app
COPY --from=build-python /app /app

ENV PATH="/app/.venv/bin:$PATH"
# Set the user to 'appuser'
USER appuser

CMD ["private-assistant-intent-engine"]
