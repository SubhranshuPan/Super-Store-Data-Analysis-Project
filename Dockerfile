# Containerized SuperStore Sales Dashboard.
# Build:  docker build -t superstore-dashboard .
# Run:    docker run -p 8501:8501 superstore-dashboard
FROM python:3.11-slim

WORKDIR /app

# System deps: curl for the healthcheck only
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Only copy what the dashboard actually needs at runtime
COPY superstore/ superstore/
COPY data/ data/
COPY dashboard/ dashboard/
COPY .streamlit/ .streamlit/

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
