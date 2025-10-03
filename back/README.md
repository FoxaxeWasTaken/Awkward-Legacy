## How to build a backend docker image
```bash
docker build -t awkward-legacy .
```

## How to run a backend docker container
```bash
docker run -p 8000:8000 awkward-legacy
```

## How to run pytest locally (venv)
```bash
export PYTHONPATH=$(pwd)/back
pytest back/tests
```