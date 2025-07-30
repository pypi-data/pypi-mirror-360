"""caching utils
"""
import os

from evaluate import EvaluationModule


def update_hf_metric_lockfiles_permissions(metric: EvaluationModule) -> None:
    """By dfault hf metric create persistent .locks
    with permission granted only for user (640). This
    disables cache sharing.

    Args:
        metric (EvaluationModule): hf metric
    """
    if hasattr(metric, "filelocks"):
        for filelock in metric.filelocks:
            try:
                os.chmod(filelock.lock_file, 0o660)
            except FileNotFoundError:
                ...
