# Use a lightweight base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install required dependencies
RUN pip install --no-cache-dir fastapi[all] sqlalchemy uvicorn python-multipart python-jose[cryptography] PyJWT passlib sqlitecloud sqlalchemy-sqlitecloud

# Copy the project files to the image
COPY . /app/

EXPOSE 80

# Set the entry point to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
