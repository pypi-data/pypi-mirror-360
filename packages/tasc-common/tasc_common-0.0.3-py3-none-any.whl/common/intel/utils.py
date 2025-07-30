import os
import re
from contextlib import contextmanager
from typing import Any

import numpy as np
import openai
import ruptures as rpt
import tiktoken
from packaging import version

from common.utils import get_path, format_string
from common.config import common_settings


def parse_prompts(input_data) -> tuple[str, str | None]:
    # Check if the input is a file path
    if os.path.exists(input_data):
        with open(input_data) as file:
            markdown_text = file.read()
    else:
        markdown_text = input_data

    # Use a regular expression to split on ':::user' only when it is on a line by itself
    parts = re.split(r"\n\s*:::user\s*\n", markdown_text, maxsplit=1)

    # Strip leading and trailing whitespace from each part
    system_prompt = parts[0].strip()
    user_prompt = parts[1].strip() if len(parts) > 1 else None

    return system_prompt, user_prompt


OPENAI_MODELS = {
    "gpt-3.5-turbo-0125",
    "gpt-4",
    "gpt-4-turbo-2024-04-09",
    "gpt-4o-2024-05-13",
    "gpt-4-0125-preview",
    "gpt-4-1106-preview",
    "gpt-4-vision-preview",
}

TOGETHER_COMPUTE_MODELS = {
    "mistralai/Mistral-7B-Instruct-v0.2",
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
}

ANTHROPIC_MODELS = [
    "claude-3-5-sonnet-20240620",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022",
    "claude-sonnet-4-20250514",
    "claude-opus-4-20250514",
]

DEFAULT_FLAGSHIP_MODEL = common_settings.DEFAULT_FLAGSHIP_MODEL
DEFAULT_VISION_MODEL = common_settings.DEFAULT_FLAGSHIP_VISION_MODEL  # Deprecated
DEFAULT_FLAGSHIP_VISION_MODEL = common_settings.DEFAULT_FLAGSHIP_VISION_MODEL

DEFAULT_FAST_LONG_CONTEXT_MODEL = common_settings.DEFAULT_FAST_LONG_CONTEXT_MODEL
DEFAULT_FAST_MODEL = common_settings.DEFAULT_FAST_LONG_CONTEXT_MODEL
DEFAULT_FLAGSHIP_LONG_CONTEXT_MODEL = common_settings.DEFAULT_FLAGSHIP_MODEL

DEFAULT_SMALL_EMBEDDING_MODEL = common_settings.DEFAULT_SMALL_EMBEDDING_MODEL
DEFAULT_LARGE_EMBEDDING_MODEL = common_settings.DEFAULT_LARGE_EMBEDDING_MODEL

DEFAULT_TOKENIZER_MODEL = "gpt-4"

TOKENIZER_MODEL_MAPS = {
    "mistralai/Mistral-7B-Instruct-v0.2": "gpt-4",
    "mistralai/Mixtral-8x7B-Instruct-v0.1": "gpt-4",
    "gpt-4-0125-preview": "gpt-4",
    "gpt-4-1106-preview": "gpt-4",
    "gpt-4-turbo-2024-04-09": "gpt-4",
    "gpt-4o-2024-05-13": "gpt-4",
    "gpt-4o-mini-2024-07-18": "gpt-4",
    "claude-3-5-sonnet-20240620": "gpt-4",
    "claude-sonnet-4-20250514": "gpt-4",
    "claude-opus-4-20250514": "gpt-4",
}

CONTEXT_LENGTHS = {
    "gpt-3.5-turbo-0125": 16384,
    "gpt-4": 8192,
    "gpt-4-1106-preview": 32768,
    "gpt-4-0125-preview": 32768,
    "gpt-4-turbo-2024-04-09": 32768,
    "gpt-4o-2024-05-13": 65536,
    "gpt-4o-mini-2024-07-18": 65536,
    "gpt-4-vision-preview": 32768,
    "mistralai/Mistral-7B-Instruct-v0.2": 32768,
    "mistralai/Mixtral-8x7B-Instruct-v0.1": 32768,
    "claude-3-5-sonnet-20240620": 65536,
    "claude-sonnet-4-20250514": 65536,
    "claude-opus-4-20250514": 65536,
}

DEFAULT_CONTEXT_LENGTH_FALLBACKS = {
    "gpt-4": "gpt-4-turbo-2024-04-09",
}


def encode(text: str, model_name: str | None = None) -> list[int]:
    model_name = TOKENIZER_MODEL_MAPS.get(model_name, DEFAULT_TOKENIZER_MODEL)
    encoding = tiktoken.encoding_for_model(model_name)
    return encoding.encode(text, allowed_special=encoding.special_tokens_set)


def decode(tokens: list[int], model_name: str | None = None) -> str:
    model_name = TOKENIZER_MODEL_MAPS.get(model_name, DEFAULT_TOKENIZER_MODEL)
    return tiktoken.encoding_for_model(model_name).decode(tokens)


def count_tokens_in_str(text: str, model_name: str | None = None) -> int:
    assert isinstance(text, str)
    return len(encode(text, model_name=model_name))


