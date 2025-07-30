import regex
import string

from rouge_score import rouge_scorer

def _normalize_answer(text):
    # NOTE(dfridman): copy-pase from lm_eval/tasks/nqopen.py
    # Lowercase and remove punctuation, strip whitespace
    text = text.strip().lower().translate(str.maketrans("", "", string.punctuation))

    # Remove articles, resulting in duplicate whitespace
    text = regex.sub(r"\b(a|an|the)\b", " ", text)

    # Remove duplicate whitespace
    text = " ".join(text.split())

    return text

def process_results(doc, results):
    rouge = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"])

    gt = _normalize_answer(doc["target"])
    pred = _normalize_answer(results[0])

    scores = rouge.score(gt, pred)
    scores = {
        metric_name: v.fmeasure for metric_name, v in scores.items()
    }
    return scores
