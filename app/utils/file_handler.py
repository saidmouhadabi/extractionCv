import os
from werkzeug.utils import secure_filename
from app.config import Config
import fitz
from docx import Document


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def save_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # Créer le répertoire s'il n'existe pas
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)

        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        return filepath
    return None


def extract_text(file_path):
    """Extrait le texte d'un fichier PDF ou Word."""
    try:
        if file_path.endswith('.pdf'):
            with fitz.open(file_path) as pdf:
                text = ""
                for page in pdf:
                    text += page.get_text()
            return text
        elif file_path.endswith('.docx'):
            document = Document(file_path)
            text = ""
            for paragraph in document.paragraphs:
                text += paragraph.text + "\n"
            return text
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as txt_file:
                text = txt_file.read()
            return text
        else:
            raise ValueError("Format de fichier non pris en charge")
    except Exception as e:
        raise Exception(f"Erreur lors de l'extraction du texte : {str(e)}")
