import math
from typing import Tuple

import pandas as pd
from langchain_core.runnables.config import RunnableConfig
from langchain_openai import ChatOpenAI, OpenAI
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import (BarColumn, MofNCompleteColumn, Progress, TextColumn,
                           TimeElapsedColumn)

from safety_eval.configs import ModelConfig
from safety_eval.utils import console


def split_flow_control_params(inference_params: dict)-> Tuple[dict, dict]:
    control_flow = ["concurrency", "retries"]
    control_flow_params: dict = {key: inference_params[key] for key in control_flow if key in inference_params}
    pure_inference_params = {key: inference_params[key] for key in inference_params if key not in control_flow}
    return control_flow_params, pure_inference_params


def run_inference(
        model_config: ModelConfig, 
        dataset_content: pd.DataFrame,
        output_file: str
    ) -> None:
    """Performs inference on the candidate model

    Args:
        batch_size: The batch size for inference
        model_config_file: The Eval Tool model config file
        dataset_name: The name of the dataset. This is used to identify the column containing 
        the text
        dataset_content: The Pandas dataframe
        inference_params: The inference params passed to `model.generate_text`
        output_file: The name of the output file
    """
    control_flow_params, inference_params = split_flow_control_params(model_config.inference_params)
    if model_config.type == "completions":
        Client = OpenAI
    elif model_config.type == "chat":
        Client = ChatOpenAI
    else:
        raise ValueError(f"Unrecognised model type {model_config.type}.")
    candidate_model = Client(base_url=model_config.base_url, api_key=model_config.api_key, model=model_config.llm_name, **inference_params)
    model_output = []
    total = dataset_content.shape[0]
    batch_size = control_flow_params['concurrency']
    num_batches = math.ceil(total/batch_size)
    console.print(f"[bold red]Using inference params: {model_config.inference_params}\n")
    console.print(f"[bold red]Using model endpoint: {model_config.base_url}\n")

    status = console.status(f"[bold red]Generating model output")
    progress = Progress(TextColumn("[progress.description]{task.description}"), TimeElapsedColumn(), BarColumn(), MofNCompleteColumn())
    with Live(Panel(Group(status, progress)), console=console):
        task = progress.add_task("Progress", total=num_batches)
        for i in range(num_batches):
            batch = dataset_content.iloc[batch_size * i: batch_size * (i + 1)]
            user_inputs = [row["prompt"] for _, row in batch.iterrows()] # TODO: possibly parametrize "prompt" out. It's the same for aegis and wildguard now
            output = candidate_model.with_retry(stop_after_attempt=control_flow_params['retries']).batch(user_inputs, config=RunnableConfig(max_concurrency=batch_size))
            if isinstance(candidate_model, ChatOpenAI):
                output = [example.content for example in output]            
            model_output.extend(output)
            progress.update(task, advance=1)

    console.print("Model output generated", style="#0000d7")
    dataset_content['model_output'] = model_output
    dataset_content.to_csv(output_file, index=False)
