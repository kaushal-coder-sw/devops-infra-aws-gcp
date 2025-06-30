from flask import Flask, request
import logging
import subprocess
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def trigger_job():
    # Get the parameters from the request
    bucket_name = request.args.get("BUCKET_NAME")

    logging.info(f"Received request - Bucket: {bucket_name}")
    if not bucket_name:
        logging.error("Missing BUCKET_NAME parameter")
        return "❌ Missing BUCKET_NAME", 400

    try:

        # Cloud Run Job configuration - using the job_name from the first file
        job_name = "scanning-virus-with-clamav-job"
        region = "asia-south1"

        logging.info(f"🚀 Triggering Cloud Run Job: {job_name} for bucket: {bucket_name}")
        
        # Prepare environment variables
        env_vars = f"BUCKET_NAME={bucket_name}"

        # Execute the Cloud Run job with all parameters
        result = subprocess.run([
            "gcloud", "beta", "run", "jobs", "execute", job_name,
            f"--region={region}",
            f"--args={bucket_name}",
            f"--project=cloudshielddevelopment",
            "--update-env-vars", env_vars
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        logging.info(f"Cloud Run job triggered successfully: {result.stdout.decode()}")
        if result.stderr:
            logging.error(f"Cloud Run job execution errors: {result.stderr.decode()}")

        # Return success response
        return f"✅ Scan job '{job_name}' triggered for bucket: {bucket_name}", 200

    except subprocess.CalledProcessError as e:
        # Log the full error output including stderr and stdout from subprocess
        logging.error(f"❌ Error triggering job: {e}")
        logging.error(f"Subprocess stdout: {e.stdout.decode() if e.stdout else 'No stdout'}")
        logging.error(f"Subprocess stderr: {e.stderr.decode() if e.stderr else 'No stderr'}")

        return f"❌ Failed to trigger job: {str(e)}\nStdout: {e.stdout.decode() if e.stdout else 'No stdout'}\nStderr: {e.stderr.decode() if e.stderr else 'No stderr'}", 500

if __name__ == "__main__":
    # Use waitress for production-ready deployment
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)