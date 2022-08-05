FROM python:3.9-slim-bullseye

# Set separate working directory for easier debugging.
WORKDIR /app

# Create virtual environment.
ENV VIRTUAL_ENV "/app/.virtualenv"
RUN python -m venv $VIRTUAL_ENV
ENV PATH "$VIRTUAL_ENV/bin:$PATH"

# hadolint ignore=DL3013
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Install requirements seperately to take advantage of layer caching.
COPY setup.cfg .
RUN python -c "import configparser; c = configparser.ConfigParser(); c.read('setup.cfg'); print(c['options']['install_requires'])" > requirements.txt
# hadolint ignore=DL3059
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy minimal set of package files
COPY MANIFEST.in .
COPY README.md .
COPY LICENSE.md .
COPY pyproject.toml .
COPY src ./src

# Install croninfo package.
RUN python -m pip install --no-cache-dir --no-dependencies .

# Switch to non-root user.
USER 5000

# Set entry point for image.
ENTRYPOINT ["croninfo"]
CMD ["--help"]
