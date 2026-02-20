# Fitness Class Management and Booking System API

A REST API which enables users to create, browse, and manage fitness classes of a particular facility, and for guests/members to book spots in them. This system mimics a lightweight version of fitness studio management systems like Fitune or FitBudd, focusing on core backend functionality and its evolution over time, while working on simplified frontend.

## Prerequisites

- python 3.10 or higher
- MongoDB installed. Follow [https://www.mongodb.com/docs/manual/installation/](https://www.mongodb.com/docs/manual/installation/)
  to install MongoDB locally. Select the right link for your operating system.

## Important Note: Authentication for Protected Endpoints

In order to ensure that you are able to test the protected API endpoints (such as booking a class or viewing a class list as a trainer) please do the following:

1. Use the `auth/register` endpoint to create an account.
    1. Use `"trainer_code": "IAMATRAINER"` for creating a trainer account, otherwise role will be member.
2. After registration, use the `auth/login` endpoint to login (this will provide you with an authentication token)
    1. **IMPORTANT**: Make sure to copy the token from `"access_token": "hjX02ksdkKkjqD..."` in the JSON response.
3. Finally, SwaggerUI provides an "Authorize" button at the top of the page. Click this:
    1. For the token value field, write `Bearer <token>`, replacing `<token>` with the copied string you recieved from the login endpoint. Make sure to include a space between Bearer and the token.
    1. Hit Authorize and you will now be "logged in" and authenticated + authorized for the protected routes.

## Tech Stack

This flask web app uses:

- [Flask-RESTX][flask-restx] for creating REST APIs. Directory structure
  follows [flask restx instructions on scaling your project][flask-restx-scaling]
    - flask-restx automatically generates
      [OpenAPI specifications][openapi-specification] for your API
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

This assumes you are already running MongoDB (e.g., through
`brew services restart mongodb-community` on MacOS or
`sudo systemctl restart mongod` on Linux.
Find the equivalent for your OS)

### Setting up the environment

1. Check `.samplenv` file and follow the instructions there to create
   your `.env` file
2. Run `make dev_env` to create a virtual environment and install dependencies

### Running the server

2. Run `make run_server` to run the local server.
3. Go to [http://127.0.0.1:8000](http://127.0.0.1:8000) to see it running!

You can use `ctrl-c` to stop the server.
