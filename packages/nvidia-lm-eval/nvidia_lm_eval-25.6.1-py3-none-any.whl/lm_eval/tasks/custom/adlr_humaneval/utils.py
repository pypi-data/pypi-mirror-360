import evaluate as hf_evaluate
from lm_eval.filters.sanitize import sanitize
from concurrent.futures import ThreadPoolExecutor

## run simple test to check code execution is enabled before model generation
# import os
# os.environ["HF_ALLOW_CODE_EVAL"] = "1"
# test_cases = ["assert add(2, 3)==5"]
# candidates = [["def add(a,b): return a+b\n\n"]]
# results = pass_at_k.compute(references=test_cases, predictions=candidates, k=[1])
# print(results)


## Evaluation functions
pass_at_k_fn = hf_evaluate.load("code_eval")


def pass_at_k(references, predictions, k: int):
    pass_at_k_results = pass_at_k_fn.compute(
        references=references,
        predictions=predictions,
        k=[k],
    )
    return pass_at_k_results[0][f"pass@{k}"]


def pass_at_1(references, predictions):
    return pass_at_k(references, predictions, k=1)


def pass_at_10(references, predictions):
    return pass_at_k(references, predictions, k=10)


def pass_at_50(references, predictions):
    return pass_at_k(references, predictions, k=50)


## Formatting functions
def build_text(doc):
    # we no longer follow Mistral's suggestion of adding a newline, it generally makes things worse
    return doc["prompt"]


def build_references(doc):
    return doc["test"] + "\n" + f"check({doc['entry_point']})"


def process_resp(resp, doc):
    """Helper function to sanitize responses with associated docs."""
    return [sanitize(doc["prompt"] + r, doc["entry_point"]) for r in resp]


def build_predictions(resps, docs, num_workers=32):
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(process_resp, resps, docs))
    return results


def no_sanitize_predictions(resps, docs):
    preds = []
    for resp, doc in zip(resps, docs):
        pred = [doc["prompt"] + r for r in resp]
        preds.append(pred)

    return preds
