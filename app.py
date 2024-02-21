from flask import Flask, jsonify, request
from google.cloud import storage
import datetime

app = Flask(__name__)


def generate_signed_url(bucket_name, blob_name):
    """Generates a v4 signed URL for accessing a blob."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        # This URL is valid for 15 minutes
        expiration=datetime.timedelta(minutes=15),
        # Allow GET requests using this URL.
        method="GET",
    )

    return url


@app.route('/generate-signed-url', methods=['GET'])
def get_signed_url():
    bucket_name = request.args.get('bucket_name')
    blob_name = request.args.get('blob_name')

    if not bucket_name or not blob_name:
        return jsonify({'error': 'Missing bucket_name or blob_name parameter'}), 400

    try:
        signed_url = generate_signed_url(bucket_name, blob_name)
        return jsonify({'signed_url': signed_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
