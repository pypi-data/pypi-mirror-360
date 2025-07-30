import yaml

ALL_LANGS = {
    "ar": "arabic",
    "cs": "czech",
    "de": "german",
    "en": "english",
    "es": "spanish",
    "fr": "french",
    "hi": "hindi",
    "id": "indonesian",
    "it": "italian",
    "ja": "japanese",
    "ko": "korean",
    "nl": "dutch",
    "pt": "portugese",
    "ru": "russian",
    "th": "thai",
    "tr": "turkish",
    "vi": "vietnamese",
    "zh": "chinese",
}

if __name__ == "__main__":
    for lang_code, lang_name in ALL_LANGS.items():
        yaml_dict = {
            "include": "wikilingua_yaml",
            "task": f"wikilingua_{lang_name}",
            "dataset_name": lang_code,
        }

        file_save_path = f"wikilingua_{lang_code}.yaml"
        with open(file_save_path, "w", encoding="utf-8") as yaml_file:
            yaml.dump(
                yaml_dict,
                yaml_file,
                width=float("inf"),
                allow_unicode=True,
            )