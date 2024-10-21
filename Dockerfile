
# Dockerfile

FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

COPY . /app

# Install system dependencies for rasterio, netCDF, and unzip
RUN apt-get update && apt-get install -y \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Run setup.py to populate the database
RUN python /app/setup.py

# Copy the rest of the application code
COPY . .

# Expose port 8000 for the FastAPI app
EXPOSE 8000

# Run the FastAPI app with Uvicorn, referencing app.main:app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]