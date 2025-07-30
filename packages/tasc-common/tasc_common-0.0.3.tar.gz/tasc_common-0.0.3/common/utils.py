from __future__ import annotations

import asyncio
import base64
import glob
import hashlib
import inspect
import io
import json
import logging
import os
import pickle
import re
import shutil
import signal
import string
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
from math import copysign
from sys import exc_info
from traceback import format_exception
from typing import IO, Any, Optional, List, Dict, Tuple, Callable, get_type_hints, Type
from urllib.parse import urlparse, urlunparse

import git
import jsonschema
from loguru import logger
import mistune
import numpy as np
import pdfkit
from diskcache import Cache
from docstring_parser import parse
from jose import JWTError, jwt
from PIL import Image
from jsonschema.exceptions import ValidationError
from pydantic import create_model, RootModel


def generate_token(input: str, hours: int = 24) -> str:
    from common.config import common_settings as settings

    delta = timedelta(hours=hours)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": input},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_token(token: str) -> str | None:
    from common.config import common_settings as settings

    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return str(decoded_token["sub"])
    except JWTError:
        return None


# ------ Path-fu ------


def get_git_root():
    try:
        # Start the search from the directory of the current file
        repo = git.Repo(
            os.path.dirname(os.path.abspath(__file__)), search_parent_directories=True
        )
        return repo.git.rev_parse("--show-toplevel")
    except git.InvalidGitRepositoryError:
        return None


def get_path(
    relative_path: str, makedirs: bool = True, root_directory: str | None = None
) -> str:
    if root_directory is None:
        # Get the root directory of the Git repository
        root_directory = get_git_root()
        if not root_directory:
            root_directory = "/"
    if root_directory is None:
        raise ValueError("root_directory must be specified if not in a Git repository.")
    path = os.path.join(root_directory, relative_path)
    if makedirs and not os.path.exists(path):
        # Check if the path ends with an extension (assumed to be a file in this case)
        if os.path.splitext(relative_path)[1]:
            dir_to_make = os.path.dirname(path)
        else:
            dir_to_make = path
        os.makedirs(dir_to_make, exist_ok=True)
    return path


# ------ Python-fu ------


