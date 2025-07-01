# Dockerfile

# Use a base image with git and Node.js
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && \
    apt-get install -y git curl python3 python3-pip && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Set working directory
WORKDIR /app

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# copy pass on the docker container
COPY .env /app/.env

# Copy json_update_server.py into the container
COPY json_update_server.py /app/json_update_server.py

# Install python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

EXPOSE 3000

# Run entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
