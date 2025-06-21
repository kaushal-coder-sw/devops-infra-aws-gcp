#!/bin/bash
set -e

# Default GCS script location — override with `-e GCS_SCRIPT_URI=...` during docker run
GCS_SCRIPT_URI="${GCS_SCRIPT_URI:-gs://bucketname/virus_scan.py}"

# Set GCP credentials (assumes key is mounted via Docker volume)
export GOOGLE_APPLICATION_CREDENTIALS="/app/virus_scan/virus_scan-31701dfb1af9.json"

# Activate Python virtual environment
source /root/gcp-env/bin/activate

# Ensure required Python packages are installed
pip install --upgrade google-cloud-storage google-cloud-firestore

# Validate script URI
if [ -z "$GCS_SCRIPT_URI" ]; then
  echo "❌ Error: GCS_SCRIPT_URI is not set."
  echo "➡️ Set it in Docker run: -e GCS_SCRIPT_URI=gs://your-bucket/script.py"
  exit 1
fi

# Authenticate with gcloud using service account
gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"

# Prepare file path
SCRIPT_NAME=$(basename "$GCS_SCRIPT_URI")
SCRIPT_PATH="/app/virus_scan/${SCRIPT_NAME}"

echo "📥 Downloading latest scanner script from: $GCS_SCRIPT_URI"

# Fetch latest script from GCS
gsutil cp "$GCS_SCRIPT_URI" "$SCRIPT_PATH"

# Make it executable
chmod +x "$SCRIPT_PATH"

echo "🚀 Executing scanner script with args: $@"
python3 "$SCRIPT_PATH" "$@"

