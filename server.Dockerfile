FROM python:3.10.10-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /src

# Install make and curl
RUN apt-get update \
 && apt-get install -y make curl --no-install-recommends \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Install Dependencies
COPY poetry.lock pyproject.toml Makefile ./
RUN make docker-install

COPY ./src ./src

EXPOSE 8000

CMD ["/root/.local/bin/poetry", "run", "server"]
