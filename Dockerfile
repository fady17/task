# 1. Use an official Python 3.10 runtime as a parent image
FROM python:3.10-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Copy the requirements file and install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of your application code into the container
COPY ./alembic /app/alembic
COPY ./app /app/app
COPY alembic.ini .

# 5. Copy the entrypoint script and make it executable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# 6. Set the entrypoint for the container
ENTRYPOINT ["/app/entrypoint.sh"]

# 7. Define the default command to run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]