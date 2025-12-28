import boto3
import os
from botocore.exceptions import ClientError
from typing import Optional

class S3Client:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.s3 = boto3.client('s3')

    def upload_file(self, file_path: str, object_name: Optional[str] = None) -> bool:
        """
        Uploads a file to an S3 bucket.

        Args:
            file_path (str): File to upload
            object_name (str): S3 object name. If not specified, file_path is used

        Returns:
            bool: True if file was uploaded, else False
        """
        if object_name is None:
            object_name = os.path.basename(file_path)

        try:
            self.s3.upload_file(file_path, self.bucket_name, object_name)
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return False
        return True

    def download_file(self, object_name: str, file_path: str) -> bool:
        """
        Downloads a file from an S3 bucket.
        
        Args:
            object_name (str): S3 object name to download
            file_path (str): Local path to save the file
            
        Returns:
            bool: True if file was downloaded, else False
        """
        try:
            self.s3.download_file(self.bucket_name, object_name, file_path)
        except ClientError as e:
            print(f"Error downloading file from S3: {e}")
            return False
        return True
