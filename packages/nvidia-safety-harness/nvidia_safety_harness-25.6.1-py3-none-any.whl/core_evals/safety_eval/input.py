import logging
import os
import pathlib
from typing import Optional

import yaml

from .api_dataclasses import Evaluation
from .utils import (
    MisconfigurationError,
    deep_update,
    dotlist_to_dict,
    is_package_installed,
)


def load_run_config(yaml_file: str) -> dict:
    """Load the run configuration from the YAML file.

    NOTE: The YAML config allows to override all the run configuration parameters.
    """
    with open(yaml_file, "r") as file:
        config = yaml.safe_load(file)
    return config


def parse_cli_args(args) -> dict:
    """Parse CLI arguments into the run configuration format.

    NOTE: The CLI args allow to override a subset of the run configuration parameters.
    """
    config = {
        "config": {},
        "target": {
            "api_endpoint": {},
        },
    }

    if args.eval_type:
        config["config"]["type"] = args.eval_type
    if args.output_dir:
        config["config"]["output_dir"] = args.output_dir
    if args.api_key_name:
        config["target"]["api_endpoint"]["api_key"] = args.api_key_name
    if args.model_id:
        config["target"]["api_endpoint"]["model_id"] = args.model_id
    if args.model_type:
        config["target"]["api_endpoint"]["type"] = args.model_type
    if args.model_url:
        config["target"]["api_endpoint"]["url"] = args.model_url

    overrides = parse_override_params(args.overrides)
    # "--overrides takes precedence over other CLI args (e.g. --model_id)"
    config = deep_update(config, overrides, skip_nones=True)
    return config


def parse_override_params(override_params_str: Optional[str] = None) -> dict:
    if not override_params_str:
        return {}

    # Split the string into key-value pairs, handling commas inside quotes
    pairs = []
    current_pair = ""
    in_quotes = False
    quote_char = None

    for char in override_params_str:
        if char in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = char
            current_pair += char
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
            current_pair += char
        elif char == "," and not in_quotes:
            pairs.append(current_pair.strip())
            current_pair = ""
        else:
            current_pair += char

    if current_pair:
        pairs.append(current_pair.strip())

    return dotlist_to_dict(pairs)


def get_framework_evaluations(
    filepath: str, run_config_cli_overrides: Optional[dict] = None
) -> tuple[str, str, list[Evaluation]]:
    framework = {}
    with open(filepath, "r") as f:
        framework = yaml.safe_load(f)

        framework_name = framework["framework"]["name"]
        pkg_name = framework["framework"]["pkg_name"]
        run_config_framework_defaults = framework["defaults"]

    evaluations = dict()
    for evaluation_dict in framework["evaluations"]:
        # Apply run config evaluation defaults onto the framework defaults
        run_config = deep_update(
            run_config_framework_defaults, evaluation_dict["defaults"], skip_nones=True
        )

        # Apply run config CLI overrides onto the framework+evaluation defaults
        # TODO(pj): This is a hack and we should only override the config of the evaluation
        #           that was picked in the CLI. Move it somehow one level up where we
        #           already have the evaluation picked.
        run_config = deep_update(
            run_config, run_config_cli_overrides or {}, skip_nones=True
        )

        evaluation = Evaluation(
            framework_name=framework_name,
            pkg_name=pkg_name,
            **run_config,
        )

        evaluations[evaluation_dict["defaults"]["config"]["type"]] = evaluation

    run_config_framework_defaults_with_cli = deep_update(
        run_config_framework_defaults, run_config_cli_overrides or {}, skip_nones=True
    )
    run_config_framework_defaults_with_cli["framework_name"] = framework_name
    run_config_framework_defaults_with_cli["pkg_name"] = pkg_name

    return framework_name, pkg_name, evaluations, run_config_framework_defaults_with_cli


