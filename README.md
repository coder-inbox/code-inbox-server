# 📦 Code Inbox Server

<div align="center">

[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Static typing: mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![Codeql](https://github.com/github/docs/actions/workflows/codeql.yml/badge.svg)

</div>

A fully asynchronous backend for [Code Inbox](https://github.com/wiseaidev/code-inbox).

## 🛠️ Development Requirements

To contribute to this project, you'll need the following tools and dependencies:

- [Make](https://www.gnu.org/software/make/)
- Python (>= 3.9)
- [Poetry](https://python-poetry.org/)

## 📂 Project Structure

<details>
<summary><code>❯ tree src</code></summary>

```sh
.
├── nylas          # Package contains different config files for the `nylas` app.
│   ├── crud.py       # Module contains different CRUD operations performed on the database.
│   ├── models.py     # Module contains different data models for ODM to interact with database.
│   ├── router.py     # Module contains different routes for this api.
│   └── schemas.py    # Module contains different schemas for this api for validation purposes.
├── users         # Package contains different config files for the `users` app.
│   ├── crud.py       # Module contains different CRUD operations performed on the database.
│   ├── models.py     # Module contains different models for ODMs to inteact with database.
│   ├── router.py     # Module contains different routes for this api.
│   └── schemas.py    # Module contains different schemas for this api for validation purposes.
├── utils         # Package contains different common utility modules for the whole project.
│   ├── dependencies.py     # A utility script that yield a session for each request to make the crud call work.
│   ├── engine.py           # A utility script that initializes an ODMantic engine and client and set them as app state variables.
├── config.py     # Module contains the main configuration settings for project.
├── main.py       # Startup script. Starts uvicorn.
└── py.typed      # mypy related file.
```

</details>

## 🚀 Installation with Make

The best way to configure, install dependencies, and run the project is by using `make`. Follow these steps to get started:

1. **Create a virtual environment:**

   ```sh
   make venv
   ```

2. **Activate the virtual environment:**

   ```sh
   source .venv/bin/activate
   ```

3. **Install dependencies:**

   ```sh
   make install
   ```

4. **Setup a MongoDB Atlas account:**

   Create an account and cluster on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/signup).

5. **Set your MongoDB Credentials:**

   Update the following environment variables in your `.env` file with your MongoDB credentials:

   ```yaml
   MONGODB_USERNAME=
   MONGODB_PASSWORD=
   MONGODB_HOST=cluster_name.example.mongodb.net
   MONGODB_DATABASE=shop
   ```

6. **Create a Deta Account:**

   Create an account on [Deta](https://www.deta.sh/) and create a new project.

7. **Set your Deta project key:**

   Set the following environment variable in your `.env` file according to your project key value:

   ```yaml
   DETA_PROJECT_KEY=
   ```

8. **Generate a secret key:**

   Generate a secret key using OpenSSL and update its env var in the `.env` file:

   ```sh
   openssl rand -hex 128
   ```

   ```yaml
   JWT_SECRET_KEY=generated_secret_key
   DEBUG=info
   ```

9. **Run The Project Locally:**

   ```sh
   make run
   ```

   Access Swagger Documentation: <http://localhost:8000/docs>

   Access Redocs Documentation: <http://localhost:8000/redocs>

## 🚀 Deployments

### Deploy locally with Compose v2

1. Clone the `code-inbox` submodule:

   ```sh
   git submodule update --init --recursive
   ```

2. Install and configure [Compose v2](https://github.com/docker/compose) on your machine.

3. Build docker containers services:

   ```sh
   make build
   ```

   or

   ```sh
   docker compose build
   ```

4. Spin up the containers:

   ```sh
   make up
   ```

   or

   ```sh
   docker compose up
   ```

   Wait until the client service becomes available.

5. Stop the running containers:

   ```sh
   make down
   ```

### 🚀 Deta Micros (Endpoints not working)

You'll need to create a Deta account to use the Deta version of the APIs.

[![Deploy on Deta](https://button.deta.dev/1/svg)](https://go.deta.dev/deploy?repo=https://github.com/wiseaidev/code-inbox-server)

### 🚀 Heroku

This button will only deploy the server.

[![Deploy on Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/wiseaidev/code-inbox-server)

## 📋 Core Dependencies

The following packages are the main dependencies used to build this project:

- [`python`](https://github.com/python/cpython)
- [`fastapi`](https://github.com/tiangolo/fastapi)
- [`uvicorn`](https://github.com/encode/uvicorn)
- [`pydantic`](https://github.com/pydantic/pydantic)
- [`odmantic`](https://github.com/art049/odmantic)
- [`PyJWT`](https://github.com/jpadilla/pyjwt)
- [`passlib`](https://passlib.readthedocs.io/en/stable/index.html)
- [`python-multipart`](https://github.com/andrew-d/python-multipart)

## 📄 License

This project and the accompanying materials are made available under the terms and conditions of the [MIT LICENSE](https://github.com/wiseaidev/code-inbox-server/blob/main/LICENSE).
