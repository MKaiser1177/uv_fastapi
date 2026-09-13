# PokeHub

PokeHub is a small full-stack Pokémon dashboard built with FastAPI, Streamlit, pandas, and uv. The backend loads the bundled Pokémon dataset, exposes statistics through a JSON API, and the frontend consumes that API to display a chart, the complete dataset, and a type-specific filtered view.

## Features

- FastAPI service for Pokémon statistics and filtering.
- Streamlit dashboard with a Pokémon type selector.
- Bar chart showing the eight most common Pokémon types.
- Bundled CSV data, so no external database or API is required.
- Local development and Docker Compose workflows.

## Architecture

```text
Pokemon.csv
		|
		v
FastAPI backend (port 8000)
		|  /pokemon/stats
		|  /pokemon/number_types
		|  /pokemons/type?poke_type=...
		v
Streamlit frontend (port 8501)
```

The backend reads `backend/src/backend/data/Pokemon.csv` when the application module is imported. The frontend uses the `BACKEND_URL` environment variable to locate the API. Its default value is `http://127.0.0.1:8000`, which is suitable when both applications run directly on the host.

## Project layout

```text
.
├── backend/
│   ├── pyproject.toml             # Backend package and dependencies
│   └── src/backend/
│       ├── api.py                 # FastAPI application and routes
│       ├── constants.py           # Dataset path
│       ├── data_processing.py     # CSV loading and pandas transformations
│       └── data/Pokemon.csv       # Bundled Pokémon dataset
├── frontend/
│   ├── pyproject.toml             # Frontend package and dependencies
│   └── src/frontend/
│       └── dashboard.py           # Streamlit dashboard
├── dockerfiles/
│   ├── backend.dockerfile
│   └── frontend.dockerfile
├── docker-compose.yaml            # Two-service container setup
└── README.md
```

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)
- Docker and Docker Compose, if using the container workflow

Each application has its own `pyproject.toml` and virtual environment. Install dependencies separately from the corresponding application directory.

## Run locally

### 1. Start the backend

From PowerShell:

```powershell
Set-Location backend
uv sync
uv run uvicorn backend.api:app --reload --host 127.0.0.1 --port 8000
```

The API is then available at `http://127.0.0.1:8000`. FastAPI's interactive documentation is available at `http://127.0.0.1:8000/docs`.

### 2. Start the frontend

Open a second terminal:

```powershell
Set-Location frontend
uv sync
$env:BACKEND_URL = "http://127.0.0.1:8000"
uv run streamlit run src/frontend/dashboard.py
```

Open the Streamlit URL printed in the terminal, normally `http://localhost:8501`.

For macOS or Linux, the equivalent environment variable command is:

```bash
BACKEND_URL=http://127.0.0.1:8000 uv run streamlit run src/frontend/dashboard.py
```

The frontend makes requests when the page loads. Keep the backend running while using the dashboard.

## Run with Docker Compose

From the repository root:

```powershell
docker compose up --build
```

This starts:

| Service | Host URL | Container port | Purpose |
| --- | --- | --- | --- |
| `backend` | `http://localhost:8000` | `8000` | FastAPI API |
| `frontend` | `http://localhost:8501` | `8501` | Streamlit dashboard |

Inside the Compose network, the frontend reaches the backend at `http://backend:8000`. This is configured by `docker-compose.yaml`; do not replace it with `localhost` in the container environment because `localhost` would refer to the frontend container itself.

Stop the services with:

```powershell
docker compose down
```

To rebuild after dependency or source changes:

```powershell
docker compose up --build
```

## API reference

The API is served by `backend.api:app`.

### `GET /pokemon/stats`

Returns every row from the CSV as a JSON array. Each item contains the dataset columns, including `Name`, `Type 1`, `Type 2`, base stats, `Generation`, and `Legendary`. Missing secondary types are represented internally as `missing`.

Example:

```text
http://localhost:8000/pokemon/stats
```

### `GET /pokemon/number_types`

Returns an object whose keys are Pokémon types and whose values are the number of occurrences across both `Type 1` and `Type 2`. The `missing` placeholder is excluded from the result.

Example response shape:

```json
{
	"Water":  ...,
	"Normal": ...,
	"Grass":  ...
}
```

### `GET /pokemons/type`

Filters the dataset by either primary or secondary type. The query parameter is `poke_type`.

```text
http://localhost:8000/pokemons/type?poke_type=water
```

The backend trims whitespace and capitalizes the supplied value, so values such as `water` and ` Water ` are accepted. Note that this route intentionally uses the plural path `/pokemons/type`.

## Data processing

The data pipeline in `backend/src/backend/data_processing.py`:

1. Loads `Pokemon.csv` with pandas.
2. Replaces missing values in `Type 2` with `missing`.
3. Counts values from both type columns and combines counts for types that appear in either column.
4. Sorts type counts from highest to lowest and removes the `missing` placeholder.
5. Filters rows when a requested type matches `Type 1` or `Type 2`.

The CSV is packaged with the backend and resolved relative to the Python module, so the application does not depend on the current working directory when it is launched through the documented commands.

## Configuration

The frontend supports one environment variable:

| Variable | Default | Description |
| --- | --- | --- |
| `BACKEND_URL` | `http://127.0.0.1:8000` | Base URL used for frontend API requests |

The backend currently has no required environment variables.

## Troubleshooting

### The dashboard cannot connect to the API

Confirm that the backend is running and that `BACKEND_URL` points to the correct address. For local development use `http://127.0.0.1:8000`; for Docker Compose use `http://backend:8000` from inside the frontend container.

### The API cannot find `Pokemon.csv`

Run the backend from the repository copy and keep the dataset at `backend/src/backend/data/Pokemon.csv`. The Dockerfile copies the complete `backend/` directory into the image, including the data file.

### Port 8000 or 8501 is already in use

Stop the process using the port, or change the host side of the Compose mapping. For example, `8000:8000` can become `8001:8000`; the frontend's container-side `BACKEND_URL` should remain `http://backend:8000`.

## Development notes

- Backend dependencies are declared in `backend/pyproject.toml`.
- Frontend dependencies are declared in `frontend/pyproject.toml`.
- `uv sync` creates or updates the environment from the relevant project file.
- The package entry points named `backend` and `frontend` currently print a greeting; the documented development commands invoke Uvicorn and Streamlit directly because those are the actual application servers.
- FastAPI's generated OpenAPI schema can be inspected at `/docs` or `/openapi.json` while the backend is running.
