import os
import sys
import subprocess
import datetime
from google.cloud import storage
from google.cloud import firestore

# ✅ Use ADC (Application Default Credentials)
storage_client = storage.Client()
firestore_client = firestore.Client()

# ✅ Known multi and dual regions
MULTI_REGIONS = ['us', 'eu', 'asia']
DUAL_REGIONS = ['nam4', 'eur4', 'asia1']
SINGLE_REGIONS = [
    'us-central1', 'us-east1', 'us-east4', 'us-west1', 'us-west2', 'us-west3', 'us-west4',
    'northamerica-northeast1', 'northamerica-northeast2',
    'southamerica-east1',
    'europe-west1', 'europe-west2', 'europe-west3', 'europe-west4', 'europe-west6',
    'europe-central2',
    'asia-east1', 'asia-east2', 'asia-northeast1', 'asia-northeast2', 'asia-northeast3',
    'asia-south1', 'asia-south2', 'asia-southeast1', 'asia-southeast2',
    'australia-southeast1', 'australia-southeast2',
    'me-central1', 'me-west1'
]

def scan_file(file_path):
    try:
        print(f"🔍 Scanning {file_path}...")
        result = subprocess.run(["clamscan", file_path], capture_output=True, text=True)
        print(f"ClamAV output:\n{result.stdout}")
        return "FOUND" in result.stdout
    except Exception as e:
        print(f"❌ Error scanning file {file_path}: {e}")
        return False

def download_file_from_gcs(bucket_name, file_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    download_path = f"/tmp/{file_name}"
    os.makedirs(os.path.dirname(download_path), exist_ok=True)
    blob.download_to_filename(download_path)
    return download_path

def get_bucket_region(bucket_name):
    bucket = storage_client.bucket(bucket_name)
    bucket.reload()
    return bucket.location.lower()

def find_quarantine_bucket(region):
    region = region.lower().strip()
    is_multi = region in MULTI_REGIONS
    is_dual = region in DUAL_REGIONS
    is_single = region in SINGLE_REGIONS

    for bucket in storage_client.list_buckets():
        name = bucket.name.lower()

        if 'quarantine' not in name:
            continue

        if is_multi and 'multiregion' in name:
            return bucket.name
        elif is_dual and 'dualregion' in name:
            return bucket.name
        elif is_single and region in name:
            return bucket.name

    return None

def quarantine_file(bucket_name, file_name, region):
    quarantine_bucket_name = find_quarantine_bucket(region)
    if not quarantine_bucket_name:
        print(f"❌ No quarantine bucket found for region '{region}'")
        return None

    try:
        source_bucket = storage_client.bucket(bucket_name)
        source_blob = source_bucket.blob(file_name)

        quarantine_blob_path = f'quarantine/{bucket_name}/{file_name}'
        quarantine_bucket = storage_client.bucket(quarantine_bucket_name)
        quarantine_blob = quarantine_bucket.blob(quarantine_blob_path)

        # Copy blob to quarantine bucket
        source_bucket.copy_blob(source_blob, quarantine_bucket, quarantine_blob.name)

        # Delete original from source bucket
        source_blob.delete()

        print(f"🚨 Infected file '{file_name}' quarantined in '{quarantine_bucket_name}'. Deleted from '{bucket_name}'.")

        # ✅ Direct metadata URL to quarantined file
        direct_url = (
            f"https://console.cloud.google.com/storage/browser/_details/"
            f"{quarantine_bucket_name}/{quarantine_blob_path}?project={storage_client.project}"
        )

        return direct_url

    except Exception as e:
        print(f"❌ Error quarantining file {file_name}: {e}")
        return None


def log_file_result(bucket_name, file_name, region, status, public_url=None):
    try:
        collection = firestore_client.collection('scanresults')
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        log_data = {
            'bucket_name': bucket_name,
            'file_name': file_name,
            'region': region,
            'timestamp': timestamp,
            'status': status
        }

        # ✅ Add quarantine URL if file is infected
        if status == 'infected' and public_url:
            log_data['quarantine_url'] = public_url

        # ✅ Log the data to Firestore
        collection.add(log_data)
        print(f"📝 Logged {status} file {file_name} to Firestore.")

    except Exception as e:
        print(f"❌ Error logging to Firestore: {e}")

def scan_bucket(bucket_name):
    try:
        region = get_bucket_region(bucket_name)
        bucket = storage_client.bucket(bucket_name)

        for blob in bucket.list_blobs():
            print(f"📁 Processing: {blob.name}")
            file_path = download_file_from_gcs(bucket_name, blob.name)

            if scan_file(file_path):
                print(f"⚠️ File {blob.name} is infected!")
                public_url = quarantine_file(bucket_name, blob.name, region)
                log_file_result(bucket_name, blob.name, region, "infected", public_url)
            else:
                print(f"✅ File {blob.name} is clean.")
                log_file_result(bucket_name, blob.name, region, "clean")
    except Exception as e:
        print(f"❌ Error scanning bucket: {e}")

if __name__ == "__main__":
    bucket_name = os.getenv('BUCKET_NAME')
    print(f"Bucket Name: {bucket_name}")
    if not bucket_name:
        raise ValueError("BUCKET_NAME is not set")
    print(f"Processing bucket: {bucket_name}")
    scan_bucket(bucket_name)