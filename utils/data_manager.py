import json, os

class DataManager:
    @staticmethod
    def salvar_json(data, arquivo):
        os.makedirs(os.path.dirname(arquivo), exist_ok=True)
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def carregar_json(arquivo, default=None):
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default if default is not None else []
