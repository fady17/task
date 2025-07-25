
FROM python:3.10-slim


WORKDIR /app

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application source code
# This is simpler than copying directory by directory for a demo
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# It first applies database migrations for the 'app' module, then starts the server.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]