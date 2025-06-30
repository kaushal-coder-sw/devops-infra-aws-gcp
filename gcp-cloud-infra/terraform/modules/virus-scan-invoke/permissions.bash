PROJECT_ID="cloudshielddevelopment"
SERVICE_ACCOUNT="development-service-account@cloudshielddevelopment.iam.gserviceaccount.com"

# Assign Cloud Run Admin role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/run.admin"

# Assign Cloud Functions Invoker role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/cloudfunctions.invoker"

# Assign Service Account User role (if using service account keys)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/iam.serviceAccountUser"

# Assign Cloud Run Viewer role (optional if needed)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/run.viewer"

# Assign Cloud Run Job Invoker role (to allow Cloud Run jobs to be triggered)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/run.jobsInvoker"
