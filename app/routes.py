import zipfile
import traceback
from flask import Blueprint, request, jsonify, render_template, send_file
from app.services.cv_parser import CVParser
from app.utils.file_handler import save_file, extract_text, allowed_file, secure_filename
from app.config import Config
import os
import tempfile
import io
import json

main = Blueprint('main', __name__)
cv_parser = CVParser(api_key=Config.GROQ_API_KEY)

@main.route('/')
def home():
    return render_template('upload.html')

@main.route('/parse-cvs', methods=['POST'])
def parse_cvs():
    """Route pour traiter plusieurs CV et retourner une archive ZIP"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400

        files = request.files.getlist('files')
        if not files:
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400

        # Créer un dossier temporaire pour stocker les JSON
        with tempfile.TemporaryDirectory() as temp_dir:
            json_files = []

            for file in files:
                if file.filename == '' or not allowed_file(file.filename):
                    continue

                try:
                    # Sauvegarde temporaire
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    print(f"Fichier sauvegardé : {filepath}")

                    # Traitement
                    text = extract_text(filepath)
                    print(f"Texte extrait du fichier : {filename}")
                    cv_data = cv_parser.process_cv(text)
                    print(f"Données CV traitées : {cv_data}")

                    # Nom du fichier basé sur le nom détecté
                    person_name = cv_data.get('Full Name', 'inconnu').replace(' ', '_')
                    json_filename = f"cv_{person_name}.json"
                    json_path = os.path.join(temp_dir, json_filename)

                    # Sauvegarder le JSON
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(cv_data, f, ensure_ascii=False, indent=2)
                    print(f"JSON sauvegardé : {json_path}")

                    json_files.append(json_path)

                    # Nettoyage
                    os.remove(filepath)
                    print(f"Fichier temporaire supprimé : {filepath}")

                except Exception as e:
                    print(f"Erreur sur {file.filename}: {str(e)}")
                    traceback.print_exc()
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    continue

            if not json_files:
                return jsonify({'error': 'Aucun CV traité avec succès'}), 400

            # Créer l'archive ZIP en mémoire
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for json_file in json_files:
                    zipf.write(json_file, os.path.basename(json_file))
                    print(f"Fichier ajouté à l'archive : {json_file}")

            # Retourner le fichier ZIP
            zip_buffer.seek(0)
            return send_file(
                zip_buffer,
                mimetype='application/zip',
                as_attachment=True,
                attachment_filename='cv_results.zip'  # Utilisez attachment_filename au lieu de download_name
            )


    except Exception as e:
        print(f"Erreur globale : {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
