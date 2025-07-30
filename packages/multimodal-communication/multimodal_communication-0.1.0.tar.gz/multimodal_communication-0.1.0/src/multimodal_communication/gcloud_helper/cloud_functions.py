import pandas as pd
from google.cloud import storage
import pickle as pkl
import json
import warnings


class CloudHelper:
    """
    A class to more easily upload, download, and delete files from Google Cloud. Only to be used by the user of the computer,
    as credentials are tied to the computer user as explained below:

    When interacting with Google Cloud Client libraries, the library can auto-detect the
    credentials to use. Make sure the ADC credentials are downloaded on the personal device as outlined below

    //  set up ADC as described in https://cloud.google.com/docs/authentication/external/set-up-adc
    //  2. Replace the project variable.
    //  3. Make sure that the user account or service account that you are using
    //  has the required permissions. For this sample, you must have "storage.buckets.list".
    """

    def __init__(self, obj=None, path=None, project_id="inspiring-dryad-422903-c4"):
        # Initialize the class with object OR file_path attributes, so that we can work
        # with objects either from memory, or saved on the machine. Default values are set
        # to None so that the user can override whichever they choose.

        self.obj = obj
        self.path = path
        self.project_id = project_id

        # Connect to the gcloud client
        self.storage_client = storage.Client(project=self.project_id)

        if self.obj is not None and self.path is not None:
            raise ValueError("One of parameters 'object' and 'file_path' must be None")

        if not project_id:
            raise ValueError(
                "Input project_id must be provided in order to connect to client"
            )

    def upload_to_cloud_from_local(self, bucket_name, file_name):
        """
        Function to upload a file to Google Cloud. Can either upload objects from memory or saved
        on machine depending on user inputs of 'object' and 'file_path'

        Parameters
        --------------

        bucket_name: String
            The name of the bucket in the cloud storage project to upload the file to.

        file_name: String
            The name with which we would like the file to appear in the Cloud.

        file_path: String
            "local/path/to/file"

        """
        if self.path is not None and self.obj is None:  # If using local path
            # Locate the correct bucket
            bucket = self.storage_client.get_bucket(bucket_name)

            # Build the blob and send it to the bucket
            blob = bucket.blob(file_name)
            blob.upload_from_filename(self.path)

        elif type(self.obj) != type(None) and type(self.path) == type(
            None
        ):  # If using local memory
            # Locate the correct bucket
            bucket = self.storage_client.bucket(bucket_name)

            # Build the blob
            blob = bucket.blob(file_name)

            try:  # Works for Pandas DataFrames specifically
                blob.upload_from_string(self.obj.to_csv(), "text/csv")
            except AttributeError:  # If we are not uploading a df (ideally a dict)
                json_data = json.dumps(self.obj)
                blob.upload_from_string(json_data, content_type="application/json")

    def delete_from_cloud(self, bucket_name, file_name):
        """
        Function to deletes a blob from an existing Cloud Bucket.

        Parameters
        --------------
        project_id: String
          The project id of your Google Cloud project

        bucket_name: String
            The name of the bucket in the cloud storage project to delete the file from.

        file_name: String
            The name of the file within the bucket to delete.

        """
        # Connect to the gcloud client
        storage_client = storage.Client(project=self.project_id)

        # Locate the correct bucket
        bucket = storage_client.bucket(bucket_name)

        # Identify the blob and delete it
        blob = bucket.blob(file_name)
        blob.delete()

    def download_from_cloud(self, gs_filepath, file_type: str = "csv"):
        """
        Downloads a blob into memory given the bucket and subbucket info in filepath form.
        In the case that the filepath does not exist, return an empty DataFrame rather than an error.

        Parameters
        --------------
        gs_filepath: String
            A filepath-like string of the file in the Cloud, starting from the bucket_name. Do not include
            the 'gs:// prefix.

        """

        # Append the necessary 'gs//:' to the file path
        path = "gs://" + gs_filepath if "gs://" not in gs_filepath else gs_filepath

        # Files can be uploaded as either CSVs or JSON, so try pulling the file as both options
        if file_type == "csv":
            try:
                file = pd.read_csv(path)
            except:
                try:
                    file = pd.read_pickle(path)
                except FileNotFoundError:
                    warnings.warn(f"File Not Found @ {path}. Returning Empty df")
                    return pd.DataFrame()
        elif file_type == "pq":
            try:
                file = pd.read_parquet(path)
            except FileNotFoundError:
                warnings.warn(f"File Not Found @ {path}. Returning Empty df")
                return pd.DataFrame()
        else:
            try:
                file = pd.read_pickle(path)
            except FileNotFoundError:
                warnings.warn(f"File Not Found @ {path}. Returning Empty df")
                return pd.DataFrame()
        return file
