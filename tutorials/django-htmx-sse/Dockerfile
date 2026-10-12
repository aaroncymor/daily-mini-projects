FROM python:3.14

ARG USER
ARG GROUP

WORKDIR /app

ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="${PATH}:/root/.local/bin"

# Install Node.js and npm
RUN apt-get update && apt-get install -y curl ca-certificates gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip && pip install poetry

COPY --chown=${USER}:${GROUP} pyproject.toml poetry.lock README.md /app/
RUN poetry install --no-interaction --no-ansi

COPY --chown=${USER}:${GROUP} . /app/
RUN chmod +x /app/entrypoint.sh

# Install Tailwind dependencies for the Linux container
RUN cd /app/theme/static_src && npm install
RUN mkdir -p /app/theme/static/css/dist

CMD ["poetry", "run", "python", "manage.py", "tailwind", "start"]
