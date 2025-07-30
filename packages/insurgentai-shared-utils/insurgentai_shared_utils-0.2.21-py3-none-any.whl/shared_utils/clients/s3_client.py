import boto3

class S3Client: # Singleton class, wrapper for S3 operations

    def __init__(self, region_name:str='us-east-1'):
        session = boto3.Session()
        self.s3 = session.client('s3', region_name=region_name)

    def upload_file(self, local_file_path:str, bucket_name:str, s3_key:str) -> bool:
        """Uploads a file to an S3 bucket.
        Example:
            client.upload_file('local_file.txt', 'my-bucket', 'folder/remote_file.txt')
        """
        try:
            self.s3.upload_file(local_file_path, bucket_name, s3_key)
            return True
        except Exception as e:
            print(f"Upload failed: {e}")
            return False

    def download_file(self, bucket_name:str, s3_key:str, local_file_path:str) -> bool:
        """Downloads a file from an S3 bucket.
        Example:
            client.download_file('my-bucket', 'folder/remote_file.txt', 'downloaded_file.txt')
        """
        try:
            self.s3.download_file(bucket_name, s3_key, local_file_path)
            return True
        except Exception as e:
            print(f"Download failed: {e}")
            return False
        
s3_client = S3Client()  # module level singleton instance