FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Install Python and development tools
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create symlinks for convenience
RUN ln -s /usr/bin/python3 /usr/bin/python || true
