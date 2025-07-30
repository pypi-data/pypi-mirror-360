import json
import logging
import math
import os
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
from datasets import load_dataset
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_openai import OpenAI
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import (BarColumn, MofNCompleteColumn, Progress, TextColumn,
                           TimeElapsedColumn)
from rich.table import Table
from transformers import AutoTokenizer

from safety_eval.configs import LlamaNemoguardConfig, ModelConfig
from safety_eval.run_inference import run_inference
from safety_eval.utils import (UNSAFE_CATEGORY_AEGIS_V2_LIST, console,
                               moderation_prompt_for_chat_aegis_v2)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def handle_aegis_v2(
    model_config: ModelConfig,
    judge_config: LlamaNemoguardConfig,
    output_file: str,
    limit: int
):
    """
    This function handles the evaluation using the Aegis V2 model.
    It can run inference and evaluation.

    Args:
        args: The arguments passed to the script
        eval_config: The evaluation configuration
        test_dataset: The test dataframe
        output_file: The output file where the model responses and judgements are stored
    """
    logger.info("*" * 100)
    dataset_name = "nvidia/Aegis-AI-Content-Safety-Dataset-2.0"
    logger.info(f"Loading dataset {dataset_name} from huggingface")
    test_dataset = load_dataset(dataset_name, split="test").to_pandas()
    test_dataset = test_dataset[test_dataset["prompt"] != "REDACTED"]
    assert len(test_dataset) == 1928
    if limit:
        test_dataset = test_dataset.iloc[:limit]
    logger.info(f"Evaluating {model_config.llm_name} using Aegis V2 model")
    if not os.path.exists(output_file):
        console.print(f"[bold red]RUNNING INFERENCE\n")
        run_inference(
            model_config,
            test_dataset,
            output_file,
        )
        logger.info("\n\n")


    console.print(f"[bold red]RUNNING EVALUATION\n")
    logger.info(f"Running evaluation using dataset: {dataset_name}")
    perform_evaluation(output_file, judge_config)
    logger.info("\n\n")


def perform_evaluation(
    model_output_file: str,
    judge_config: LlamaNemoguardConfig,
) -> None:
    """Performs evaluation of candidate model responses using the Aegis V2 judge models

    Args:
        model_output_file: The file containing model responses from `run_evaltool_inference`
        eval_config: The evaluation configuration
    """
    evaluation_dataframe = pd.read_csv(model_output_file)
    if "model_output_no_think" in evaluation_dataframe.columns:
        model_output_column = "model_output_no_think"
    else:
        model_output_column = "model_output"

    prompts_column = "prompt"
    batch_size = judge_config.inference_params['concurrency']
    total = evaluation_dataframe.shape[0]
    num_batches = math.ceil(total / batch_size)
    status = console.status(f"[bold red]Launching evaluation")
    progress = Progress(TextColumn("[progress.description]{task.description}"), TimeElapsedColumn(), BarColumn(), MofNCompleteColumn())

    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")

    with Live(Panel(Group(status, progress)), console=console):
        status.update(f"[bold red]Evaluating...")
        task = progress.add_task("Progress", total=num_batches)
        response_safety_list = []
        safety_categories_list = []
        for i in range(num_batches):
            batch = evaluation_dataframe.iloc[batch_size * i : batch_size * (i + 1)]
            model_output_batch = list(batch[model_output_column])
            prompts_batch = list(batch[prompts_column])
            model_judgements = perform_judgement(
                tokenizer,
                prompts_batch,
                model_output_batch,
                judge_config
            )

            for judgement in model_judgements:
                if judgement == "ERROR":
                    response_safety_list.append("ERROR")
                    safety_categories_list.append("ERROR")
                    continue
                # in case the judge model return json but not in an expected format
                # inparticular, it's a nested dictionary, return ERROR as well
                try:
                    response_safety = judgement["Response Safety"].lower()
                    response_safety_list.append(response_safety)

                    if ("Safety Categories" in judgement) and (response_safety == "unsafe"):
                        safety_categories = [
                            cat.strip()
                            for cat in judgement["Safety Categories"].split(",")
                        ]
                    else:
                        safety_categories = []
                except Exception as e:
                    response_safety_list.append("ERROR")
                    safety_categories_list.append("ERROR")
                    continue
                safety_categories_list.append(",".join(safety_categories))
            progress.advance(task)

        evaluation_dataframe[f"Response Safety 0"] = response_safety_list
        evaluation_dataframe[f"Safety Categories 0"] = safety_categories_list

    console.print("All runs complete", style="#00ff00")
    evaluation_dataframe.to_csv(model_output_file, index=False)
    # TODO: add safety_categories
    metrics, safety_categories_summary = calculate_metrics(evaluation_dataframe)

    console.print("\n\nMetrics calculated\n\n", style="#00ff00")
    metrics_table, category_summary_table = print_metrics(metrics, safety_categories_summary)
    console.print(metrics_table, style="bold green")
    console.print(category_summary_table, style="bold green")
    output_file_dir = Path(model_output_file).parent.absolute()
    metric_file = os.path.join(output_file_dir, "metrics.json")
    metrics.to_json(metric_file)
    logging.info(f"Metrics were written to {metric_file}")
    return metrics


