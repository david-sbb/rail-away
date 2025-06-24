
# Backend setup

Before runnning the app, you'll need to have a version of python & to install requirements

```sh
# linux setup

# install uv (package manager)
$ curl -Ls https://astral.sh/uv/install.sh | sh

# create python venv
$ uv venv

# activate the venv
$ source .venv/bin/activate

# install dependencies
$ uv sync

# lint and format
$ uv run ruff format && uv run ruff check --fix
```

Now you can run the app

```sh
$ python3 app.py 
```