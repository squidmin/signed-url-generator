from flask import Flask, jsonify, request
from flask_cors import CORS
from google.cloud import storage, secretmanager
from google.oauth2 import service_account
import datetime
import json

app = Flask(__name__)
# This enables CORS for all domains on all routes. For high-stakes production deployments,
# you might want to restrict this.
CORS(app)


def get_service_account_credentials(project_id, secret_id):
    """Fetches service account key from Google Cloud Secrets Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    secret_string = response.payload.data.decode("UTF-8")
    credentials_json = json.loads(secret_string)
    credentials = service_account.Credentials.from_service_account_info(credentials_json)
    return credentials


def generate_signed_url(bucket_name, blob_name, project_id, secret_id):
    """Generates a v4 signed URL for accessing a blob using secret-based credentials."""
    credentials = get_service_account_credentials(project_id, secret_id)
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(minutes=15),
        method="GET",
        credentials=credentials  # Use the credentials fetched from Secrets Manager
    )

    return url


@app.route('/generate-signed-url', methods=['GET'])
def get_signed_url():
    bucket_name = request.args.get('bucket_name')
    blob_name = request.args.get('blob_name')
    project_id = request.args.get('project_id')
    secret_id = request.args.get('secret_id')

    if not bucket_name or not blob_name or not project_id or not secret_id:
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        signed_url = generate_signed_url(bucket_name, blob_name, project_id, secret_id)
        return jsonify({'signed_url': signed_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
