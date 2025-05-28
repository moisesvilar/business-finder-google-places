import boto3
import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)

class S3Client:
    def __init__(self):
        """Inicializa el cliente de S3."""
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        
        if not all([self.aws_access_key, self.aws_secret_key, self.bucket_name]):
            raise ValueError("Faltan credenciales de AWS o nombre del bucket")
        
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key
        )
        
    def upload_file(self, file_path: str, s3_key: str) -> Optional[str]:
        """
        Sube un archivo a S3 y devuelve su URL.
        
        Args:
            file_path: Ruta local del archivo
            s3_key: Clave (path) en S3
            
        Returns:
            URL pública del archivo o None si hay error
        """
        try:
            self.s3.upload_file(file_path, self.bucket_name, s3_key)
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            return url
            
        except Exception as e:
            logging.error(f"Error al subir archivo a S3: {str(e)}")
            return None 