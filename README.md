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

## Setup Environment Variables

```text
SECRET_KEY=
DEBUG=
ALLOWED_HOSTS=
REDIS_PASSWORD=
```

## Celery

### Start worker process

```bash
celery -A config worker -l INFO
```

### Start scheduler

```bash
celery -A config beat -l INFO
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

### Run Tests

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
