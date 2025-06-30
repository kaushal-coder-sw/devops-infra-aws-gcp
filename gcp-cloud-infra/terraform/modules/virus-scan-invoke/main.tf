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
  region  = "asia-south1" # e.g. "us-central1"
}

resource "google_cloud_run_v2_service" "function_service" {
  name     = "scanning-virus-with-clamav-service"
  location = "asia-south1"
  
  ingress = "INGRESS_TRAFFIC_ALL"

  lifecycle {
    create_before_destroy = true
  }

  template {
    containers {
      image = "asia-south1-docker.pkg.dev/virus_scan/virus_scan-repo/virus_scan_invoke_service:v0" # Replace with actual image path
    }

    # Optional: Set environment variables
    # env {
    #   name  = "ENV_VAR_NAME"
    #   value = "value"
    # }
  }

  # Optional: Allow unauthenticated invocations
  #ingress = "INGRESS_ALL" # Options: INGRESS_TRAFFIC_ALL, INGRESS_TRAFFIC_INTERNAL_ONLY, INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER

  # Optional: Define concurrency, memory, timeout, etc.
  # template {
  #   containers {
  #     ...
  #   }
  #   max_instance_count = 10
  #   timeout = "60s"
  #   service_account = "your-service-account@your-project-id.iam.gserviceaccount.com"
  # }
}

# Allow unauthenticated access if needed
resource "google_cloud_run_v2_service_iam_member" "noauth" {
  project        = "virus_scan"
  location       = google_cloud_run_v2_service.function_service.location
  name           = google_cloud_run_v2_service.function_service.name
  role           = "roles/run.invoker"
  member         = "allUsers"
}