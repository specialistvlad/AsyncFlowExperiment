# Create a Virtual Environment

python -m venv venv

# Activate the Virtual Environment

# On Windows

venv\Scripts\activate

# On macOS/Linux

source venv/bin/activate

# Install pytest and hupper

pip install pytest hupper

# Save the Installed Packages to requirements.txt

pip freeze > requirements.txt

# Create README.md

echo "# Project Name

## Setup

### Create and Activate Virtual Environment

```sh
python -m venv venv

# On Windows

venv\Scripts\activate

# On macOS/Linux

source venv/bin/activate
```

### Install Dependencies

```sh
pip install -r requirements.txt
```

### Install `pytest` and `hupper`

```sh
pip install pytest hupper
```

### Save Dependencies

```sh
pip freeze > requirements.txt
```

## Running Tests

```sh
pytest
```

## Using `hupper` for Automatic Reloading

```sh
hupper -m pytest
```

" > README.md
