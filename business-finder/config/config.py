import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Google Places API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

# AWS S3
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

# OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') 