# ==================================================================
# EnXi ERP — Production Docker Image
# ==================================================================
# Build:  docker compose build
# Run:    docker compose up -d
# ==================================================================

ARG PYTHON_VERSION=3.12
ARG NODE_VERSION=20

FROM python:${PYTHON_VERSION}-slim-bookworm

ARG NODE_VERSION
ARG FRAPPE_BRANCH=develop
ARG PAYMENTS_BRANCH=develop

LABEL maintainer="EnXi" \
      description="EnXi ERP — Open Source Enterprise Resource Planning"

ENV DEBIAN_FRONTEND=noninteractive \
    NODE_OPTIONS="--max-old-space-size=4096" \
    PATH="/home/frappe/.local/bin:/home/frappe/frappe-bench/env/bin:${PATH}"

# ---------- System dependencies ----------
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        pkg-config \
        # MariaDB client & dev headers
        mariadb-client \
        libmariadb-dev \
        # PDF generation (wkhtmltopdf)
        xvfb libfontconfig wkhtmltopdf \
        # Pillow image processing
        libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev libwebp-dev \
        # lxml XML processing
        libxml2-dev libxslt1-dev \
        # pycups printing support
        libcups2-dev \
        # pango / cairo for PDF rendering
        libpango-1.0-0 libcairo2 libpangocairo-1.0-0 \
        # General utilities
        curl wget sudo \
    && rm -rf /var/lib/apt/lists/*

# ---------- Node.js ----------
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install -g yarn \
    && rm -rf /var/lib/apt/lists/*

# ---------- Frappe system user ----------
RUN groupadd -g 1000 frappe \
    && useradd -ms /bin/bash -u 1000 -g 1000 frappe \
    && echo "frappe ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER frappe
WORKDIR /home/frappe

# ---------- Bench CLI ----------
RUN pip install --user --no-cache-dir frappe-bench

# ---------- Initialize Bench with Frappe ----------
RUN bench init \
        --skip-redis-config-generation \
        --skip-assets \
        --frappe-branch "${FRAPPE_BRANCH}" \
        --python "$(which python3)" \
        frappe-bench

WORKDIR /home/frappe/frappe-bench

# ---------- Install dependency apps ----------
RUN bench get-app payments --branch "${PAYMENTS_BRANCH}"

# ---------- Install EnXi (ERPNext) app from local source ----------
COPY --chown=frappe:frappe . /tmp/enxi-source/

RUN cd /tmp/enxi-source \
    && git init -q \
    && git config user.email "build@enxi" \
    && git config user.name "EnXi Build" \
    && git add -A \
    && git commit -q -m "docker build" \
    && cd /home/frappe/frappe-bench \
    && bench get-app file:///tmp/enxi-source \
    && rm -rf /tmp/enxi-source

# ---------- Build production assets ----------
RUN bench build --production

# ---------- Backup artefacts needed after volumes mount ----------
# When 'sites/' is a Docker volume the image contents are hidden,
# so we stash copies that the entrypoint restores at runtime.
RUN cp sites/apps.txt /home/frappe/apps.txt \
    && cp -a sites/assets /home/frappe/assets

# ---------- Entrypoint ----------
COPY --chown=frappe:frappe docker/entrypoint.sh /home/frappe/entrypoint.sh
RUN chmod +x /home/frappe/entrypoint.sh

EXPOSE 8000 9000

VOLUME ["/home/frappe/frappe-bench/sites"]

ENTRYPOINT ["/home/frappe/entrypoint.sh"]
CMD ["backend"]