def get_available_evaluations(
    run_config_cli_overrides: Optional[dict] = None,
) -> tuple[dict[str, dict[str, Evaluation]], dict[str, Evaluation]]:
    def_file = os.path.join(pathlib.Path(__file__).parent.resolve(), "framework.yml")
    if not os.path.exists(def_file):
        raise ValueError(f"Framework Definition File does not exists at {def_file}")

    framework_eval_mapping = (
        {}
    )  # framework name -> set of tasks   | used in 'framework.task' invocation
    eval_name_mapping = (
        {}
    )  # task name      -> set of tasks   | used in 'task' invocation

    logging.debug(f"Loading task definitions from file: {def_file}")
    (
        framework_name,
        pkg_name,
        framework_evaluations,
        run_config_framework_defaults_with_cli,
    ) = get_framework_evaluations(def_file, run_config_cli_overrides)
    if not is_package_installed(pkg_name):
        logging.warning(
            f"Framework {framework_name} is not installed. Skipping. Evaluations from this framework will not be available to run."
        )
    else:
        framework_eval_mapping[framework_name] = framework_evaluations
        eval_name_mapping.update(framework_evaluations)

    return (
        framework_eval_mapping,
        eval_name_mapping,
        run_config_framework_defaults_with_cli,
    )


def validate_evaluation(run_config_cli_overrides: dict) -> Evaluation:
    """Validates requested task through a dataclass. Additionally,
    handles creation of task folowing the logic:

    - evaluation type can be either 'framework.task' or 'task'
    - FDF stands for Framework Definition File

    1. If `framework_name.task_name` is available in FDF, use definition from FDF.
    2. If `framework_name.task_name` is *NOT* available in FDF, create a task out of default configuration specified in FDF.
    3. If `task_name` is available in FDF, use definition from FDF.
    3. If `task_name` is *NOT* available in FDF, raise error.

    Args:
        run_config_cli_overrides (dict): run configuration merged from config file and CLI

    Raises:
        MisconfigurationError: if eval type does not follow specified format
        MisconfigurationError: if provided framework is not available
        MisconfigurationError: if provided task is not available

    Returns:
        Task: requested task
    """
    # evaluation type can be either 'framework.task' or 'task'

    eval_type_components = run_config_cli_overrides["config"]["type"].split(".")
    if len(eval_type_components) == 2:  # framework.task invocation
        framework_name, evaluation_name = eval_type_components
    elif len(eval_type_components) == 1:  # task invocation
        framework_name, evaluation_name = None, eval_type_components[0]
    else:
        raise MisconfigurationError(
            "eval_type must follow 'framework_name.evaluation_name'. No additional dots are allowed."
        )

    (
        framework_evals_mapping,
        all_evals_mapping,
        run_config_framework_defaults_with_cli,
    ) = get_available_evaluations(run_config_cli_overrides)

    # framework.task invocation
    if framework_name:
        try:
            evals_mapping = framework_evals_mapping[framework_name]
        except KeyError:
            raise MisconfigurationError(
                f"Unknown framework {framework_name}. Frameworks available: {', '.join(framework_evals_mapping.keys())}"
            )

        # if task pointed through `framework.task` invocation is available in core-evals, use suggested config
        try:
            evaluation = evals_mapping[evaluation_name]
        except KeyError:
            evaluation = Evaluation(**run_config_framework_defaults_with_cli)
            # fix type and task to interpreted evaluation_name. This needs to be done after using default configuration
            evaluation.config.type = evaluation_name
            evaluation.config.params.task = evaluation_name
    else:  # task invocation
        evals_mapping = all_evals_mapping
        try:
            evaluation = evals_mapping[evaluation_name]
        except KeyError:
            raise MisconfigurationError(
                f"Unknown evaluation {evaluation_name}. Evaluations available: {', '.join(evals_mapping.keys())}"
            )

    logging.info(f"Invoked config:\n{str(evaluation)}")

    try:
        os.makedirs(evaluation.config.output_dir, exist_ok=True)
    except OSError as error:
        print(f"An error occurred while creating output directory: {error}")

    with open(os.path.join(evaluation.config.output_dir, "run_config.yml"), "w") as f:
        yaml.dump(evaluation.model_dump(), f)

    return evaluation
