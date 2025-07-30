import json
import pathlib

from core_evals.bigcode_evaluation_harness.api_dataclasses import EvaluationResult



def parse_output(output_dir: str) -> EvaluationResult:
    metrics_filepath = pathlib.Path(output_dir) / "metrics.json"
    if not metrics_filepath.exists():
        raise FileNotFoundError("Failed to find `metrics.json`.")
    with open(metrics_filepath) as fp:
        results = json.load(fp)
    del results["config"]

    tasks = {}
    for task_name, task_metrics in results.items():
        metrics = {}
        for metric_name, metric_value in task_metrics.items():
            if "stderr" in metric_name:
                continue
            stderr_name = f"{metric_name}_stderr"
            stats = {}
            if stderr_name in task_metrics:
                stats["stderr"] = task_metrics[stderr_name]
            metric_result = dict(
                scores={
                    metric_name: dict(value=metric_value, stats=stats)
                }
            )
            metrics[metric_name] = metric_result
        task_result = dict(metrics=metrics)
        tasks[task_name] = task_result
    evaluation_result = EvaluationResult(
        tasks=tasks,
        groups=tasks  # NOTE(dfridman): currently no support for aggregated metrics (e.g. Multipl-E)
    )
    return evaluation_result