class Singleton(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                # If the instance doesn't exist, create it and store it in the _instances dictionary.
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        # Return the singleton instance.
        return cls._instances[cls]


@dataclass
class ScoredList:
    items: List[Any]
    scores: List[float]

    @classmethod
    def from_items_and_scores(cls, items_and_scores: List[Tuple[Any, float]]):
        if len(items_and_scores) == 0:
            return cls(items=[], scores=[])
        else:
            items, scores = zip(*items_and_scores)
            return cls(items=list(items), scores=list(scores))

    @classmethod
    def from_items(cls, items: List[Any]):
        return cls(items=items, scores=[0.0] * len(items))

    def items_and_scores(self):
        for item, score in zip(self.items, self.scores):
            yield item, score

    def __len__(self):
        return len(self.items)

    def __getitem__(self, key):
        return self.items[key]

    def __iter__(self):
        return iter(self.items)

    def __contains__(self, item):
        return item in self.items

    def canonicalize_scores_(self, reverse: bool = True):
        # Create a list of (index, score) tuples
        indexed_scores = list(enumerate(self.scores))

        # Sort the indexed_scores list based on scores in descending order
        sorted_indexed_scores = sorted(
            indexed_scores, key=lambda x: x[1], reverse=reverse
        )

        # Calculate reciprocal rank scores
        total_items = len(sorted_indexed_scores)
        reciprocal_rank_scores = [1 / (i + 1) for i in range(total_items)]

        # Create a dictionary mapping original indices to new scores
        new_scores_map = {
            idx: score
            for (idx, _), score in zip(sorted_indexed_scores, reciprocal_rank_scores)
        }

        # Update the scores list while maintaining the original order
        self.scores = [new_scores_map[i] for i in range(total_items)]


class NoValue:
    pass


def format_dict(dictionary, indent=0):
    result = ""
    for key, value in dictionary.items():
        if isinstance(value, dict):
            result += "  " * indent + f"{key}:\n"
            result += format_dict(value, indent + 1)
        else:
            result += "  " * indent + f"{key}: {value}\n"
    return result


def flatten_dict(d, parent_key="", sep="/"):
    """
    Flatten an arbitrary nested dictionary.

    Parameters:
    - d (dict): The dictionary to flatten.
    - parent_key (str, optional): The base key for recursive calls. Defaults to ''.
    - sep (str, optional): The separator to use between keys. Defaults to '/'.

    Returns:
    - dict: The flattened dictionary.
    """
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


def repeat_every(
    seconds: float,
    wait_first: bool = False,
    logger: logging.Logger = None,
    raise_exceptions: bool = False,
    max_repetitions: int | None = None,
):
    def decorator(func):
        is_coroutine = asyncio.iscoroutinefunction(func)

        async def wrapped():
            repetitions = 0
            try:
                if wait_first:
                    await asyncio.sleep(seconds)
                while max_repetitions is None or repetitions < max_repetitions:
                    try:
                        await func() if is_coroutine else await asyncio.to_thread(func)
                        repetitions += 1
                    except Exception as exc:
                        if logger:
                            logger.error("".join(format_exception(*exc_info())))
                        if raise_exceptions:
                            raise exc
                    await asyncio.sleep(seconds)
            except asyncio.CancelledError:
                if logger:
                    logger.info("Cancellation received, stopping...")
                raise

        def start():
            return asyncio.create_task(wrapped())

        return start

    return decorator


def format_string(s: str, **kwargs):
    # Parse the format string to get the field names
    formatter = string.Formatter()
    field_names = [
        field_name
        for _, field_name, _, _ in formatter.parse(s)
        if field_name is not None
    ]

    # Create a dictionary with only the required fields
    required_kwargs = {key: kwargs[key] for key in field_names if key in kwargs}

    return s.format(**required_kwargs)


def has_format_field(s: str, field_name: str) -> bool:
    formatter = string.Formatter()
    return any(field_name == f_name for _, f_name, _, _ in formatter.parse(s) if f_name)


def multiline_input(prompt: str | None = "auto"):
    contents = []
    if prompt is None:
        pass
    elif prompt == "auto":
        print("Enter your text below. Type :wq to finish.")
    else:
        print(prompt)
    while True:
        line = input()
        if line == ":wq":
            break
        contents.append(line)
    return "\n".join(contents)


@dataclass
class TimestampedString:
    timestamp: float
    string: str

    @classmethod
    def from_string(cls, string: str):
        return cls(timestamp=time.time(), string=string)

    def get_age(self, unit: str = "hours"):
        if unit == "hours":
            return (time.time() - self.timestamp) / 3600
        elif unit == "days":
            return (time.time() - self.timestamp) / (3600 * 24)
        elif unit == "weeks":
            return (time.time() - self.timestamp) / (3600 * 24 * 7)
        elif unit == "months":
            return (time.time() - self.timestamp) / (3600 * 24 * 30)
        elif unit == "years":
            return (time.time() - self.timestamp) / (3600 * 24 * 365)
        else:
            raise ValueError(f"Invalid unit: {unit}")

    def __str__(self):
        return self.string

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "string": self.string,
        }

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            timestamp=d["timestamp"],
            string=d["string"],
        )

    def __hash__(self):
        return hash((self.timestamp, self.string))


def pretty_date() -> str:
    return datetime.now().strftime("%-d %B %Y")


def camel_to_snake(text):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()


def camel_to_kebab(text):
    return re.sub(r"(?<!^)(?=[A-Z])", "-", text).lower()


def parse_triple_quote(text: str) -> str:
    return parse(text).long_description


