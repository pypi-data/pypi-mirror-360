import os
import json
from core_evals.safety_eval.api_dataclasses import EvaluationResult, TaskResult, MetricResult, Score

def parse_output(output_dir):
    import yaml

    with open(os.path.join(output_dir, "run_config.yml")) as stream:
        results_yml = yaml.safe_load(stream)

    metrics_file = os.path.join(output_dir, 'metrics.json')
    with open(metrics_file, 'r') as file:
        data = json.load(file)
    print(data)
    tasks = {}
    safety_rate = data['safe'] / sum(data.values())
    tasks[results_yml['config']['type']] = TaskResult(
            metrics={
                "safety_rate": MetricResult(
                    scores={
                        "safety_rate": Score(
                            value=safety_rate,
                            stats={},
                        )
                    }
                )
            }
        )

    return EvaluationResult(groups=None, tasks=tasks)