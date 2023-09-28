# A workaround to run both the client and the server on heroku in one container.
FROM python:3.9.10-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /src

# Install make and curl
RUN apt-get update \
 && apt-get install -y make curl --no-install-recommends \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Install Dependencies
COPY ./poetry.lock ./pyproject.toml ./Makefile ./
RUN make docker-install

COPY ./src ./src

# Client

ENV REACT_APP_SERVER_URL=http://0.0.0.0:8000/api/v1
ENV REACT_APP_SOCKET_URL=ws://0.0.0.0:8000/api/v1/ws

WORKDIR /client

# Install npm
RUN apt-get update \
 && apt install -y npm --no-install-recommends \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY ./code-inbox/package.json  ./
COPY ./code-inbox/src ./src
COPY ./code-inbox/public ./public

RUN pnpm install

# Run both server and client
COPY ./run.sh  ./
CMD ["sh", "./run.sh"]
