import yaml

LANG_NAMES = {
    'cs': 'Czech',
    'uk': 'Ukrainian',
    'de': 'German',
    'en': 'English',
    'he': 'Hebrew',
    'ja': 'Japanese',
    'ru': 'Russian',
    'zh': 'Chinese'
}

ALL_TRANSLATIONS = [
'cs-uk',
'de-en',
'en-cs',
'en-de',
'en-he',
'en-ja',
'en-ru',
'en-uk',
'en-zh',
'he-en',
'ja-en',
'ru-en',
'uk-en',
'zh-en',
]



if __name__ == "__main__":
    for lang_pair in ALL_TRANSLATIONS:
        target_language = LANG_NAMES[lang_pair.split('-')[1]]
        yaml_dict = {
            "include": "wmt23_yaml",
            "task": f"wmt23_{lang_pair}",
            "dataset_kwargs": {
                "data_files": {
                    "train": f"/datasets/wmt23/samples_{lang_pair}.json",
                    "test": f"/datasets/wmt23/test_{lang_pair}.json",
                },
            },
            "doc_to_text": f"What is the " + target_language + r" translation of the sentence: {{src}}?\n"
        }

        file_save_path = f"wmt23_{lang_pair}.yaml"
        with open(file_save_path, "w", encoding="utf-8") as yaml_file:
            yaml.dump(
                yaml_dict,
                yaml_file,
                width=float("inf"),
                allow_unicode=True,
            )