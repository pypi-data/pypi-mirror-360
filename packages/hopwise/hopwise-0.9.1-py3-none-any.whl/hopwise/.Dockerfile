# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures that Python output is sent straight to terminal (useful for logging)
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt file for installing dependencies
COPY pyproject.toml .

# Install dependencies
RUN pip install --upgrade pip \
    && pip install uv
RUN uv pip install -r pyproject.toml --all-extras

# Copy the entire project into the working directory
COPY . .

# Expose a port (optional: replace with your app's port if it listens on a specific one)
# EXPOSE 8000

# Run the application (replace `your_script.py` with your project’s entry point)
# CMD ["python", "your_script.py"]
