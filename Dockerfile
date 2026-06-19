# --- Build stage: assemble the virtual environment ---
FROM python:3.13-slim AS builder

# Install a pinned uv from PyPI (avoids depending on the ghcr.io registry).
RUN pip install --no-cache-dir uv==0.10.2

# Reproducible, container-friendly uv settings: compile bytecode for faster
# startup, copy (don't symlink) packages so the venv is self-contained and can
# be copied to the runtime stage, and use the base image's Python.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Build the .venv from the lockfile: runtime dependencies only, no dev group,
# and without installing the (non-packaged) project itself.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project


# --- Runtime stage: slim image carrying only the venv and the app ---
FROM python:3.13-slim
LABEL maintainer="Sylvain Roy <sylvain.roy@m4x.org>"

WORKDIR /app

# Copy the prebuilt virtual environment from the build stage. Both stages share
# the same base image and venv path, so the interpreter symlinks stay valid and
# uv/pip never end up in the final image.
COPY --from=builder /app/.venv /app/.venv

# Copy the application code and assets.
COPY *.py ./
COPY static ./static
COPY data ./data

# Run inside the project's virtual environment.
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# GOOGLE_MAPS_API_KEY is read from the environment at runtime (never baked in):
#   docker run -p 8000:8000 -e GOOGLE_MAPS_API_KEY=... <image>
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
