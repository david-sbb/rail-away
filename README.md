# rail-away

# Backend setup

Before runnning the app, you'll need to have a version of python & to install requirements

```sh
# linux setup

# create python venv
$ python3 -m venv .venv

# activate the venv
$ source .venv/bin/activate

# install requirements
$ pip install -r requirements.txt

# lint and format
$ ruff format && ruff check --fix
```

Now you can run the app

```sh
$ python3 app.py
```