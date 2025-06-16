# Flask Users

Code Challenge

## Dependencies

### Docker
In order to run this application you'll need to run [Docker](https://docs.docker.com/get-started/) or [Podman](https://podman-desktop.io/).

### Poetry
This application uses [Poetry](https://python-poetry.org/) for dependency management. On MacOS:
```
brew install poetry
```

## Installation
```
poetry install
```

## Running the Web Application
To run the web app and back end services run:
```$bash
podman compose up -d
```

This will run each service as a daemon.  The application should now be available at [http://localhost:5001/v1/users](http://localhost:5001/v1/users).

If you have `curl` installed you can query the service from the command line using:
```$bash
curl -i -H "Content-Type: application/json" -XGET "localhost:5001/v1/users"
```

To `POST` a user document use something like:
```$bash
curl -i -H "Content-Type: application/json" -X POST localhost:5001/v1/users -d '{"metadata":"age 25, hobbies sailing", "email": "johndoe@example.com", "full_name": "John Doe", "password": "very-insecure"}'
```

## Testing
Install test dependencies:
```
poetry install --with test
```

To run all tests run:
```$bash
poetry run pytest --disable-warnings
```

For verbose output:
```$bash
poetry run pytest -v
```

For code coverage:
```$bash
poetry run pytest -v --cov-report term-missing --cov=flask_users
```

To suppress warning:
```$bash
poetry run pytest -v --cov-report term-missing --cov=flask_users -p no:warnings
```