def markdown_to_html(markdown_content: str) -> str:
    # Create markdown parser with necessary plugins
    logger.info(f"markdown_content: {markdown_content}")
    html_content = mistune.html(markdown_content)

    # HTML template with CSS styling
    html_template = """<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 40px auto;
                padding: 20px;
                color: #333;
            }}
            h1, h2, h3, h4 {{
                color: #2c3e50;
                margin-top: 24px;
            }}
            a {{
                color: #3498db;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            ul, ol {{
                padding-left: 20px;
            }}
            li {{
                margin: 8px 0;
            }}
            strong {{
                color: #2c3e50;
            }}
            p {{
                margin: 16px 0;
            }}
            pre {{
                background-color: #f6f8fa;
                padding: 1em;
                border: 1px solid #ddd;
                overflow: auto;
            }}
            code {{
                background-color: #f6f8fa;
                padding: 0.2em 0.4em;
                border-radius: 3px;
            }}
        </style>
    </head>
    <body>{html_content}</body>
    </html>"""

    result = html_template.format(html_content=html_content)
    logger.info(f"result: {result}")
    return result


def truncate_after_markdown_header_with_flag(
    text: str,
    header: str,
    truncation_str: str = "[...]",
    truncate_subheaders: bool = True,
) -> str:
    """
    This function truncates the text after the first section under the specified markdown header.
    It includes a flag to determine if subheaders should also be truncated.
    """

    # Split the text by lines to process headers
    lines = text.split("\n")
    # Variable to store the index of line where the header is found
    start_index = None
    # Variable to store the index of line where the next header of the same or higher level is found
    end_index = None

    # Search for the line index of the specified header
    for i, line in enumerate(lines):
        if line.strip() == header:
            start_index = i
            break

    # If the header was not found, return the original text
    if start_index is None:
        return text

    # Determine the level of the original header
    original_header_level = header.count("#")

    # Search for the next header of the same or higher level
    for i, line in enumerate(lines[start_index + 1 :], start=start_index + 1):
        # Check if the line starts with a header
        if line.startswith("#"):
            current_header_level = line.count("#")
            # If subheaders should not be truncated and the current header level is greater than the original, continue
            if not truncate_subheaders and current_header_level > original_header_level:
                continue
            # If the level is the same or higher than the original header, mark the end index
            if current_header_level <= original_header_level:
                end_index = i
                break

    # If the end index wasn't found, we truncate everything after the start header
    end_index = end_index or len(lines)

    # Join the text back together with the truncation after the specified header's section
    truncated_text = "\n".join(
        lines[: start_index + 1] + [truncation_str] + lines[end_index:]
    )

    return truncated_text


def find_markdown_header(text: str, header: str) -> bool:
    # Make sure header starts with a '#'
    assert header.startswith("#"), "Header must start with '#'"
    # Escape special characters in the header text
    header_text = re.escape(header.lstrip("#").strip())

    # Create a regex pattern that matches the header with the correct number of '#' characters
    pattern = rf'^\s*{"#"*header.count("#")} {header_text}\s*$'

    # Search for the pattern in the text using MULTILINE flag
    return bool(re.search(pattern, text, re.MULTILINE))


def find_text_under_header(
    text: str,
    header: str,
    keep_subheaders: bool = False,
    break_on_horizontal_rules: bool = False,
    assert_found: bool = False,
) -> str | None:
    if not header.startswith("#"):
        return None

    if not find_markdown_header(text, header):
        return None

    lines = text.split("\n")
    header_level = header.count("#")
    found_header = False
    result = []

    for line in lines:
        if line.startswith(header):
            found_header = True
            continue

        if found_header:
            if keep_subheaders:
                break_strings = ["#" * i + " " for i in range(1, header_level + 1)]
            else:
                break_strings = ["#"]

            if break_on_horizontal_rules:
                break_strings.append("---")

            if any(line.startswith(break_string) for break_string in break_strings):
                break

            result.append(line)

    if not result:
        if assert_found:
            raise ValueError(f"Header '{header}' not found in text:\n\n{text}")
        else:
            return None

    return "\n".join(result)


def find_markdown_block(text: str) -> str | None:
    # Pattern to match markdown code block
    pattern = r"```markdown(.*?)```"

    # Searching for the pattern in the text
    match = re.search(pattern, text, re.DOTALL)

    # Returning the matched group if found, else an empty string
    return match.group(1).strip() if match else None


