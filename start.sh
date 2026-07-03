#!/usr/bin/env bash
set -e

# Start the FastAPI backend on localhost so Streamlit (the public process)
# can call it via http://127.0.0.1:8000

echo "Starting backend on 127.0.0.1:8000"
uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Wait for backend health endpoint to become available.
for i in {1..20}; do
  echo "Waiting for backend to become healthy... ($i/20)"
  if python -c 'import urllib.request, sys; urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2); sys.exit(0)' 2>/dev/null; then
    echo "Backend is ready."
    break
  fi
  sleep 1
done

if ! python -c 'import urllib.request, sys; urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2); sys.exit(0)' 2>/dev/null; then
  echo "Backend failed to start." >&2
  kill "$BACKEND_PID" || true
  exit 1
fi

echo "Starting Streamlit on port ${PORT:-8501}"
exec streamlit run frontend/app.py --server.port ${PORT:-8501} --server.address 0.0.0.0 --server.headless true
