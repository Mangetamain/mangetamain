# Streamlit + Poetry + Docker — README

Run a Streamlit app with **Poetry** for dependencies and **Docker** for consistent dev/prod. This guide uses a **Docker-first** workflow (Poetry runs inside the container). No local venv required.

---

## 📦 Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose V2)
- Git (optional)

---

## 🚀 Quick Start (build & run)

```bash
# 1) clone or create the project folder
cd streamlit-poetry-docker

# 2) build the image (first time or after dependency changes)
docker build -t streamlit-poetry .

# 3) run the container (opens app on http://localhost:8501)
docker run --rm -p 8501:8501 streamlit-poetry
```

App available at: http://localhost:8501

---

## 🛠️ Dev Mode (live reload, no rebuild on code changes)

Use a **bind mount** so Streamlit reloads automatically when you edit `.py` files:

```bash
docker run --rm -p 8501:8501 -v "$PWD":/app streamlit-poetry
```

Or with **Docker Compose** (recommended):

```yaml
# docker-compose.yml
version: "3.9"
services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - .:/app   # live code reload
    command: poetry run streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```

Run:

```bash
docker compose up --build   # first time
docker compose up           # subsequent runs (live reload on save)
```

**When do you need to rebuild?**
- When you change dependencies (`pyproject.toml` / `poetry.lock`)
- When you change system packages or the Dockerfile
- Otherwise, for Python code changes: **no rebuild needed**.

---

## ➕ Add/Update Dependencies (Poetry inside container)

Run Poetry **inside the image** so it updates your local `pyproject.toml` and `poetry.lock`:

```bash
# add a runtime dependency
docker run --rm -it -v "$PWD":/app streamlit-poetry poetry add requests

# add a dev-only dependency (example)
docker run --rm -it -v "$PWD":/app streamlit-poetry poetry add --group dev black
```

Then rebuild to bake them into the image:

```bash
docker build -t streamlit-poetry .
```

---

## 📁 Project Structure (minimal)

```
.
├─ app.py
├─ pyproject.toml
├─ poetry.lock            # generated after first install (optional to commit)
├─ Dockerfile
├─ docker-compose.yml     # optional, for dev convenience
└─ .dockerignore
```

**Example `app.py`:**
```python
import streamlit as st

st.set_page_config(page_title="Docker + Poetry + Streamlit", page_icon="🚀")
st.title("Hello from Docker + Poetry + Streamlit 🚀")
name = st.text_input("Your name")
if name:
    st.success(f"Welcome, {name}!")
```

---

## 🧱 Dockerfile (Poetry inside the image)

This variant installs dependencies as **root** (system site-packages), then runs as **non-root**:

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_HOME=/opt/poetry \
    PATH="/opt/poetry/bin:$PATH"

# System deps (add as needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

# Copy dependency files first (better layer caching)
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-interaction --no-ansi --no-root

# Copy source
COPY . .

# Drop privileges for runtime
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501
CMD ["poetry", "run", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
```

---

## 🧹 .dockerignore (recommended)

```
__pycache__/
*.pyc
*.pyo
*.pyd
.git
.gitignore
.streamlit/
.env
.venv/
```

---

## 🧪 Local Run Without Docker (optional)

If you really want to run locally:

```bash
# install Poetry locally once (macOS)
curl -sSL https://install.python-poetry.org | python3 -
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc

poetry install
poetry run streamlit run app.py
```

> Keep Python version in `pyproject.toml` aligned with the Docker base image (e.g., `python = "^3.11"`).

---

## ❓ Troubleshooting

- **`/bin/sh: 1: poetry: Permission denied`**  
  Ensure Poetry is installed into a world-readable path and in `PATH`. In the provided Dockerfile we set:
  - `POETRY_HOME=/opt/poetry`
  - `PATH="/opt/poetry/bin:$PATH"`
  Also, run `poetry install` **before** switching to a non-root user when installing to system site-packages.

- **Changes don’t appear while coding**  
  Run with a bind mount (compose `volumes: - .:/app`) so Streamlit reloads on save.

- **Need to rebuild or not?**  
  - Dependencies / Dockerfile / apt changes → **rebuild**  
  - Python code only → **no rebuild** (use bind mount)

---

## ✅ Commands Cheat Sheet

```bash
# build image
docker build -t streamlit-poetry .

# run (no live reload)
docker run --rm -p 8501:8501 streamlit-poetry

# run with live reload (mount source)
docker run --rm -p 8501:8501 -v "$PWD":/app streamlit-poetry

# compose (build first time)
docker compose up --build

# add dependency (updates pyproject + lock locally)
docker run --rm -it -v "$PWD":/app streamlit-poetry poetry add <package>

# rebuild after dependency changes
docker build -t streamlit-poetry .
```

---

Happy building! 🚀
