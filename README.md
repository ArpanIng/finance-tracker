## Installation

### Install dependencies

```bash
poetry install
```

### Activate the virtual environment

```bash
source .venv/bin/activate
```

## Migrations

```bash
python manage.py migrate
```

### Generate dummy data

```bash
python manage.py generate_transactions
```

## Runserver

### Run the development server

```bash
python manage.py runserver
```

or

```bash
python manage.py runserver --settings=config.settings.development
```

### Run the production server

```bash
python manage.py runserver --settings=config.settings.production
```

## Testing

### Run Tetsts

```bash
python manage.py test app_name
```

### Run Tests with Coverage Tracking

```bash
coverage run manage.py test
```

### Generate the Coverage Report

```bash
coverage report -m
```
