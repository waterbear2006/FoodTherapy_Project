# ==========================================
# Phase 1: Build the Vue 3 Frontend
# ==========================================
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY diet-health-frontend/package*.json ./
RUN npm install
COPY diet-health-frontend/ .
RUN npm run build

# ==========================================
# Phase 2: Setup Python Backend & Final Image
# ==========================================
FROM python:3.9-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Setup Backend
WORKDIR /app/Backened
COPY Backened/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend files
COPY Backened/ .

# Sync Frontend Build to Backend Static folder
# We defined 'dist_path = BASE_DIR / "static"' in main.py
RUN mkdir -p /app/Backened/static
COPY --from=frontend-builder /app/frontend/dist /app/Backened/static

# Expose the API and Frontend port
EXPOSE 8000

# Run the application
# Use 0.0.0.0 for external access within Docker
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
