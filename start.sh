#!/usr/bin/env bash
set -e

# Start the FastAPI backend on localhost so Streamlit (the public process)
# can call it via http://127.0.0.1:8000

echo "Starting backend on 127.0.0.1:8000"
uvicorn backend.main:app --host 127.0.0.1 --port 8000 &

sleep 1

echo "Starting Streamlit on port ${PORT:-8501}"
streamlit run frontend/app.py --server.port ${PORT:-8501} --server.address 0.0.0.0 --server.headless true
