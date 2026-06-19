FROM python:3.13-slim
LABEL maintainer="Sylvain Roy <sylvain.roy@m4x.org>"

# Install a pinned uv from PyPI (avoids depending on the ghcr.io registry).
RUN pip install --no-cache-dir uv==0.10.2

# Reproducible, container-friendly uv settings: compile bytecode for faster
# startup, copy (don't symlink) packages, and use the base image's Python
# rather than fetching a managed one.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Install runtime dependencies from the lockfile in a cached layer. This step
# only re-runs when pyproject.toml or uv.lock change, not on code edits.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

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
