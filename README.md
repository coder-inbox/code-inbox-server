# Code Inbox Server

<div align="center">

[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Static typing: mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

</div>

![architecture](static/architecture.jpg)

A Fully Async-based backend for [Code Inbox](https://github.com/wiseaidev/code-inbox).

## Development Requirements

- Make (GNU command)
- Python (>= 3.9)
- Poetry (1.6)

## Project Structure

<details>
<summary><code>❯ tree src</code></summary>

```sh
├── nylas         # Package contains different config files for the `nylas` app.
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
│   ├── openai_api.py       # A utility script that creates an openai object.
│   ├── dependencies.py     # A utility script that yield a session for each request to make the crud call work.
│   ├── engine.py           # A utility script that initializes an ODMantic engine, client, nylas, and openai and set them as app state variables.
├── config.py     # Module contains the main configuration settings for project.
├── main.py       # Startup script. Starts uvicorn.
└── py.typed      # mypy related file.
```

</details>

## Installation with Make

The project is best configured, dependencies installed, and managed using the `make` utility. Therefore, it is essential to ensure that you have `make` properly installed and configured on your local machine before proceeding. Follow the steps below to install `make` on your specific operating system:

**For Windows:**

1. Visit the [Stack Overflow thread](https://stackoverflow.com/questions/32127524/how-to-install-and-use-make-in-windows) that provides detailed instructions on how to install and use `make` on Windows.

2. Follow the step-by-step guide to download and set up `make` for Windows. Once installed, ensure that the `make` executable is in your system's PATH for easy access.

**For Mac OS:**

1. Visit the [Stack Overflow thread](https://stackoverflow.com/questions/11494522/installing-make-on-mac) that explains the installation process for `make` on Mac OS.

2. Follow the instructions provided in the thread to install `make` on your Mac OS. You may use package managers like Homebrew or MacPorts to simplify the installation process.

**Using `make` for the Project**

With `make` installed and configured on your machine, you can now navigate to the root directory of this project and take advantage of the available `make` commands to manage and run the project efficiently. Here are some common `make` commands you can run:

```sh
Please use 'make <target>' where <target> is one of:

venv                     Create a virtual environment
install                  Install the package and all required core dependencies
run                      Running the app locally
deploy-deta              Deploy the app on a Deta Micro
clean                    Remove all build, test, coverage and Python artifacts
lint                     Check style with pre-commit
test                     Run tests quickly with pytest
test-all                 Run tests on every Python version with tox
build                    Build docker containers services
up                       Spin up the built containers
down                     Stop all running containers
coverage                 Check code coverage quickly with the default Python
```

By running these `make` commands, you can streamline various project-related tasks and ensure a smooth development and execution experience.

### 1. Create a virtualenv

```sh
make venv
```

### 2. Activate the virtualenv

```sh
source .venv/bin/activate
```

### 3. Install dependencies

```sh
make install
```

**Note**: _This command will automatically generate a `.env` file from `.env.example`, uninstall the old version of poetry on your machine, then install latest version `1.6.1`, and install the required main dependencies._

### 4. Setup a MongoDB Account and Configure Your Database

MongoDB is a popular NoSQL database that you can use to store and manage your data. To get started with MongoDB and set up your database, follow these steps:

#### 4.1 Create a MongoDB Account and Deploy a Cluster

1. **Sign Up for a MongoDB Account:** Go to the official MongoDB website at [https://account.mongodb.com/account/login](https://account.mongodb.com/account/login) to create a MongoDB account if you don't already have one. You may need to provide some basic information during the registration process.
   ![mongodb create account](static/mongodb-create-account.png)

1. **Create a New Deployment:**
   - After logging into your MongoDB account, navigate to the MongoDB Atlas dashboard.
   - Click on the "Create" button to initiate the creation of a new deployment.
   ![Create a new deployment](static/create-new-deployment.png)

1. **Select the Free Tier:** Choose the free tier option to get started without incurring any costs during the initial setup.
   ![MongoDB Free Tier](static/free-tier-select.png)

1. **Set Username and Password:** Set up a username and password that you'll use to connect to your remote MongoDB server. Click "Create User" to save these credentials.
   ![Set Username and Password](static/set-username-and-password.png)

1. **Configure IP Access List:** To connect to your MongoDB cluster from anywhere for development and simplicity purposes, set the IP access list to "0.0.0.0/0." This allows connections from any IP address. Later, in a production environment, you should restrict this access to specific IPs for security reasons. Click "Add Entry" to confirm your settings.
   ![Configure IP Access List](static/configure-ip-access-list.png)

#### 4.2 Connect to the MongoDB Cluster

1. **Access the Database Section:** In the MongoDB Atlas dashboard, locate the left-side panel and click on the "Database" section.
   ![Database Section](static/mongodb-database.png)

1. **Connect to the Cluster:** Click the "Connect" button associated with your cluster to establish a connection.

1. **Copy the Cluster URL:** A connection dialog will appear with your cluster's connection details. Click the "Copy" button next to the Cluster URL. You'll need this URL to connect to your MongoDB cluster from your application.
   ![Cluster URL](static/mongodb-url-cluster.png)

#### 4.3 Set Your MongoDB Credentials

Now that you have your MongoDB cluster set up, you need to configure your project to use the MongoDB database. Follow these steps to set your MongoDB credentials:

1. **Update Your Environment Variables:** Open your project's configuration file or `.env` file, which stores environment variables.

1. **Set the MongoDB Credentials:**
   - Add the following environment variables to your configuration file, filling in the values accordingly:
     ```yaml
     # Database
     MONGODB_USERNAME=<Your_MongoDB_Username>
     MONGODB_PASSWORD=<Your_MongoDB_Password>
     MONGODB_HOST=<Your_MongoDB_Cluster_URL>
     MONGODB_DATABASE=coding
     ```
   - Replace `<Your_MongoDB_Username>`, `<Your_MongoDB_Password>`, and `<Your_MongoDB_Cluster_URL>` with the credentials and URL copied from your MongoDB cluster settings.

3. **Save Your Configuration:** Make sure to save the changes to your configuration file.

By setting these environment variables, your project will have the necessary credentials to connect to your MongoDB cluster and interact with your database. This configuration allows your application to store and retrieve data from MongoDB seamlessly.

Please note that keeping your MongoDB credentials secure is crucial to maintaining the security of your database. In a production environment, consider using more secure access controls and practices.

### 5. Create a Deta Account and Configure Data Storage

To utilize Deta for data storage and management, follow these steps:

1. **Sign up for a Deta Account:** Start by creating a Deta account if you don't already have one. You can sign up at [Deta's website](https://deta.space/).

1. **Create a Deta Space:** After logging into your Deta account, navigate to the Deta Space section. Here, you can organize your data collections and storage.
   ![Deta Space UI](static/deta-space-ui.png)

1. **Create a New Collection:** Inside your Deta Space, create a new collection. Collections are used to organize and store your data.
   ![Create a New Collection](static/deta-space-create-collection.png)

1. **Attach a Drive:** To store profile images or other files, you can attach a drive to your collection. In this case, name it `profile-images`. This drive will be used to manage and store profile images.
   ![Attach a Drive](static/deta-space-create-drive.png)
   ![Drive Name](static/deta-space-drive-name.png)

1. **Generate a Data Key:** To interact with your Deta collection programmatically, you'll need a data key. Create a new data key for your project, and make sure to copy it. You'll use this key in the next step.
   ![Create a Data Key](static/deta-space-project-key.png)

#### 5.1 Set Your Deta Project Key

Now that you have your Deta project set up, you need to configure your project to use the Deta API. Follow these steps to set your Deta project key:

1. **Update Your Environment Variables:** Open your project's configuration file or `.env` file, which stores environment variables.

1. **Set the Deta Project Key:** Add the following environment variable to your configuration file, replacing `DETA_PROJECT_KEY` with the actual key you copied earlier:
     ```yaml
     # Deta
     DETA_PROJECT_KEY=<Your_Deta_Project_Key>
     ```
   - Make sure to save the changes to your configuration file.

By setting the `DETA_PROJECT_KEY` environment variable, your project will have the necessary access to interact with your Deta Space and perform actions like storing and retrieving data.

### 6. Create a Nylas Account and Configure the System Token

Nylas is a platform that enables email and scheduling functionality in your application. To get started with Nylas and configure the system token, follow these steps:

#### 6.1 Create a Nylas Account and Configure Nylas Client ID and Client Secret

1. **Visit the Nylas Website:** Go to the official Nylas website at [https://dashboard.nylas.com/sign-in](https://dashboard.nylas.com/sign-in) to create a Nylas account if you don't already have one.

1. **Registration Process:** Complete the registration process by filling in the necessary information.
   ![Registration Process](static/nylas-info.png)

1. **Connect an Account:** After successfully creating your Nylas account and logging in, go to the "Account" tab or section in the Nylas dashboard.
   ![Connect an Account](static/connect-account.png)

1. **Connect an Email Account:** Click on "Connect an Account" to integrate an email account with Nylas. Follow the on-screen instructions to connect the desired email account(s) that your application will interact with.

1. **Copy the Access Token:** Once you have successfully connected your email account(s), Nylas will provide an access token. Copy this access token as you will need it to configure your application.
   ![Access Token](static/access-token.png)

To integrate Nylas into your application, you need to set up the Nylas Client ID and Client Secret in your project's settings.

1. **Access App Settings:** In the Nylas dashboard, navigate to the "App Settings" section. This is where you can manage your application's configuration.
   ![Access App Settings](static/app-settings.png)

#### 6.2 Set Your Nylas Client ID, Client Secret, and System Token

Now that you have your Nylas project set up, you need to set the Client ID, Client Secret, and System Token in your application:

1. **Set the Nylas Client ID, Client Secret, and System Token:** Open your project's configuration file or `.env` file, where you store environment variables.

1. **Add the Nylas Client ID , Client Secret, and System Token:** In your configuration file, add the following environment variables, replacing `<Your_Nylas_Client_ID>`, `<Your_Nylas_Client_Secret>`, and `<Your_Nylas_System_Token>` with the actual values you obtained from the Nylas dashboard:
     ```yaml
     # Nylas
     NYLAS_SYSTEM_TOKEN=<Your_Nylas_System_Token>
     NYLAS_CLIENT_ID=<Your_Nylas_Client_ID>
     NYLAS_CLIENT_SECRET=<Your_Nylas_Client_Secret>
     ```
     - Save the changes to your configuration file.

By setting the `NYLAS_CLIENT_ID`, `NYLAS_CLIENT_SECRET` and `NYLAS_SYSTEM_TOKEN` environment variables, your application will have the necessary credentials to authenticate and interact with the Nylas API for email and scheduling functionality. These credentials are essential for secure communication with Nylas services.

### 7. Run The Project Locally

```sh
make run
```

**Note**: _You have to set **DEBUG=info** to access the docs._

#### Access Swagger Documentation

> <http://localhost:8000/docs>

#### Access Redocs Documentation

> <http://localhost:8000/redocs>

## Deployments

### Deploy locally with Compose v2

First thing first, to run the entire platform, you have to clone the `code-inbox` submodule using the following command:

```sh
git submodule update --init --recursive
```

Once that is done, make sure you have [compose v2](https://github.com/docker/compose) installed and configured on your machine, and run the following command to build the predefined docker services(make sure you have a .env file beforehand):

**Using Make**

```sh
make build
```

or simply running:

```
docker compose build
```

Once that is done, you can spin up the containers:

**Using Make**

```sh
make up
```

or running:

```
docker compose up
```

Wait until the client service becomes available:

```sg
code-inbox-client-1      | Starting the development server...
```

You can stop the running containers but issuing the following command on a separate terminal session:

```
make down
```

### Deta Micros (Endpoints not working)

You'll need to create a Deta account to use the Deta version of the APIs.

[![Deploy on Deta](https://button.deta.dev/1/svg)](https://go.deta.dev/deploy?repo=https://github.com/wiseaidev/code-inbox-server)

### Heroku

This button will only deploy the server.

[![Deploy on Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/wiseaidev/code-inbox-server)

## Core Dependencies

The following packages are the main dependencies used to build this project:

- [`python`](https://github.com/python/cpython)
- [`fastapi`](https://github.com/tiangolo/fastapi)
- [`uvicorn`](https://github.com/encode/uvicorn)
- [`pydantic`](https://github.com/pydantic/pydantic)
- [`odmantic`](https://github.com/art049/odmantic)
- [`deta-python`](https://github.com/deta/deta-python)
- [`Nylas Python SDK`](https://github.com/nylas/nylas-python)
- [`python-multipart`](https://github.com/andrew-d/python-multipart)

## License

This project and the accompanying materials are made available under the terms and conditions of the [`MIT LICENSE`](LICENSE).
