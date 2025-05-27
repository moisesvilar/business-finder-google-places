import boto3
from botocore.exceptions import ClientError
import os
import sys

# Añadir el directorio raíz al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME

# DEBUG: Mostrar valores cargados
def _debug_env():
    print("AWS_ACCESS_KEY_ID:", AWS_ACCESS_KEY_ID)
    print("AWS_SECRET_ACCESS_KEY:", AWS_SECRET_ACCESS_KEY)
    print("S3_BUCKET_NAME:", S3_BUCKET_NAME)

_debug_env()

class S3Client:
    def __init__(self, region_name: str = "eu-west-1"):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=region_name
        )
        self.bucket = S3_BUCKET_NAME

    def upload_file(self, local_path: str, s3_key: str, public: bool = True) -> str:
        """
        Sube un archivo a S3 y devuelve la URL pública.
        """
        try:
            self.s3.upload_file(local_path, self.bucket, s3_key)
            url = f"https://{self.bucket}.s3.amazonaws.com/{s3_key}"
            return url
        except ClientError as e:
            print(f"Error al subir a S3: {e}")
            return ""
        except Exception as e:
            print(f"Error inesperado al subir a S3: {e}")
            return "" 