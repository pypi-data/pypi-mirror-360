# Stage 1: Builder with heavy build-time and system dependencies
FROM python:3.12-slim-buster AS builder

ENV UV_VERSION=0.2.8
# Install uv using pip from the base image
RUN pip install uv==${UV_VERSION}
ENV PATH="/root/.local/bin:$PATH"

# Install system dependencies required by Pandoc for PDF generation
RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-latex-base \
    && rm -rf /var/lib/apt/lists/*

# Set up the application directory
WORKDIR /app

# Create a virtual environment in a standard location
RUN uv venv /opt/venv

# Copy only dependency files first to leverage Docker layer caching
COPY ./src/pyproject.toml ./src/uv.lock* /app/src/
COPY ./src/packages/huoshui-converter-core /app/src/packages/huoshui-converter-core
COPY ./src/packages/huoshui-structured-converter /app/src/packages/huoshui-structured-converter

# Install dependencies into the virtual environment
# We use system-site-packages to make the pre-installed pandoc/texlive available
RUN . /opt/venv/bin/activate && uv sync --system-site-packages --no-build
# The --no-build flag is important here to avoid trying to build the workspace itself in the container

# Stage 2: Final lean production image
FROM python:3.12-slim-buster AS final

# Create a non-root user to run the application
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser

# Copy required system binaries and libraries from the builder stage
# This part is tricky and might need adjustment. `ldd` can help find all shared libraries.
COPY --from=builder /usr/bin/pandoc /usr/bin/
# Copying the entire texlive distribution is large but necessary for pandoc's PDF engine
COPY --from=builder /usr/share/texlive /usr/share/texlive
# Add other necessary libs if pandoc complains
# Example: COPY --from=builder /usr/lib/x86_64-linux-gnu/libfontconfig.so.1 /usr/lib/x86_64-linux-gnu/

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code from the builder stage
COPY --from=builder --chown=appuser:appuser /app/src/packages/huoshui-converter-core/huoshui_converter_core /app/huoshui_converter_core
COPY --from=builder --chown=appuser:appuser /app/src/packages/huoshui-structured-converter/huoshui_structured_converter /app/huoshui_structured_converter

# Switch to the non-root user
USER appuser

# Set environment variables for the runtime
ENV PATH="/opt/venv/bin:$PATH"
ENV FASTMCP_TRANSPORT="http-stream"

EXPOSE 8080

# Define the command to run the application
CMD ["fastmcp", "run", "huoshui_structured_converter.server:main", "--host", "0.0.0.0", "--port", "8080"] 
