import json


class Output:
    """
    Base class for output handlers.
    """

    def write(self, data, file_name) -> None:
        """
        Write data to the specified output.

        :param data: Data to be written.
        :param file_name: Name of the file to be created.
        :return: None
        """
        raise NotImplementedError("Subclasses should implement this method.")


class GCSOutput(Output):
    """
    Class to handle output to Google Cloud Storage (GCS).
    """

    def __init__(self, bucket_name, blob_path):
        """
        Initialize the GcsOutput with the bucket and blob names.

        :param bucket_name: Name of the GCS bucket.
        :param blob_path: Name of the blob in the GCS bucket.
        """
        self.bucket_name = bucket_name
        self.blob_path = blob_path

    def write(self, data, file_name) -> None:
        """
        Write data to the specified GCS bucket and blob.

        :param data: Data to be written to GCS.
        :param file_name: Name of the file to be created in GCS.
        :return: None
        """
        from google.cloud import storage

        client = storage.Client()
        bucket = client.bucket(self.bucket_name)
        blob_name = f"{self.blob_path}/{file_name}.json"
        blob = bucket.blob(blob_name)  # Create a blob object with the specified name

        blob.upload_from_string(data=json.dumps(data), content_type="application/json")  # Assuming data is a string
