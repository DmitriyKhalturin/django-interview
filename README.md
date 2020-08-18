
#### Requirements
* [Python 3.8](https://www.python.org/)
* [Pip](https://pypi.org/project/pip/)
* [Pipenv](https://github.com/pypa/pipenv)

#### Installation
```shell script
pipenv install --ignore-pipfile   # Install dependencies from Pipfile.lock
```

#### Execution
```shell script
pipenv shell                      # enter to virtual environment
python manage.py makemigrations   # create db migrations scripts (if need)
python manage.py migrate          # apply migrations scripts
python manage.py runserver        # start django server
```

#### Api documentation
[See swagger on local server](http://127.0.0.1:8000/swagger/)

Or at the address (example.com/swagger/) on your server.

#### Test
```shell script
pipenv shell                      # enter to virtual environment
python manage.py test --tag=api   # run test
```
