# Use a lightweight base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /code

# Copy the code and dependencies
COPY . /code

# Install necessary packages
RUN pip install -r requirements.txt

# Copy wait-for-it.sh into the container and make it executable
COPY wait-for-it.sh /code/wait-for-it.sh
RUN chmod +x /code/wait-for-it.sh

# Expose the port your app will run on
EXPOSE 8000

# Default command (can be overridden in docker-compose.yml)
CMD ["uvicorn", "scripts.run:app", "--host", "0.0.0.0", "--port", "8000"]
