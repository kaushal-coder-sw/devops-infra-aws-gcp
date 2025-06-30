terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.45.2"
    }
  }
  required_version = ">= 1.0"
}

provider "google" {
  project = "virus_scan"
  region  = "asia-south1" # e.g., "us-central1"
}

resource "google_cloud_run_v2_job" "function_job" {
  name     = "scanning-virus-with-clamav-job"
  location = "asia-south1"
  project  = "virus_scan"

  template {
    template {
      containers {
        image = "asia-south1-docker.pkg.dev/virus_scan/virus_scan-repo/virus_scan_job:v0" # Replace with the actual image path

        # Set environment variables
        env {
          name  = "ENV_VAR_1"
          value = "value1"
        }

        env {
          name  = "ENV_VAR_2"
          value = "value2"
        }

        env {
          name  = "ENV_VAR_3"
          value = "value3"
        }

        # Optional: Configure resource limits
        # resources {
        #   limits = {
        #     memory = "512Mi"
        #     cpu    = "1"
        #   }
        # }
      }

    }
  }
}
