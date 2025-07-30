import datasets

def process_docs(dataset: datasets.Dataset) -> datasets.Dataset:
    """Filters dataset and sets the correct answer."""
    filtered_data = []
    for item in dataset:
        if item["error_type"] == "ok":
            correct_answer = item["answer"]
        elif item["error_type"] == "wrong_groundtruth" and item["correct_answer"]:
            try:
                correct_answer = int(item["correct_answer"])
            except ValueError:
                correct_answer = list("ABCD").index(item["correct_answer"])
        else:
            # multiple answers, bad questions, etc.
            continue
        filtered_data.append({
            "question": item["question"],
            "choices": item["choices"],
            "correct_answer": correct_answer,
        })

    return datasets.Dataset.from_list(filtered_data)