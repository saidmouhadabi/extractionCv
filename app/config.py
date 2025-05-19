import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-12345')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', 'default_api_key')
