FROM python:3.11-slim

ARG TIGRISFS_VERSION=v1.2.1

WORKDIR /app

# Install System Dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    fuse \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Bun
ENV BUN_INSTALL="/root/.bun"
ENV PATH="$BUN_INSTALL/bin:$PATH"
RUN curl -fsSL https://bun.sh/install | bash

# Install TigrisFS
RUN set -e; \
    ARCH=$(uname -m); \
    case "$ARCH" in \
        x86_64) ARCH="amd64" ;; \
        aarch64) ARCH="arm64" ;; \
    esac; \
    curl -fL "https://github.com/tigrisdata/tigrisfs/releases/download/${TIGRISFS_VERSION}/tigrisfs_${TIGRISFS_VERSION#v}_linux_${ARCH}.tar.gz" | \
    tar -xzf - -C /usr/local/bin/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Default Port (overridden by Worker)
ENV PORT=8080
# Force cache invalidation
ENV CACHEBUST=20251205_1750
COPY . .
COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

# API Port
EXPOSE 8080

# Entrypoint
CMD ["/startup.sh"]
