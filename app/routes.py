from flask import Blueprint, request, jsonify
from app.services.cv_parser import CVParser
from app.utils.file_handler import save_file, extract_text
from app.config import Config
import os

main = Blueprint('main', __name__)
cv_parser = CVParser(api_key=Config.GROQ_API_KEY)


@main.route('/parse-cv', methods=['POST'])
def parse_cv():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné  a omar'}), 400

        filepath = save_file(file)
        if not filepath:
            return jsonify({'error': 'Type de fichier non autorisé'}), 400

        try:
            text = extract_text(filepath)
            result = cv_parser.process_cv(text)

            # Nettoyer le fichier après traitement
            os.remove(filepath)

            return jsonify(result)
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            raise e

    except Exception as e:
        return jsonify({'error': str(e)}), 500
from flask import render_template

@main.route('/')
def home():
    return render_template('upload.html')
