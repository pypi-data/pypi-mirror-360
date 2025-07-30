"""Generate a config per subset."""
from datasets import get_dataset_config_names
import os

data_name = "edinburgh-dawg/mmlu-redux"

# List all configs for this dataset
configs = get_dataset_config_names(data_name)

# Generate YAML files in the current directory
for subset in configs:
    filename = f"mmlu_redux_{subset}.yaml"
    content = f"""
dataset_name: {subset}
include: _default_template_yaml
task: mmlu_redux_{subset}
task_alias: {subset}
    """.strip()

    with open(filename, "w") as file:
        file.write(content)

    print(f"Generated: {filename}")
