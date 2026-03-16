[![CI Unit Tests](https://github.com/cs-uh-2012-spring26/cs-uh-2012-software-engineering-groupproject-group-a/actions/workflows/tests.yml/badge.svg)](https://github.com/cs-uh-2012-spring26/cs-uh-2012-software-engineering-groupproject-group-a/actions/workflows/tests.yml)

# Fitness Class Management and Booking System API

A REST API which enables users to create, browse, and manage fitness classes of a particular facility, and for guests/members to book spots in them. This system mimics a lightweight version of fitness studio management systems like Fitune or FitBudd, focusing on core backend functionality and its evolution over time, while working on simplified frontend.

## Prerequisites

- python 3.10 or higher
- MongoDB installed. Follow [here](https://www.mongodb.com/docs/manual/installation/)
  to install MongoDB locally.

## Tech Stack

This flask web app uses:

- [Flask-RESTX][flask-restx] for creating REST APIs. Directory structure
  follows [flask restx instructions on scaling your project][flask-restx-scaling]
- [PyMongo][pymongo] for communicating with the mongodb database
- [pytest][pytest] for testing
  (see [flask specific testing instructions on pytest][pytest-flask]
  for more info specific to testing Flask applications)
- [mongomock][mongomock] for mocking the mongodb during unit testing

[flask-restx]: https://flask-restx.readthedocs.io/en/latest/quickstart.html
[flask-restx-scaling]: https://flask-restx.readthedocs.io/en/latest/scaling.html
[openapi-specification]: https://swagger.io/docs/specification/v3_0/about/
[pymongo]: https://pymongo.readthedocs.io/en/stable/
[pytest]: https://docs.pytest.org/en/stable/
[pytest-flask]: https://flask.palletsprojects.com/en/stable/testing/
[mongomock]: https://docs.mongoengine.org/guide/mongomock.html

## Running Locally

### Ensuring a local database instance is running

There are two ways run the application:

- a local database which will allow for persistant data, even if you terminate the server and restart

- or using the the MOCK_DB flag to be true

Firstly, open your terminal and enter the command `brew services restart mongodb-community` on MacOS or
`sudo systemctl restart mongod` on Linux. (Find the equivalent for your OS). This will start a local MongoDB instance which the API server will connect to.

Next, we want to ensure that the service started with no issues, run `brew services list`.

You should see:

| Name              | Status                                   | User | File |
| ----------------- | ---------------------------------------- | ---- | ---- |
| mongodb-community | <span style="color:green">started</span> | ...  | ...  |

If the status is anything other than **started**, there might be a local issue with running the database.

---

### Setting up the environment

1. Run the following command (or equivalent) in your terminal to copy the .env: `cp .samplenv .env` (on macOS & Linux)
   1. If your local MongoDB instance is not running properly, keep `MOCK_DB=true`. Otherwise, if you want persistent data, change `MOCK_DB=false`.

2. With a text editor of your choice, open the .env and adjust the following variables:
   1. Please replace the `SENDGRID_API_KEY` and `SENDGRID_FROM_EMAIL` with the actual API key and email found [HERE](https://drive.google.com/file/d/1DFUREQG2wdz_tl0wQeTQI-xLspBQHyWm/view?usp=sharing).
3. Run `make dev_env` to create a virtual environment and install dependencies

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

2. After registration, use the `auth/login` endpoint to login (this will provide you with an authentication token)
   1. **IMPORTANT**: Make sure to copy the token from `"access_token": "hjX02ksdkKkjqD..."` in the JSON response.
3. Finally, SwaggerUI provides an "Authorize" button at the top of the page. Click this:
   1. For the token value field, write `Bearer <token>`, replacing `<token>` with the copied string you recieved from the login endpoint. Make sure to include a space between Bearer and the token.
   1. Hit Authorize and you will now be "logged in" and authenticated + authorized for the protected routes.
