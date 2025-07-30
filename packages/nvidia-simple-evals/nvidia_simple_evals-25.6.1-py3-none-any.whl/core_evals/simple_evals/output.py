import json
import pathlib
import re

from core_evals.simple_evals.api_dataclasses import EvaluationResult, MetricResult, Score, TaskResult


# This is the only required function
def parse_output(output_dir: str) -> EvaluationResult:
    # Only look for JSON files directly in the output directory, not recursively, otherwise e.g. cache files will be included.
    result_files = list(pathlib.Path(output_dir).glob("*.json"))
    if not result_files:
        raise FileNotFoundError("Failed to find `{task_name}.json` with metric.")
    if len(result_files) > 1:
        raise ValueError(
            "More than 1 `{task_name}.json` files found. `output_dir` must contain a single evaluation."
        )

    with open(result_files[0]) as fp:
        results = json.load(fp)

    task_name = results.pop("task_name")

    group_metric_names = ["score"]
    if "score_macro" in results:
        group_metric_names.append("score_macro")
    scores = {}
    for metric_name in group_metric_names:
        stats = {}
        full_stat_names = [k for k in results.keys() if k.startswith(f"{metric_name}:")]
        for full_stat_name in full_stat_names:
            if full_stat_name in results:
                m = re.match(".*:(.*)", full_stat_name)
                stat_name = m.group(1)
                if stat_name == "std":
                    stat_name = "stddev"
                stats[stat_name] = results.pop(full_stat_name)
        metric_type = "macro" if "macro" in metric_name == "score_macro" else "micro"
        scores[metric_type] = Score(
            value=results.pop(metric_name),
            stats=stats,
        )
    group_result = dict(
        metrics={
            "score": MetricResult(scores=scores)
        }
    )
    groups = {task_name: group_result}

    tasks = {}
    task_names = [key for key in results.keys() if ":" not in key]
    for task_name in task_names:
        full_stat_names = [k for k in results.keys() if k.startswith(f"{task_name}:")]
        stats = {}
        for full_stat_name in full_stat_names:
            m = re.match(".*:(.*)", full_stat_name)
            stat_name = m.group(1)
            stats[stat_name] = results.pop(full_stat_name)
        tasks[task_name] = TaskResult(
            metrics={
                "score": MetricResult(
                    scores={
                        "micro": Score(
                            value=results.pop(task_name),
                            stats=stats,
                        )
                    }
                )
            }
        )
    if not tasks:
        tasks = groups
    return EvaluationResult(groups=groups, tasks=tasks)