def extract_tag_content(text, tag_name):
    pattern = f"<{tag_name}>(.*?)</{tag_name}>"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    return None


def remove_tag_content(text, tag_name):
    """
    Removes content between specified tags from the text.

    Args:
        text (str): The input text to process
        tag_name (str): The name of the tag to remove

    Returns:
        str: Text with the specified tag and its content removed
    """
    pattern = f"<{tag_name}>.*?</{tag_name}>"
    return re.sub(pattern, "", text, flags=re.DOTALL)


def create_xml_tags(tag_name: str, **kwargs) -> tuple[str, str]:
    """
    Create opening and closing XML tags with optional attributes.

    Args:
        tag_name: Name of the XML tag
        **kwargs: Optional attributes to add to opening tag

    Returns:
        tuple[str, str]: Opening and closing XML tags

    Examples:
        >>> create_xml_tags("div", class_name="container", data_id="123")
        ('<div class="container" data-id="123">', '</div>')

        >>> create_xml_tags("img", src="/image.jpg", alt="A photo")
        ('<img src="/image.jpg" alt="A photo">', '</img>')
    """
    # Convert kwargs from snake_case to kebab-case
    attrs = {k.replace("_", "-"): v for k, v in kwargs.items()}

    # Build opening tag with attributes
    attrs_str = " ".join(f'{k}="{str(v)}"' for k, v in attrs.items())
    open_tag = f'<{tag_name}{" " + attrs_str if attrs_str else ""}>'

    # Build closing tag
    close_tag = f"</{tag_name}>"

    return open_tag, close_tag


def extract_from_pattern(text: str, template: str) -> dict | None:
    """
    Extract variables from a text string based on a given template.

    This function searches for a pattern in the text that matches the provided template
    and extracts the values of variables defined in the template.

    Args:
        text (str): The input text to search within.
        template (str): The template string containing variables in curly braces,
                        e.g., "Hello, my name is {name} and I am {age} years old."

    Returns:
        dict | None: A dictionary containing the extracted variables as key-value pairs,
                     where the keys are the variable names from the template and the values
                     are the corresponding extracted strings. Returns None if no match is found.

    Examples:
        >>> text = "Hello, my name is John Doe and I am 25 years old."
        >>> template = "Hello, my name is {name} and I am {age} years old."
        >>> extract_from_pattern(text, template)
        {'name': 'John Doe', 'age': '25'}

        >>> text = "The quick brown fox jumps over the lazy dog."
        >>> template = "The {color} {animal} jumps over the {adjective} dog."
        >>> extract_from_pattern(text, template)
        {'color': 'quick brown', 'animal': 'fox', 'adjective': 'lazy'}

    Note:
        - The function will return the first match found in the text.
        - The function can handle multi-line text and content containing curly braces.
        - The parts of the template outside the curly braces must match exactly in the text.
    """
    # Convert template to regex pattern, using non-greedy matching
    pattern = re.sub(r"\{(\w+)\}", lambda m: f"(?P<{m.group(1)}>.*?)", template)

    # Try to find the pattern in the string, with DOTALL flag to match newlines
    match = re.search(pattern, text, re.DOTALL)

    if match:
        return match.groupdict()
    else:
        return None


