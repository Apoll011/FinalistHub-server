# Use a lightweight base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install required dependencies
RUN pip install --no-cache-dir fastapi[all] sqlalchemy uvicorn python-multipart

# Copy the project files to the image
COPY . /app/

EXPOSE 8000

# Set the entry point to run the application
CMD ["uvicorn", "main:app"]
