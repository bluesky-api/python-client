# Setup

Install python and poetry:

    asdf install

Install required packages:

    poetry install

# Development

Activate the venv before anything else:

    poetry shell

Run the tests:

    pytest

Before committing, format the code:

    bin/format

To build the documentation:

    cd docs
    make html

Then open `docs/_build/html/index.html`.
