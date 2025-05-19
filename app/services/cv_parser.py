import json
import time
from groq import Groq
import re


class CVParser:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        self.final_keys = {
            "Full Name": "",
            "Email Address": "",
            "Phone Number": "",
            "Level of Education": "",
            "Educational Institution": ""
        }

    def split_text(self, text, max_length=10000):
        return [text[i:i + max_length] for i in range(0, len(text), max_length)]

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
            # Prendre la première partie valide (ou fusionner si besoin)
            merged = structured_data[0]

            # Mapping vers les clés finales
            mapped = {
                "Full Name": merged.get("full_name", ""),
                "Email Address": merged.get("email", ""),
                "Phone Number": merged.get("phone", ""),
                "Level of Education": merged.get("education_level", ""),
                "Educational Institution": merged.get("educational_institution", "")
            }

            end_time = time.time()
            print("temps de traitement  : ", end_time - start_time)
            return mapped

        return self.final_keys

    def _create_instruction(self, text_part):
        return (
            '''Organisez et structurez les données issues du texte d'entrée dans un format JSON clair avec ces 5 champs uniquement :

- `full_name`
- `email`
- `phone`
- `education_level`
- `educational_institution`

**Règles** :
- Si un champ est manquant, mettez sa valeur à `null`.
- Ne retournez qu'un objet JSON valide, sans aucun autre texte. Exemple :

{
  "full_name": "Jean Dupont",
  "email": "jean.dupont@email.com",
  "phone": "+33 6 12 34 56 78",
  "education_level": "Master",
  "educational_institution": "Université de Paris"
}

Voici le texte à analyser :

''' + text_part
        )

    def _process_part(self, instruction, part_number):
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": instruction}],
                    model="llama-3.3-70b-versatile",
                )
                response = chat_completion.choices[0].message.content.strip()
                json_match = re.search(r"\{.*\}", response, re.DOTALL)

                if json_match:
                    json_content = json_match.group()
                    api_data = json.loads(json_content)

                    # Convertir les `null` en chaînes vides pour uniformité
                    cleaned_data = {k: (v if v is not None else "") for k, v in api_data.items()}
                    return cleaned_data

            except Exception as e:
                print(f"Erreur partie {part_number}, tentative {attempt + 1}: {str(e)}")
                time.sleep(2)
        return None
