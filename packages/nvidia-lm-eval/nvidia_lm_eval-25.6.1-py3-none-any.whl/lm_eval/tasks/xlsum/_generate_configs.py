import yaml

ALL_LANGS = ['amharic',
    'arabic',
    'azerbaijani',
    'bengali',
    'burmese',
    'chinese_simplified',
    'chinese_traditional',
    'english',
    'french',
    'gujarati',
    'hausa',
    'hindi',
    'igbo',
    'indonesian',
    'japanese',
    'kirundi',
    'korean',
    'kyrgyz',
    'marathi',
    'nepali',
    'oromo',
    'pashto',
    'persian',
    'pidgin',
    'portuguese',
    'punjabi',
    'russian',
    'scottish_gaelic',
    'serbian_cyrillic',
    'serbian_latin',
    'sinhala',
    'somali',
    'spanish',
    'swahili',
    'tamil',
    'telugu',
    'thai',
    'tigrinya',
    'turkish',
    'ukrainian',
    'urdu',
    'uzbek',
    'vietnamese',
    'welsh',
    'yoruba',
]


if __name__ == "__main__":
    for lang_name in ALL_LANGS:
        yaml_dict = {
            "include": "xlsum_yaml",
            "task": f"xlsum_{lang_name}",
            "dataset_name": lang_name,
        }

        file_save_path = f"xlsum_{lang_name}.yaml"
        with open(file_save_path, "w", encoding="utf-8") as yaml_file:
            yaml.dump(
                yaml_dict,
                yaml_file,
                width=float("inf"),
                allow_unicode=True,
            )