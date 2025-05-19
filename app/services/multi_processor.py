import os
from concurrent.futures import ThreadPoolExecutor
from app.utils.file_handler import extract_text
from app.services.cv_parser import CVParser


class MultiCVProcessor:
    def __init__(self, api_key, max_workers=3):
        self.parser = CVParser(api_key)
        self.max_workers = max_workers

    def process_single_cv(self, file_path):
        try:
            text = extract_text(file_path)
            result = self.parser.process_cv(text)
            return {
                "filename": os.path.basename(file_path),
                "status": "success",
                "data": result
            }
        except Exception as e:
            return {
                "filename": os.path.basename(file_path),
                "status": "error",
                "error": str(e)
            }

    def process_multiple_cvs(self, file_paths):
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.process_single_cv, path) for path in file_paths]

            for future in futures:
                try:
                    results.append(future.result())
                except Exception as e:
                    results.append({
                        "filename": "unknown",
                        "status": "error",
                        "error": str(e)
                    })

        return results