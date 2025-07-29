from datapipelab.app.node.tnode import TNode
from datapipelab.logger import logger

class GCPBucketAPINode(TNode):
    def __init__(self, spark, tnode_config):
        super().__init__(spark=spark)
        self.node_name = tnode_config['name']
        self.credentials_path = tnode_config['options']['credentials_path']
        self.project_name = tnode_config['options']['project_name']
        self.bucket_name = tnode_config['options']['bucket_name']
        self.prefix = tnode_config['options'].get('subdirectory', None)  # Optional subdirectory (prefix) to delete

    def __delete_gcs_folder(self, bucket_name, prefix=None):
        from google.cloud import storage
        from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_file(self.credentials_path)
        client = storage.Client(credentials=credentials, project=self.project_name)

        bucket = client.bucket(bucket_name)

        if prefix:
            # Delete only objects under the prefix (subfolder)
            blobs = bucket.list_blobs(prefix=prefix)
            deleted = False
            for blob in blobs:
                blob.delete()
                deleted = True
            if deleted:
                logger.info(f"Deleted all objects under prefix '{prefix}' in bucket '{bucket_name}'.")
            else:
                logger.info(f"No objects found under prefix '{prefix}' in bucket '{bucket_name}'.")
        else:
            # Delete the entire bucket (must be empty)
            try:
                bucket.delete(force=True)  # force=True to delete non-empty bucket
                logger.info(f"Bucket '{bucket_name}' deleted.")
            except Exception as e:
                logger.info(f"Error deleting bucket '{bucket_name}': {e}")

    def _process(self):
        self.__delete_gcs_folder(self.bucket_name, self.prefix)
        return None
