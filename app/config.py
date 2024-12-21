import os

class Config:
    SECRET_KEY = 'dev-key-12345'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
    GROQ_API_KEY = "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"