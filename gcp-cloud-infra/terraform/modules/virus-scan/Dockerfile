# Use an official Python base image
FROM python:3.10-slim

# Install necessary system packages
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    ca-certificates \
    apt-transport-https \
    lsb-release \
    clamav \
    clamav-daemon \
    clamav-freshclam \
    && rm -rf /var/lib/apt/lists/*

# Add Google Cloud SDK distribution URI as a package source
RUN curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
    > /etc/apt/sources.list.d/google-cloud-sdk.list

# Install Google Cloud SDK (includes gsutil)
RUN apt-get update && \
    apt-get install -y google-cloud-sdk && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app/virus_scan

# Copy requirements and install dependencies
COPY requirements.txt .

RUN python3 -m venv /root/gcp-env && \
    /root/gcp-env/bin/pip install --upgrade pip && \
    /root/gcp-env/bin/pip install -r requirements.txt

# Copy the rest of the app
COPY . .

# Update ClamAV database (run freshclam to get the latest virus definitions)
RUN freshclam

EXPOSE 8080

# Entrypoint script (ensure entrypoint.sh exists in your app directory and is executable)
RUN chmod +x entrypoint.sh

# Set the entrypoint to the script
ENTRYPOINT ["./entrypoint.sh"]
