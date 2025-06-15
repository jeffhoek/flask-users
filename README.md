# Flask Users

Code Challenge

## Dependencies

### Docker
In order to run this application you'll need to run Docker.  Please see https://docs.docker.com/get-started/ if you haven't already set up Docker in your development environment.

### Python
This application uses Python 3.6 and `virtualenv` to isolate depedencies from your OS.  Please ensure you have python3 installed (https://www.python.org/).
`virtualenv` is also recommended:
```$basj
pip install virtualenv
```

## Installation
Unzip the archive and `cd` into the top-level `flask_users` directory.

Create your virtual environment:
```$bash
virtualenv -p python3 myenv
```

Then activate the environment:
```$bash
source myenv/bin/activate
```

Your terminal prompt should now have the `(myenv)` prefix.

Install requirements.txt:
```$bash
pip install -r requirements.txt
```

## Running the Web Application
To run the web app and back end services run:
```$bash
docker-compose up -d
```
This will run each service as a daemon.  The application should now be available at `localhost:5001/v1/users`.
If you have `curl` installed you can query the service from the command line using:
```$bash
curl -i -H "Content-Type: application/json" -XGET "localhost:5001/v1/users"
```
Or to `POST` a user document use:
```$bash
curl -i -H "Content-Type: application/json" -X POST localhost:5001/v1/users -d '{"metadata":"age 25, hobbies sailing", "email": "johndoe@example.com", "full_name": "John Doe}'
```


## Testing
Start up mongodb:
```$bash
docker-compose up -d mongodb
```
Then to run all tests simply run:
```$bash
pytest
```
For verbose output:
```$bash
pytest -v
```
For code coverage:
```$bash
pytest -v --cov-report term-missing --cov=flask_users
```
To suppress warning:
```$bash
pytest -v --cov-report term-missing --cov=flask_users -p no:warnings
```

