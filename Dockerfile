# One image for the setup job, the API and the Streamlit app (see docker-compose.yml).
FROM python:3.11-slim

# XGBoost and LightGBM need OpenMP.
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir -r requirements.txt
COPY sql ./sql
COPY api ./api
COPY app ./app