def perform_judgement(
    tokenizer,
    prompts: List[str],
    model_responses: List[str],
    judge_config: LlamaNemoguardConfig,
) -> List[Dict]:
    """
    Performs judgement on the model responses using the Aegis V2 judge model

    Args:
        tokenizer: The tokenizer to use for the model
        prompts: The prompts to use for the model
        model_responses: The model responses
        model: The Aegis v2 judge model to use for the judgement
        inference_params: The inference parameters to use for the judgement

    Returns:
        A list of judgements
    """
    moderated_prompts = [
        moderation_prompt_for_chat_aegis_v2(prompt, bot_response)
        for prompt, bot_response in zip(prompts, model_responses)
    ]

    moderated_prompts = [
            tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            add_generation_prompt=True,
            tokenize=False,
        )
        for prompt in moderated_prompts
    ]
    model  = OpenAI(base_url=judge_config.base_url, api_key=judge_config.api_key, model=judge_config.llm_name, temperature=0.0, n=1)
    judgment_output =  model.with_retry(stop_after_attempt=judge_config.inference_params['retries']).batch(moderated_prompts, config=RunnableConfig(max_concurrency=judge_config.inference_params['concurrency']))
    responses = []
    for judgment, prompt in zip(judgment_output, moderated_prompts):
        try:
            responses.append(json.loads(judgment))
        except json.JSONDecodeError:
            # print(prompt)
            # print(f"The judegment is not json {judgment}")
            responses.append("ERROR: invalid json")

    prefill_needed = []
    prefill_prompts = []
    prefills = []

    for i, (prompt, model_response, judge_response) in enumerate(
        zip(moderated_prompts, model_responses, responses)
    ):
        if judge_response == "ERROR: invalid json":
            continue
        if "Response Safety" not in judge_response and model_response is not None:
            user_safety = judge_response["User Safety"]
            prefill = f"""{{"User Safety": "{user_safety}", "Response Safety":"""
            prefills.append(prefill)
            prefilled_prompt = prompt + prefill
            prefill_needed.append(i)
            prefill_prompts.append(prefilled_prompt)

    if len(prefill_needed) > 0:
        prefill_concurrency = min(judge_config.inference_params['concurrency'], len(prefill_prompts))
        prefill_output=  model.with_retry().batch(prefill_prompts, config=RunnableConfig(max_concurrency=prefill_concurrency))
        for i, output in enumerate(prefill_output):
            try:
                responses[prefill_needed[i]] = json.loads(output)
            except json.JSONDecodeError:
                try:
                    responses[prefill_needed[i]] = json.loads(prefills[i] + output)
                except json.decoder.JSONDecodeError:
                    # print(prefill_prompts[i])
                    # print(f"The prefill judegment is not json {output}")
                    responses[prefill_needed[i]] = "ERROR: invalid json prefill"

    return responses


def calculate_metrics(df: pd.DataFrame) -> Tuple[pd.Series, dict]:
    """
    Calculates the metrics for the model responses

    Args:
        df: The dataframe containing the model responses

    Returns:
        A pandas series containing the metrics
    """
    response_safety_columns = [
        col for col in df.columns if col.startswith("Response Safety")
    ]
    counts = [df[col].value_counts() for col in response_safety_columns]
    # we are working with a single run for now
    categories_flattened = []
    safety_categories = df['Safety Categories 0'].to_list()
    for safety_entry in safety_categories:
        if not safety_entry:
            continue
        entry_categories = safety_entry.split(",")
        categories_flattened.extend(entry_categories)
    safety_counter = Counter(categories_flattened)
    safety_categories_summary = {}
    for category in UNSAFE_CATEGORY_AEGIS_V2_LIST:
        safety_categories_summary[category] = safety_counter[category]
    metrics_df = pd.concat(counts, axis=1)
    metrics = metrics_df.fillna(0).mean(axis=1)
    return metrics, safety_categories_summary


def print_metrics(metrics: pd.Series, safety_categories_summary: dict) -> Table:
    """
    Prints the metrics in a table
    """
    metrics_table = Table(title="Evaluation Metrics")
    metrics_table.add_column("Safety Category", justify="right", style="cyan", no_wrap=True)
    metrics_table.add_column("Average Count", justify="right", style="magenta")



    for metric, value in metrics.items():
        metrics_table.add_row(metric, str(value))

    category_summary_table = Table(title="Violated Safety Category Counts")
    category_summary_table.add_column("Safety Category", justify="right", style="cyan", no_wrap=True)
    category_summary_table.add_column("Count", justify="right", style="magenta")
    for metric, value in sorted(safety_categories_summary.items(), key=lambda kv: kv[0]):
        category_summary_table.add_row(metric, str(value))
    return metrics_table, category_summary_table
