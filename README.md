[![CI Unit Tests](https://github.com/cs-uh-2012-spring26/cs-uh-2012-software-engineering-groupproject-group-a/actions/workflows/tests.yml/badge.svg)](https://github.com/cs-uh-2012-spring26/cs-uh-2012-software-engineering-groupproject-group-a/actions/workflows/tests.yml)

# Fitness Class Management and Booking System API

A REST API which enables users to create, browse, and manage fitness classes of a particular facility, and for guests/members to book spots in them. This system mimics a lightweight version of fitness studio management systems like Fitune or FitBudd, focusing on core backend functionality and its evolution over time, while working on simplified frontend.

## Prerequisites

- python 3.10 or higher
- MongoDB installed. Follow [here](https://www.mongodb.com/docs/manual/installation/) to install MongoDB locally.

## Tech Stack

This flask web app uses:

- [Flask-RESTX][flask-restx] for creating REST APIs. Directory structure
  follows [flask restx instructions on scaling your project][flask-restx-scaling]
- [PyMongo][pymongo] for communicating with the mongodb database
- [pytest][pytest] for testing
  (see [flask specific testing instructions on pytest][pytest-flask]
  for more info specific to testing Flask applications)
- [mongomock][mongomock] for mocking the mongodb during unit testing

<details>
<summary>Click to see full list of resources</summary>

- [Flask-RESTX Quickstart][flask-restx]
- [Flask-RESTX Scaling Guide][flask-restx-scaling]
- [OpenAPI Specification][openapi-specification]
- [PyMongo Documentation][pymongo]
- [pytest Documentation][pytest]
- [Flask Testing Documentation][pytest-flask]
- [mongomock Documentation][mongomock]

</details>

[flask-restx]: https://flask-restx.readthedocs.io/en/latest/quickstart.html
[flask-restx-scaling]: https://flask-restx.readthedocs.io/en/latest/scaling.html
[openapi-specification]: https://swagger.io/docs/specification/v3_0/about/
[pymongo]: https://pymongo.readthedocs.io/en/stable/
[pytest]: https://docs.pytest.org/en/stable/
[pytest-flask]: https://flask.palletsprojects.com/en/stable/testing/
[mongomock]: https://docs.mongoengine.org/guide/mongomock.html

## Deployed API

### URL to deployed API

[https://cs-uh-2012-software-engineering.onrender.com/](https://cs-uh-2012-software-engineering.onrender.com/)

**Note**: Since we are using the free tier version of Render, please allow for a minute or so for the server to spin up upon accessing the URL.

### Virtual Machine Set Up

Since the suggest DigitalOcean virtual machine was unavailable due to a paywall and no available credits, we resorted to using [Render.com](https://render.com/) to set up the virtual machine and deploy our website through their service. For the continuous deployment, Render provides us with a `RENDER_DEPLOY_HOOK` which we set up as a GitHub secret to trigger the deployment on pushes or changes to the main branch.

### Docker and MongoDB Cluster

Since the free tier of Render is limited, we host the MongoDB database using a [MongoDB Atlas](https://www.mongodb.com/products/platform/atlas-database), which allows us to have a universal database for the deployed service. The actual deployment on the Render Virtual Machine is done by running `docker compose up`, with the deploy variable env variables directly on the server.

## Running Locally

### Ensuring a local database instance is running

There are two ways to run the application:

- a local database which will allow for persistent data, even if you terminate the server and restart

- or using the MOCK_DB flag to be true

Firstly, open your terminal and enter the command `brew services restart mongodb-community` on macOS or
`sudo systemctl restart mongod` on Linux. (Find the equivalent for your OS). This will start a local MongoDB instance which the API server will connect to.

Next, we want to ensure that the service started with no issues, run `brew services list`.

You should see:

| Name              | Status                                   | User | File |
| ----------------- | ---------------------------------------- | ---- | ---- |
| mongodb-community | <span style="color:green">started</span> | ...  | ...  |

If the status is anything other than **started**, there might be a local issue with running the database.

---

### Setting up the environment

**NOTE:** If you are going to run with docker locally ensure that your local .env has `MONGO_URI=mongodb://mongo:27017`, as it is in the example.env.

However, if you will be running the application without docker, you need to change it for the localhost version, `MONGO_URI=mongodb://localhost:27017`

1. Run the following command (or equivalent) in your terminal to copy the .env: `cp example.env .env` (on macOS & Linux)
   1. If your local MongoDB instance is not running properly, keep `MOCK_DB=true`. Otherwise, if you want persistent data, change `MOCK_DB=false`.

2. With a text editor of your choice, open the .env and adjust the following variables:
   1. The following variables are sensitive, therefore please copy and paste them directly from [the protected link here](https://drive.google.com/file/d/1DFUREQG2wdz_tl0wQeTQI-xLspBQHyWm/view?usp=sharing). `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL`, `TELEGRAM_BOT_TOKEN`, and `TELEGRAM_BOT_USERNAME`.
3. Run `make dev_env` to create a virtual environment and install dependencies

---

### Running with Docker

Make sure Docker is running, then start the backend and MongoDB with:

    docker compose up --build

The API will be available at [http://localhost:8000](http://localhost:8000).

Docker Compose reads your `.env` file and overrides the database settings so the app connects to the MongoDB container. You do not need to run MongoDB locally when using Docker.

To stop the containers, press `ctrl-c`, then run:

    docker compose down

---

### Running the server and tests

There are multiple ways to start the application or just run the tests.

To **run the tests and start the local server**, run:

    make run_local_server

which will run the tests and start the local server, accessible at [http://127.0.0.1:8000](http://127.0.0.1:8000).

To start the server without running the tests, run:

    make run_server

You can use `ctrl-c` to stop the server. Same place accessible at [http://127.0.0.1:8000](http://127.0.0.1:8000).

Lastly, to **only run the tests**, run:

    make tests

### TLDR: Running the server

1. Make sure `mongodb-community` is running locally

2. Set up the `.env` file by copying and adding secret variables
3. Set up virtual env and install deps (`make dev_env`)
4. Run server + tests with `make run_local_server`.

## Important Note: Authentication for Protected Endpoints

In order to ensure that you are able to test the protected API endpoints (such as booking a class or viewing a class list as a trainer) please do the following:

1. Use the `auth/register` endpoint to create an account.
   1. Use `"trainer_code": "IAMATRAINER"` for creating a trainer account, otherwise role will be member.
   1. **IMPORTANT**: The endpoint will now also provide you with a `"telegram_connect_link"`. To enable Telegram notifications, please refer to the section below, _Telegram Notificaitons_.

2. After registration, use the `auth/login` endpoint to log in (this will provide you with an authentication token)
   1. **IMPORTANT**: Make sure to copy the token from `"access_token": "hjX02ksdkKkjqD..."` in the JSON response.
3. Finally, SwaggerUI provides an "Authorize" button at the top of the page. Click this:
   1. For the token value field, write `Bearer <token>`, replacing `<token>` with the copied string you received from the login endpoint. Make sure to include a space between Bearer and the token.
   1. Hit Authorize and you will now be "logged in" and authenticated + authorized for the protected routes.

## Telegram Notifications

After registering, the response includes a Telegram link. To link your account:

1. Open the link on a device where your Telegram account is active and tap **Start** to start the bot.
2. After having started the bot, you will not get any reply. To finish the sync, go ahead and continue with the login step.
3. Log in to the app: the bot will automatically send you a confirmation message once your Telegram account is successfully linked.

### Configuring Notifications: `POST /reminders/configure`

This endpoint lets authenticated users choose how they receive reminders. Send a JSON body with `preferred_notification_methods`, a non-empty list of one or both supported channels: `"email"` and `"telegram"`. The saved preferences are applied to all future booking reminders for that user.
