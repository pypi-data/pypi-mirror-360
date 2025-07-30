import json
from typing import Dict

from resource.file_operator import FileOperator


class JsonFileOperator(FileOperator[Dict]):
    @classmethod
    def file_suffix(cls) -> str:
        return "json"

    def load(self):
        with open(self.path, "r", encoding="utf-8") as f:
            self.set_data(json.load(f))

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.get_data(), f, ensure_ascii=False, indent=2)