def extract_urls(text: str, unique: bool = True) -> list[str]:
    """
    Extract all URLs from a text string.

    Args:
        text (str): The text to extract URLs from
        unique (bool): Whether to return only unique URLs. Defaults to True.

    Returns:
        list[str]: List of extracted URLs

    Examples:
        >>> text = "Check out https://example.com and http://test.com/page?q=1"
        >>> extract_urls(text)
        ['https://example.com', 'http://test.com/page?q=1']
    """
    # This pattern matches URLs starting with http://, https://, or www.
    url_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*|www\.(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*"

    urls = re.findall(url_pattern, text)

    # Add https:// to URLs starting with www.
    urls = ["https://" + url if url.startswith("www.") else url for url in urls]

    if unique:
        urls = list(dict.fromkeys(urls))  # Remove duplicates while preserving order

    return urls


def attach_protocol_to_url(key: str, protocol: str):
    return f"{protocol}://{key}" if "://" not in key else key


def file_to_base64(file_path_or_file: str | IO) -> str:
    if isinstance(file_path_or_file, str):
        file_path = file_path_or_file
        file = open(file_path, "rb")
    else:
        file = file_path_or_file
    base64_str = base64.b64encode(file.read()).decode("utf-8")
    if isinstance(file_path_or_file, str):
        file.close()
    return base64_str


def image_to_base64(image_path_or_image_file: str | IO) -> str:
    base64_image = file_to_base64(image_path_or_image_file)
    return f"data:image/jpeg;base64,{base64_image}"


def read_base64_url_image(base64_url_str: str) -> np.ndarray:
    # Split the base64 URL to extract the base64 string part
    base64_str = base64_url_str.split(",")[1]

    # Decode the base64 string to get raw image bytes
    image_bytes = base64.b64decode(base64_str)

    # Read the image from bytes using PIL
    image = Image.open(io.BytesIO(image_bytes))

    # Convert the PIL image to a NumPy array
    numpy_image = np.array(image)

    return numpy_image


def str_to_urlsafe_base64(s: str) -> str:
    """Convert a string to URL-safe base64 encoding.

    Args:
        s: String to encode

    Returns:
        URL-safe base64 encoded string
    """
    # Convert string to bytes, encode to base64, then decode back to string
    b64 = base64.urlsafe_b64encode(s.encode("utf-8")).decode("utf-8")
    # Remove padding = signs
    return b64.rstrip("=")


def urlsafe_base64_to_str(b64: str) -> str:
    """Convert a URL-safe base64 string back to original string.

    Args:
        b64: URL-safe base64 encoded string

    Returns:
        Original decoded string
    """
    # Add back padding if needed
    padding = 4 - (len(b64) % 4)
    if padding != 4:
        b64 += "=" * padding

    # Decode base64 to bytes then convert to string
    return base64.urlsafe_b64decode(b64.encode("utf-8")).decode("utf-8")


def find_json_block(text: str, load: bool = False) -> str | dict | list | None:
    # Pattern to match JSON code block
    pattern = r"```json(.*?)```"

    # Searching for the pattern in the text
    match = re.search(pattern, text, re.DOTALL)

    # Returning the matched group if found, else an empty string
    json_block = match.group(1).strip() if match else None

    if load:
        return json.loads(json_block) if json_block is not None else None
    else:
        return json_block


def parse_json(text: str, raise_on_fail: bool = True) -> dict | list | None:
    if "```json" in text and "```" in text:
        return find_json_block(text, load=True)
    if text.startswith("```"):
        text.strip("```")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        if raise_on_fail:
            raise
        else:
            return None


class AgentTimeoutException(Exception):
    pass


def timeout(seconds):
    def decorator(func):
        def _handle_timeout(_signum, _frame):
            raise AgentTimeoutException(
                f"Function '{func.__name__}' timed out after {seconds} seconds"
            )

        def wrapper(*args, **kwargs):
            # Set the signal handler and a timeout
            old_handler = signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                # Restore the original signal handler
                signal.signal(signal.SIGALRM, old_handler)
                # Cancel the alarm
                signal.alarm(0)
            return result

        return wrapper

    return decorator


SESSION_ID = f"s{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:5]}"


def get_session_id() -> str:
    return SESSION_ID


# ------ Tokens ------


def markdown_to_pdf(md_text: str, output_path: str, html_prefix: str | None = None):
    html = mistune.html(md_text)
    if html_prefix is not None:
        html = html_prefix + html
    pdfkit.from_string(html, output_path)


# ------ URLs and Paths ------


def url_to_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc or parsed_url.path  # netloc for http(s), path for others


def domain_to_url(domain):
    if not domain.startswith(("http://", "https://", "www.")):
        return urlunparse(("https", domain, "", "", "", "")).strip("/") + "/"
    elif domain.startswith("www."):
        return urlunparse(("https", domain[4:], "", "", "", "")).strip("/") + "/"
    else:
        return domain.strip("/") + "/"


def email_to_url(email: str) -> str | None:
    email_services = [
        "gmail.com",
        "yahoo.com",
        "outlook.com",
        "icloud.com",
        "aol.com",
        "zoho.com",
        "protonmail.com",
        "yandex.com",
        "mail.com",
        "gmx.com",
        "hotmail.com",  # Adding Hotmail as it's still commonly used
        "live.com",  # Microsoft's Live.com is also a popular choice
        "fastmail.com",  # FastMail is known for its speed and privacy
        "inbox.com",  # Inbox.com is another option, though less popular
        "rediffmail.com",  # Rediffmail is used in some regions, especially in India
    ]
    domain = email.split("@")[1]
    if domain in email_services:
        return None
    else:
        return domain_to_url(domain)


def get_email_path(email: str) -> str:
    return email.replace("@", "__at__").replace(".", "__dot__")


# ------ Caching ------


_cache_instance = None


class CacheConfig:
    _use_cache = True

    @classmethod
    def enable_cache(cls):
        cls._use_cache = True

    @classmethod
    def disable_cache(cls):
        cls._use_cache = False

    @classmethod
    def is_cache_enabled(cls):
        return cls._use_cache


def get_cache():
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = Cache(get_path("data/cache"))
    return _cache_instance


def custom_memoize(expire=None, tag=None, use_cache=True):
    def decorator(func):
        cache = get_cache()

        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def wrapper(*args, **kwargs):
                if CacheConfig.is_cache_enabled() and use_cache:
                    # If caching is enabled, use the memoized version of the function
                    @cache.memoize(expire=expire, tag=tag)
                    async def cached_func(*a, **k):
                        return await func(*a, **k)

                    return await cached_func(*args, **kwargs)
                else:
                    # If caching is disabled, directly call the original function
                    return await func(*args, **kwargs)

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                if CacheConfig.is_cache_enabled() and use_cache:
                    # If caching is enabled, use the memoized version of the function
                    @cache.memoize(expire=expire, tag=tag)
                    def cached_func(*a, **k):
                        return func(*a, **k)

                    return cached_func(*args, **kwargs)
                else:
                    # If caching is disabled, directly call the original function
                    return func(*args, **kwargs)

        return wrapper

    return decorator


def safe_json_dump(data, filepath, allow_fallback=False):
    # This ensures we don't accidentally overwrite an existing file with a corrupt file.
    temp_filename = filepath + ".tmp"
    pickle_filename = filepath + ".pkl"

    try:
        # Serialize to a string
        serialized_data = json.dumps(data, indent=2)

        # Write to a temporary file
        with open(temp_filename, "w") as temp_file:
            temp_file.write(serialized_data)

        # Verify temporary file
        with open(temp_filename) as temp_file:
            json.load(temp_file)

        # Use shutil.move for an atomic operation
        shutil.move(temp_filename, filepath)

    except (TypeError, json.JSONDecodeError) as json_error:
        if allow_fallback:
            # Fallback to pickle if JSON fails
            try:
                with open(pickle_filename, "wb") as pickle_file:
                    pickle.dump(data, pickle_file)
                return pickle_filename
            except Exception as pickle_error:
                raise Exception(
                    f"Pickle serialization failed: {pickle_error}"
                ) from pickle_error
        else:
            raise Exception(f"JSON serialization failed: {json_error}") from json_error

    finally:
        # Clean up temp file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    return filepath


def string_hash(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()


def pickle_hash(data: Any) -> str:
    return hashlib.md5(pickle.dumps(data)).hexdigest()


# ------ Redis-fu ------


def get_authorized_messaging_channel_id(account_id: str):
    return f"MESSAGE_CHANNEL:{account_id}"


def get_authorized_scheduling_event_channel_id(account_id: str):
    return f"SCHEDULING_EVENT_CHANNEL:{account_id}"


def get_authorized_conversation_title_update_event_id(account_id: str):
    return f"CONVERSATION_TITLE_UPDATE_EVENT:{account_id}"


# ------ Math-fu ------


class PSquareQuantileTracker:
    def __init__(self, quantiles: Optional[List[float]] = None):
        if quantiles is None:
            quantiles = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        self.quantiles = quantiles
        self.n = 0
        self.tiles = {p: self._create_tile(p) for p in quantiles}

    def _create_tile(self, p: float) -> Dict:
        return {
            "dn": [0, p / 2, p, (1 + p) / 2, 1],
            "npos": [1, 1 + 2 * p, 1 + 4 * p, 3 + 2 * p, 5],
            "pos": list(range(1, 6)),
            "heights": [],
            "initialized": False,
        }

    def add(self, item: float) -> None:
        self.n += 1
        for p, tile in self.tiles.items():
            self._update_tile(tile, item)

    def _update_tile(self, tile: Dict, item: float) -> None:
        if len(tile["heights"]) != 5:
            tile["heights"].append(item)
            if len(tile["heights"]) == 5:
                tile["heights"].sort()
                tile["initialized"] = True
        else:
            if item < tile["heights"][0]:
                tile["heights"][0] = item
                k = 1
            elif item >= tile["heights"][-1]:
                tile["heights"][-1] = item
                k = 4
            else:
                k = next(
                    i
                    for i in range(1, 5)
                    if tile["heights"][i - 1] <= item < tile["heights"][i]
                )

            tile["pos"] = [j if i < k else j + 1 for i, j in enumerate(tile["pos"])]
            tile["npos"] = [x + y for x, y in zip(tile["npos"], tile["dn"])]

            self._adjust_tile(tile)

    def _adjust_tile(self, tile: Dict) -> None:
        for i in range(1, 4):
            n = tile["pos"][i]
            q = tile["heights"][i]

            d = tile["npos"][i] - n

            if (d >= 1 and tile["pos"][i + 1] - n > 1) or (
                d <= -1 and tile["pos"][i - 1] - n < -1
            ):
                d = int(copysign(1, d))

                qp1, q, qm1 = (
                    tile["heights"][i + 1],
                    tile["heights"][i],
                    tile["heights"][i - 1],
                )
                np1, n, nm1 = tile["pos"][i + 1], tile["pos"][i], tile["pos"][i - 1]
                qn = self._calc_p2(qp1, q, qm1, d, np1, n, nm1)

                if qm1 < qn < qp1:
                    tile["heights"][i] = qn
                else:
                    tile["heights"][i] = q + d * (tile["heights"][i + d] - q) / (
                        tile["pos"][i + d] - n
                    )

                tile["pos"][i] = n + d

    @staticmethod
    def _calc_p2(
        qp1: float, q: float, qm1: float, d: float, np1: float, n: float, nm1: float
    ) -> float:
        outer = d / (np1 - nm1)
        inner_left = (n - nm1 + d) * (qp1 - q) / (np1 - n)
        inner_right = (np1 - n - d) * (q - qm1) / (n - nm1)
        return q + outer * (inner_left + inner_right)

    def get_quantiles(self) -> Dict[float, float]:
        return {
            p: (
                tile["heights"][2]
                if tile["initialized"]
                else sorted(tile["heights"])[
                    min(max(int(len(tile["heights"]) * p), 0), len(tile["heights"]) - 1)
                ]
            )
            for p, tile in self.tiles.items()
        }

    def state_dict(self) -> Dict:
        return {
            "n": self.n,
            "quantiles": self.quantiles,
            "tiles": {str(k): v for k, v in self.tiles.items()},
        }

    def load_state_dict(self, state_dict: Dict) -> None:
        self.n = state_dict["n"]
        self.quantiles = state_dict["quantiles"]
        self.tiles = {float(k): v for k, v in state_dict["tiles"].items()}


def indent(message: str, level: int = 4) -> str:
    return "\n".join([f"{' ' * level}{line}" for line in message.split("\n")])


def get_function_schema(
    func: Callable,
    exclude_function_name: bool = False,
    exclude_function_description: bool = False,
) -> Dict[str, Any]:
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    return_type = type_hints.get("return", Any)

    # Parse the docstring
    # There's a complication where the docstrings that just spec the
    # args don't get parsed correctly. We'll fix this by adding a line of "fake description".
    ignore_string = "__ignore__"
    func_docstring = inspect.getdoc(func) or ""
    if func_docstring.startswith("Args:\n"):
        func_docstring = ignore_string + "\n\n" + func_docstring
    docstring = parse(func_docstring)

    # Create field definitions for Pydantic
    fields = {}
    field_descriptions = {}

    for name, param in sig.parameters.items():
        # Skip 'self' parameter for methods
        if name == "self":
            continue
        # Skip *args and **kwargs
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue

        if param.default is param.empty:
            fields[name] = (type_hints.get(name, Any), ...)
        else:
            fields[name] = (type_hints.get(name, type(param.default)), param.default)

        # Get parameter description from parsed docstring
        param_doc = next(
            (param.description for param in docstring.params if param.arg_name == name),
            None,
        )
        if param_doc:
            field_descriptions[name] = param_doc

    # Create models for input and output
    input_model = create_model(
        f"{func.__name__}",
        __doc__=(
            docstring.short_description
            if docstring.short_description != ignore_string
            else None
        ),
        **fields,
    )
    output_model = RootModel[return_type]

    # Get the base schemas
    input_schema = input_model.model_json_schema()
    output_schema = output_model.model_json_schema()

    # Add descriptions to properties if available
    if field_descriptions:
        for field_name, desc in field_descriptions.items():
            if field_name in input_schema.get("properties", {}):
                input_schema["properties"][field_name]["description"] = desc

    # Add function descriptions to the schema
    if docstring.short_description and docstring.short_description != ignore_string:
        input_schema["description"] = docstring.short_description
        if docstring.long_description and docstring.long_description != ignore_string:
            input_schema["description"] += "\n\n" + docstring.long_description

    if exclude_function_name:
        input_schema.pop("title", None)
    if exclude_function_description:
        input_schema.pop("description", None)

    return {
        "input_schema": input_schema,
        "output_schema": output_schema,
    }


def validate_against_schema(
    data: Dict[str, Any], schema: Dict[str, Any]
) -> tuple[bool, str]:
    """
    Validates a dictionary against a JSON schema.

    Args:
        data: Dictionary to validate
        schema: JSON schema to validate against

    Returns:
        tuple[bool, str]: (is_valid, error_message)
        If valid, returns (True, "")
        If invalid, returns (False, error_description)
    """
    try:
        jsonschema.validate(data, schema)
        return True, ""
    except ValidationError as e:
        return False, str(e)


def return_none_if_error(
    func: Callable = None,
    *,
    exception_logger: Any = None,
    exception_classes: Tuple[Type[Exception]] = None,
):
    """Decorator that catches exceptions and returns None instead of raising them.

    Args:
        func: The function to decorate (when used without parameters)
        exception_logger: Optional loguru logger to call logger.exception() on errors
        exception_classes: Optional tuple of exception classes to catch (defaults to Exception)
    """
    if exception_classes is None:
        exception_classes = (Exception,)
    elif not isinstance(exception_classes, (tuple, list)):
        exception_classes = (exception_classes,)
    else:
        exception_classes = tuple(exception_classes)

    if exception_logger is None:
        exception_logger = logger

    def decorator(f):
        if asyncio.iscoroutinefunction(f):

            @wraps(f)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await f(*args, **kwargs)
                except exception_classes:
                    if exception_logger:
                        exception_logger.exception(f"Exception in {f.__name__}")
                    return None

            return async_wrapper
        else:

            @wraps(f)
            def sync_wrapper(*args, **kwargs):
                try:
                    return f(*args, **kwargs)
                except exception_classes:
                    if exception_logger:
                        exception_logger.exception(f"Exception in {f.__name__}")
                    return None

            return sync_wrapper

    # Handle both @return_none_if_error and @return_none_if_error(...) usage
    if func is None:
        return decorator
    else:
        return decorator(func)
