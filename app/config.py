import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')  # Ajoute aussi la clé secrète
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'default_api_key')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
