import json
import time
from groq import Groq
import re


class CVParser:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        self.default_structure = {
            "name": "",
            "email": "",
            "phone": "",
            "age": None,
            "city": "",
            "work": [
                {
                    "job_title": "",
                    "company_name": "",
                    "responsibilities": "",
                    "city": "",
                    "start_date": "",
                    "end_date": "",
                    "environnement": "",
                    "context": ""
                }
            ],
            "yoe": "",
            "educations": [
                {
                    "degree": "",
                    "institution": "",
                    "start_year": "",
                    "end_year": ""
                }
            ],
            "languages": [
                {
                    "language": "",
                    "level": ""
                }
            ],
            "skills": [
                {
                    "skill": "",
                    "level": "",
                    "category": ""
                }
            ],
            "social": [
                {
                    "skill": ""
                }
            ],
            "certifications": [],
            "projects": [
                {
                    "project_name": "",
                    "description": "",
                    "start_date": "",
                    "end_date": ""
                }
            ],
            "volunteering": [],
            "references": [],
            "headline": "",
            "summary": "",
            "language": ""
        }

    def split_text(self, text, max_length=10000):
        return [text[i:i + max_length] for i in range(0, len(text), max_length)]

    def merge_structured_data(self, structured_data_list):
        if not structured_data_list:
            return self.default_structure

        merged_data = structured_data_list[0].copy()
        list_keys = ['work', 'educations', 'languages', 'skills',
                     'interests', 'social', 'certifications', 'projects',
                     'volunteering', 'references']

        for key in list_keys:
            merged_lists = []
            for data_part in structured_data_list:
                merged_lists.extend(data_part.get(key, []))

            unique_merged_lists = []
            seen = set()
            for item in merged_lists:
                item_str = json.dumps(item, sort_keys=True)
                if item_str not in seen:
                    seen.add(item_str)
                    unique_merged_lists.append(item)

            merged_data[key] = unique_merged_lists

        text_keys = ['name', 'email', 'phone', 'city', 'yoe',
                     'headline', 'summary', 'language']

        for key in text_keys:
            for data_part in structured_data_list:
                if data_part.get(key):
                    merged_data[key] = data_part[key]
                    break

        return merged_data

    def process_cv(self, text):
        text_parts = self.split_text(text)
        structured_data = []
        start_time = time.time()

        for i, part in enumerate(text_parts):
            print(f"Traitement de la partie {i + 1}/{len(text_parts)}...")
            instruction = self._create_instruction(part)
            processed_data = self._process_part(instruction, i + 1)
            if processed_data:
                structured_data.append(processed_data)

        if structured_data:
            final_data = self.merge_structured_data(structured_data)
            end_time = time.time()
            processing_time = end_time - start_time
            print("temps de traitement  : ",processing_time)
            return final_data  # Retourner uniquement l'objet JSON des données

        return self.default_structure

    def _create_instruction(self, text_part):
        return (
                "Organisez et structurez les données issues du texte d'entrée dans un format JSON clair et défini selon les directives suivantes :\n\n"
    "**Structure Générale :**\n"
    "- Les informations doivent être complètes et organisées sous un format JSON, même si certains champs sont absents.\n"
    "- Ne modifiez pas le contenu original (orthographe ou style).\n"
    "- Utilisez l'intégralité du texte disponible.\n\n"
    "**Règles de Mise en Forme :**\n"
    "- Les champs contenant des listes (ex. : expériences professionnelles, formations,éducation, ou similaires) doivent être formatés avec des balises HTML `<ul>` et `<li>`.\n"
    "**Structure JSON à respecter** :"
    "-------------------- skills & languages -------------------- "
  "- `skills` : Liste brute des compétences techniques('skill') et des category mentionnées similaire dans le texte et 'level', sans tentative de catégorisation ou regroupement par l'inteligence artificielle"
  "- `languages` : Liste des langues mentionnées dans le texte (langues de communication comme le Français, l'Anglais, etc.)."
  "**Règles d'extraction et de structuration** :"
  "- Identifier toutes les compétences techniques mentionnées (par exemple, langages de programmation, frameworks, outils, technologies,...)."
  "- Pour `skills`, si des catégories implicites existent, organiser les compétences sous ces catégories. "
  "Inclure uniquement les compétences techniques telles qu'elles sont mentionnées dans le texte, sans appliquer de regroupement ou de catégorisation."
  "- Identifier les langues de communication dans le texte et les inclure dans le champ `languages`"
  "- Ne pas modifier le contenu original (orthographe ou style ou texte)."
  "**Exclusions** :"
  "- Ignorer toute autre information qui ne relève pas des compétences techniques ou des langues (ex. : expériences professionnelles, projets, etc.)."
    "-------------------- work & yoe & langue-------------------- "
    "3. **Champs Spécifiques :**\n"
    "- `work` : contient les champs suivants :"
     "- `job_title` : Titre du poste ou rôle occupé complet."
     "- 'responsibilities' : Liste de toutes les missions ou tâches associées au projet, formatées en HTML avec `<ul>` et `<li> "
     "- `company_name` : Nom de l'entreprise."
     "- `city` : Ville où se trouve l'entreprise, si mentionnée."
     "- `start_date` : Date de début de l'expérience (exactement comme indiqué dans le texte)."
     "- `end_date` : Date de fin de l'expérience (exactement comme indiqué dans le texte)."
     "- `environnement` : Environnement technique détaillé (outils, technologies, méthodologies), si mentionné."
     "- `context` : Contexte ou description générale de l'expérience professionnelle."
    "**Règles d'extraction et de structuration** :"
   "- Extraire toutes les expériences professionnelles mentionnées dans le texte, dans l'ordre chronologique. et la mettre dans la section 'work'"
   "- Reproduire fidèlement le texte des champs extraits sans modification de l'orthographe ou du style."
   "- Les champs non mentionnés dans le texte doivent être laissés vides (null ou "")."
    "- **yoe (Years of Experience)** : Calculer le nombre total d’années d’expérience à partir des dates des expériences proffessionnelles.\n"
    "- **langue** : Identifier la langue principale utilisée dans le texte et la mentionner dans ce champ.\n"
    "-------------------- projects-------------------- "
    "- **projects** afficher si existe  :\n"
     "**Structure JSON à respecter pour la section projet** : "
    "- `project_name` : Le nom ou le titre du projet ou similaire "
    "- `description` : Une brève description du projet, comprenant son objectif ou son contexte. "
    "- `responsibilities` : Liste de toutes les missions ou tâches associées au projet, formatées en HTML avec `<ul>` et `<li> "
    "- `environnement` : Liste des technologies utilisées, telles que langages de programmation, outils, frameworks, ou patterns ou Liste des outils ou environnements utilisés pour le projet "
    "- `start_date` : La date de début du projet (si mentionnée). "
    "- `end_date` : La date de fin du projet (si mentionnée). "
    "-------------------- Social skill & headline & summary-------------------- "
    "- **Social skill** : Ajouter les compétences personnelles ou compétences clés ou similaire mentionnées sous ce champ.\n"
    "- **headline** : Extraire le titre ou le poste principal mentionné dans le texte.\n"
    "- **summary** : Inclure le résumé ou profil ou similaire de l'utilisateur si mentionné.\n\n"
    "4. **Instructions Spécifiques :**\n"
    "- Respecter strictement le texte fourni pour remplir les champs (aucune modification ou omission).\n"
    "- Les tâches mentionnées dans `responsibilities` doivent inclure toutes les responsabilités sans exception, formatées avec `<ul>` et `<li>`.\n"
    "- afficher seulement les expériences qui existent"
    "- afficher seulement les projets qui existent"
    "- Si un champ ou une section n’est pas mentionné(e) dans le texte, ne pas l’inclure dans le JSON.\n"
    "- Faire une extraction total du contenu. \n"
    "- laisser le contenu tel qu'il' est \n"
    "5. **Sortie :**\n"
    "- Retournez uniquement un objet JSON structuré, sans texte additionnel.\n"
                + json.dumps(self.default_structure, ensure_ascii=False, indent=4)
                + "\n\nVoici le texte :\n\n"
                + text_part
        )

    def _process_part(self, instruction, part_number):
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": instruction}],
                    model="llama3-70b-8192",
                )
                response = chat_completion.choices[0].message.content.strip()
                json_match = re.search(r"\{.*\}", response, re.DOTALL)

                if json_match:
                    json_content = json_match.group()
                    api_data = json.loads(json_content)
                    return {**self.default_structure, **api_data}
            except Exception as e:
                print(f"Erreur partie {part_number}, tentative {attempt + 1}: {str(e)}")
                if attempt < max_attempts - 1:
                    time.sleep(2)
        return None