def num_tokens_from_functions(
    functions: list[dict[str, Any]], model_name: str = DEFAULT_TOKENIZER_MODEL
):
    """Return the number of tokens used by a list of functions."""
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    num_tokens = 0
    for function in functions:
        function_tokens = len(encoding.encode(function["name"]))
        function_tokens += len(encoding.encode(function["description"]))

        if "parameters" in function:
            parameters = function["parameters"]
            if "properties" in parameters:
                for propertiesKey in parameters["properties"]:
                    function_tokens += len(encoding.encode(propertiesKey))
                    v = parameters["properties"][propertiesKey]
                    for field in v:
                        if field == "type":
                            function_tokens += 2
                            function_tokens += len(encoding.encode(v["type"]))
                        elif field == "description":
                            function_tokens += 2
                            function_tokens += len(encoding.encode(v["description"]))
                        elif field == "enum":
                            function_tokens -= 3
                            for o in v["enum"]:
                                function_tokens += 3
                                function_tokens += len(encoding.encode(o))
                function_tokens += 11

        num_tokens += function_tokens

    num_tokens += 12
    return num_tokens


def clip_text(
    text: str,
    num_tokens: int,
    model_name: str = DEFAULT_TOKENIZER_MODEL,
    add_truncation_marker: bool = True,
) -> str:
    if text is None:
        return None
    tokens = encode(text, model_name)
    if len(tokens) <= num_tokens:
        return text
    if add_truncation_marker:
        truncation_marker = "[...]"
        num_tokens -= count_tokens_in_str(truncation_marker, model_name)
        return decode(tokens[:num_tokens], model_name) + " " + truncation_marker
    else:
        return decode(tokens[:num_tokens], model_name)


@contextmanager
def using_openai_credentials(api_key: str | None = None, endpoint: str | None = None):
    old_api_key = openai.api_key
    old_endpoint = openai.api_base
    if api_key is not None:
        openai.api_key = api_key
    if endpoint is not None:
        openai.api_base = endpoint
    yield
    openai.api_key = old_api_key
    openai.api_base = old_endpoint


def get_endpoint_and_key_for_model(
    model_name: str,
) -> tuple[str | None, str | None]:
    if model_name in OPENAI_MODELS:
        return None, None
    if model_name in TOGETHER_COMPUTE_MODELS:
        from common.config import settings

        return (
            "https://api.together.xyz",
            settings.TOGETHER_COMPUTE_API_KEY,
        )
    raise ValueError(f"Model {model_name} not found")


def to_normed_array(x: list[float] | list[list[float]]) -> np.ndarray:
    x = np.array(x)
    if x.ndim == 2:
        return x / np.linalg.norm(x, axis=1, keepdims=True)
    else:
        return x / np.linalg.norm(x)


def similarity_matrix(
    x: list[float] | list[list[float]], y: list[float] | list[list[float]]
) -> list[float] | list[list[float]]:
    x = to_normed_array(x)
    y = to_normed_array(y)
    sim_mat = x @ y.T
    return sim_mat.tolist()


def normalize_scores(scores: np.ndarray) -> np.ndarray:
    min_score = scores.min()
    score_range = scores.max() - min_score
    if score_range == 0:
        return np.ones_like(scores)
    else:
        return (scores - min_score) / score_range


def find_outlier_threshold(scores: np.ndarray) -> float:
    # Find the histogram of scores
    hist, bin_edges = np.histogram(scores.flatten(), bins=200)
    # Define the algo
    algo = rpt.Pelt(model="l2", min_size=1).fit(hist)
    # Find the change points
    result = algo.predict(pen=10 * hist.mean())
    # Find the last change point
    last_change_point = result[-2]
    # Find the threshold
    threshold = bin_edges[last_change_point]
    return threshold


class OutOfTokenCapError(Exception):
    pass


def find_prompt_path(
    name: str, prompt_dir: str, version_string: str | None = None
) -> str:
    # First case: name is a path
    candidate_path = os.path.join(prompt_dir, f"{name}.md")
    if os.path.exists(candidate_path):
        return candidate_path

    # Second case: name is a directory
    candidate_path = os.path.join(prompt_dir, name)
    if version_string is None and os.path.isdir(candidate_path):
        # List all Markdown files in the directory
        files = [f for f in os.listdir(candidate_path) if f.endswith(".md")]

        # Sort files based on version numbers
        sorted_files = sorted(
            files, key=lambda f: version.parse(f.split("v")[-1].replace(".md", ""))
        )

        # Return the path of the most recent version
        if sorted_files:
            return os.path.join(candidate_path, sorted_files[-1])

    # Third case: name is a directory with a version preference
    elif version_string is not None:
        assert os.path.isdir(candidate_path)
        # Find the file
        prompt_path = os.path.join(candidate_path, f"v{version_string}.md")
        if os.path.exists(prompt_path):
            return prompt_path
        else:
            raise ValueError(f"Version {version_string} not found in {candidate_path}")

    else:
        raise ValueError(
            f"Prompt {name} (version {version_string}) not found in {prompt_dir}"
        )


def load_prompt(
    name: str,
    version_string: str | None = None,
    system_only: bool = False,
    system_prompt_format_kwargs: dict[str, Any] | None = None,
    user_prompt_format_kwargs: dict[str, Any] | None = None,
    # TODO: fix this default value so it has like a context manager or something that can be used to set the default value based on the environment
    prompt_dir: str = "backend/app/core/intel/prompts",
) -> str | tuple[str, str | None]:
    # Load the prompts
    # check if it's a relative path
    if not os.path.isabs(prompt_dir):
        prompt_dir = get_path(prompt_dir)
    prompt_path = find_prompt_path(name, prompt_dir, version_string)
    system_prompt, user_prompt = parse_prompts(prompt_path)
    # Format them
    if system_prompt_format_kwargs is not None:
        system_prompt = format_string(system_prompt, **system_prompt_format_kwargs)
    if user_prompt is not None and user_prompt_format_kwargs is not None:
        user_prompt = format_string(user_prompt, **user_prompt_format_kwargs)
    # Return
    if system_only:
        return system_prompt
    return system_prompt, user_prompt
