import json
from textwrap import dedent
from typing import cast, List, Literal, Optional, Callable, Any
from loguru import logger
from functools import wraps
import inspect

from common.intel.bot import Bot
from common.intel.utils import DEFAULT_FLAGSHIP_MODEL, count_tokens_in_str
from common.utils import (
    indent,
    NoValue,
    parse_json,
    remove_tag_content,
    get_function_schema,
    validate_against_schema,
)


async def true_or_false(
    question,
    *,
    model_name: str = DEFAULT_FLAGSHIP_MODEL,
    num_tries: int = 3,
    default: bool | None = None,
    think: bool = False,
    deterministic: bool = False,
    robust: bool = False,
) -> bool:
    if think:
        system_prompt = """
        <instruction>
          You will be given a question. Please proceed as following. 
          
          1. First, you must think out loud about the answer to that question inside the <thinking>...</thinking> tag.
          2. After you have thought about the answer, call the `submit_answer` tool with your answer as the argument. 
        </instruction>
        """
    else:
        system_prompt = """
        <instruction>
          You will be given a question. Your task is to answer it with either True or False. 
        
          To submit your answer, please call the `submit_answer` tool with your answer as the argument.
        </instruction>
        """
    system_prompt = dedent(system_prompt).strip()

    user_prompt = f"""
    <question>
    {indent(question, 2)}
    </question>
    """
    user_prompt = dedent(user_prompt).strip()

    _answer = None

    async def submit_answer(answer: bool):
        nonlocal _answer
        _answer = answer
        return {"info": "Answer submitted."}

    bot = Bot("true_or_false_bot", model_name=model_name, system_prompt=system_prompt)
    bot.register_function(submit_answer)
    bot.add_user_event(user_prompt)

    retry_num = 0
    while True:
        try:
            response = await bot.async_complete(
                max_tokens=100 if not think else 1024,
                temperature=0.2 if not deterministic else 0.0,
            )
            await bot.async_call_requested_tools(add_to_history=True)
        except Exception as e:
            logger.exception("API error in true_or_false")
            if not robust:
                raise
            if retry_num >= num_tries:
                if default is None:
                    raise ValueError(
                        f"Failed to get True/False answer after {num_tries} attempts due to API errors"
                    ) from e
                return default
            retry_num += 1
            continue

        if _answer is None:
            if retry_num >= num_tries:
                if isinstance(default, NoValue):
                    raise ValueError(
                        f"Failed to get True/False answer after {num_tries} attempts"
                    )
                else:
                    return bool(default)
            retry_num += 1
            bot.add_user_event(
                "<instruction>"
                "Please answer with True or False by calling the submit_answer tool."
                "</instruction>"
            )
            continue

        if _answer is None:
            return default
        return cast(bool, _answer)


async def do_it(
    instruction: str,
    *,
    task_description: str | None = None,
    model_name: str = DEFAULT_FLAGSHIP_MODEL,
    max_tokens: int | None = 1024,
    temperature: float | None = 0.2,
    tools: List[callable] | None = None,
    validator: Optional[callable] = None,
    max_num_tries: int = 3,
    default_if_validation_fails: str | None = None,
    image_url: str | None = None,
    image_detail: str = "auto",
    tags_to_remove: List[str] | None = None,
    # Bucket for storing extra information
    info_bucket: dict | None = None,
    **complete_kwargs,
) -> str:
    if task_description is None:
        task_description = "You are a helpful assistant."

    bot = Bot("do_it_bot", model_name=model_name, system_prompt=task_description)
    if tools is not None:
        for tool in tools:
            bot.register_function(tool)
    # Add image support to the user event
    bot.add_user_event(
        instruction,
        **({"image_url": image_url, "image_detail": image_detail} if image_url else {}),
    )

    # bot.async_complete can handle the temperature being None, so we don't need to check here
    base_kwargs = {"temperature": temperature}
    if max_tokens is not None:
        base_kwargs["max_tokens"] = max_tokens

    # Get the response
    response = await bot.async_complete(**base_kwargs, **complete_kwargs)

    # Validate response
    if validator is not None:
        for _ in range(max_num_tries):
            valid, instructions = validator(response.content)
            if valid:
                break
            bot.add_user_event(instructions)
            response = await bot.async_complete(
                max_tokens=max_tokens, temperature=temperature, **complete_kwargs
            )
        else:
            if default_if_validation_fails is not None:
                return default_if_validation_fails
            else:
                raise ValueError(
                    "Failed to validate the response, and no default value was provided."
                )
    # Call any requested tools
    if tools is not None:
        tool_call_result = await bot.async_call_requested_tools(add_to_history=True)
        if info_bucket is not None:
            info_bucket["tool_call_result"] = tool_call_result
    # Return the response
    content = response.content
    if tags_to_remove is not None:
        for tag in tags_to_remove:
            content = remove_tag_content(content, tag_name=tag)
    return content


async def choose_one(
    question: str,
    choices: List[str],
    *,
    num_tries: int = 3,
    default: str | None = None,
    model_name: str = DEFAULT_FLAGSHIP_MODEL,
    deterministic: bool = False,
    think: bool = False,
    robust: bool = False,
) -> str:

    if think:
        system_prompt = """
        <instruction>
          You will be given a question with multiple choices. Please proceed as following:
          
          1. First, you must think out loud about the answer inside the <thinking>...</thinking> tag.
          2. After you have thought about it, call the `submit_answer` tool with your chosen answer as the argument.
        </instruction>
        """
    else:
        system_prompt = """
        <instruction>
          You will be given a question with multiple choices. Your task is to choose the correct answer. 
            
          To submit your answer, please call the `submit_answer` tool with your answer as the argument.
        </instruction>
        """
    system_prompt = dedent(system_prompt).strip()

    choices = "\n".join(f"- {choice}" for choice in choices)
    user_prompt = f"""
    <question>
    {indent(question, 2)}
    </question>
    <choices>
    {indent(choices, 2)}
    </choices>
    """
    user_prompt = dedent(user_prompt).strip()

    _answer = None

    async def submit_answer(answer: str):
        if answer not in choices:
            return {"error": "Invalid choice.", "possible_choices": choices}
        nonlocal _answer
        _answer = answer
        return {"info": "Answer submitted."}

    bot = Bot("multiple_choice_bot", model_name=model_name, system_prompt=system_prompt)
    bot.register_function(submit_answer)
    bot.add_user_event(user_prompt)

    retry_num = 0
    while True:
        try:
            response = await bot.async_complete(
                max_tokens=100 if not think else 1024,
                temperature=0.2 if not deterministic else 0.0,
            )
            await bot.async_call_requested_tools(add_to_history=True)
        except Exception as e:
            logger.exception("API error in choose_one")
            if not robust:
                raise
            if retry_num >= num_tries:
                if default is None:
                    raise ValueError(
                        f"Failed to get valid choice after {num_tries} attempts due to API errors"
                    ) from e
                return default
            retry_num += 1
            continue

        if _answer is None:
            if retry_num >= num_tries:
                if isinstance(default, NoValue):
                    raise ValueError(
                        f"Failed to get valid choice after {num_tries} attempts"
                    )
                else:
                    return str(default)
            retry_num += 1
            bot.add_user_event(
                "<instruction>"
                "Please select one of the possible choices by calling the submit_answer tool. "
                "</instruction>"
            )
            continue
        if _answer is None:
            return default
        return cast(str, _answer)


async def choose_n(
    question: str,
    choices: List[str],
    n: int | None = None,
    *,
    min_choices: int = 1,
    max_choices: int | None = None,
    num_tries: int = 3,
    default: List[str] | None = None,
    model_name: str = DEFAULT_FLAGSHIP_MODEL,
    deterministic: bool = False,
    think: bool = False,
    robust: bool = False,
) -> List[str]:
    """Select multiple items from a list of choices.

    Args:
        question: The question to ask
        choices: List of possible choices
        n: Exact number of choices to select (overrides min/max_choices)
        min_choices: Minimum number of choices to select
        max_choices: Maximum number of choices to select
        num_tries: Number of retries on failure
        default: Default value if selection fails
        model_name: Name of the model to use
        deterministic: Whether to use deterministic sampling
        think: Whether to show thinking process
        robust: Whether to handle API errors gracefully
    """
    if n is not None:
        min_choices = max_choices = n
    elif max_choices is None:
        max_choices = len(choices)

    if think:
        system_prompt = """
        <instruction>
          You will be given a question with multiple choices. Please proceed as following:
          
          1. First, you must think out loud about the answers inside the <thinking>...</thinking> tag.
          2. After you have thought about it, call the `submit_answers` tool with your chosen answers.
          
          When choices are prefixed with indices (e.g. "0: some text", "1: other text"), 
          you MUST submit ONLY the numeric indices as your answers (e.g. ["0", "1"]).
        </instruction>
        """
    else:
        system_prompt = """
        <instruction>
          You will be given a question with multiple choices. Your task is to choose the correct answers.
            
          When choices are prefixed with indices (e.g. "0: some text", "1: other text"), 
          you MUST submit ONLY the numeric indices as your answers (e.g. ["0", "1"]).
          
          To submit your answers, please call the `submit_answers` tool with your answers as the argument.
        </instruction>
        """
    system_prompt = dedent(system_prompt).strip()

    choices_text = "\n".join(f"- {choice}" for choice in choices)
    user_prompt = f"""
    <question>
    {indent(question, 2)}
    </question>
    <choices>
    {indent(choices_text, 2)}
    </choices>
    <constraints>
    Please select between {min_choices} and {max_choices} choices.
    </constraints>
    """
    user_prompt = dedent(user_prompt).strip()

    _answers = None

    async def submit_answers(answers: List[str]):
        # Check if answers are indices
        if all(answer.isdigit() for answer in answers):
            # Convert indices to integers and validate range
            indices = [int(answer) for answer in answers]
            if not all(0 <= idx < len(choices) for idx in indices):
                return {
                    "error": f"Invalid indices: {answers}",
                    "num_choices": len(choices),
                }
        else:
            # Original validation for non-index answers
            if not all(answer in choices for answer in answers):
                invalid = [answer for answer in answers if answer not in choices]
                return {
                    "error": f"Invalid choices: {invalid}",
                    "possible_choices": choices,
                }

        if not min_choices <= len(answers) <= max_choices:
            return {
                "error": f"Must select between {min_choices} and {max_choices} choices. Selected: {len(answers)}"
            }
        nonlocal _answers
        _answers = answers
        return {"info": "Answers submitted."}

    bot = Bot("multiple_choice_bot", model_name=model_name, system_prompt=system_prompt)
    bot.register_function(submit_answers)
    bot.add_user_event(user_prompt)

    retry_num = 0
    while True:
        try:
            response = await bot.async_complete(
                max_tokens=100 if not think else 1024,
                temperature=0.2 if not deterministic else 0.0,
            )
            await bot.async_call_requested_tools(add_to_history=True)
        except Exception as e:
            logger.exception("API error in choose_n")
            if not robust:
                raise
            if retry_num >= num_tries:
                if default is None:
                    raise ValueError(
                        f"Failed to get valid choices after {num_tries} attempts due to API errors"
                    ) from e
                return default
            retry_num += 1
            continue

        if _answers is None:
            if retry_num >= num_tries:
                if default is None:
                    raise ValueError(
                        f"Failed to get valid choices after {num_tries} attempts"
                    )
                return default
            retry_num += 1
            bot.add_user_event(
                "<instruction>"
                "Please select your choices by calling the submit_answers tool."
                "</instruction>"
            )
            continue

        return cast(List[str], _answers)


async def list_items(
    instruction: str,
    *,
    model_name: str = DEFAULT_FLAGSHIP_MODEL,
    num_tries: int = 3,
    think: bool = False,
    deterministic: bool = False,
    robust: bool = False,
    default: List[str] | None = None,
) -> List[str]:
    if think:
        system_prompt = """
        <instruction>
          You will be given instructions for generating a list. Please proceed as following:

          1. First, you must think out loud about the items inside the <thinking>...</thinking> tag.
          2. After you have thought about it, call the `submit_list` tool with your list as the argument.
        </instruction>
        """
    else:
        system_prompt = """
        <instruction>
          You will be given instructions for generating a list. Your task is to generate the appropriate items.

          To submit your list, please call the `submit_list` tool with your list as the argument.
        </instruction>
        """
    system_prompt = dedent(system_prompt).strip()

    user_prompt = f"""
    <instruction>
    {indent(instruction, 2)}
    </instruction>
    """
    user_prompt = dedent(user_prompt).strip()

    _items = None

    async def submit_list(items: List[str]):
        nonlocal _items
        _items = items
        return {"info": "List submitted."}

    bot = Bot("list_items_bot", model_name=model_name, system_prompt=system_prompt)
    bot.register_function(submit_list)
    bot.add_user_event(user_prompt)

    retry_num = 0
    while True:
        try:
            response = await bot.async_complete(
                max_tokens=100 if not think else 1024,
                temperature=0.2 if not deterministic else 0.0,
            )
            await bot.async_call_requested_tools(add_to_history=True)
        except Exception as e:
            logger.exception("API error in list_items")
            if not robust:
                raise
            if retry_num >= num_tries:
                if default is None:
                    raise ValueError(
                        f"Failed to get list after {num_tries} attempts due to API errors"
                    ) from e
                return default
            retry_num += 1
            continue

        if _items is None:
            if retry_num >= num_tries:
                raise ValueError(f"Failed to get list after {num_tries} attempts")
            retry_num += 1
            bot.add_user_event(
                "<instruction>"
                "Please submit your list by calling the submit_list tool."
                "</instruction>"
            )
            continue
        if _items is None:
            return default
        return cast(List[str], _items)


async def summarize(
    text: str,
    on_fail: str = "Failed to summarize",
    model_name=DEFAULT_FLAGSHIP_MODEL,
    max_tokens: int = 1024,
    **do_it_kwargs,
) -> str:
    instruction = f"""
    You will be provided some text below, and your task is to summarize it. If you cannot summarize, please say "{on_fail}".
    
    ---
    
    {text}
    """
    instruction = dedent(instruction).strip()
    return await do_it(
        instruction=instruction,
        model_name=model_name,
        max_tokens=max_tokens,
        **do_it_kwargs,
    )


async def update_text(
    text: str,
    update: str,
    model_name: str = DEFAULT_FLAGSHIP_MODEL,
    max_tokens: int | None = None,
    **do_it_kwargs,
) -> str:
    if len(update) == 0:
        return text

    instruction = f"""
    You will be provided some text below, and your task is to update it with the new information. You may add, remove, or modify the text as needed. Return the updated text and nothing else.
    
    ---
    Text:
    
    {text}
    
    ---
    New Information:
    
    {update}
    """
    instruction = dedent(instruction).strip()

    # Compute the number of tokens needed
    if max_tokens is None:
        num_tokens = 1.25 * (count_tokens_in_str(text) + count_tokens_in_str(update))
        max_tokens = max(1024, int(num_tokens))

    return await do_it(
        instruction=instruction,
        model_name=model_name,
        max_tokens=max_tokens,
        **do_it_kwargs,
    )


async def produce_json(
    instruction: str,
    *,
    task_description: str | None = None,
    add_json_instructions: bool = None,
    custom_validator: Optional[Callable[[str], tuple[bool, str]]] = None,
    **do_it_kwargs,
) -> dict | list:
    if add_json_instructions is None:
        json_found_in_prompt = "json" in instruction.lower()
        if task_description is not None:
            json_found_in_prompt = (
                json_found_in_prompt or "json" in task_description.lower()
            )
        add_json_instructions = not json_found_in_prompt
    if add_json_instructions:
        instruction = (
            instruction
            + "\n\n"
            + "Please produce a JSON code block ```json\n...\n``` satisfying the instructions above."
        )

    if custom_validator is None:

        def json_validator(response_content: str) -> tuple[bool, str]:
            parsed = parse_json(response_content, raise_on_fail=False)
            if parsed is not None:
                return True, ""
            return (
                False,
                "Please provide a valid JSON object in a JSON code block, like this:\n\n```json\n...\n```",
            )

    else:
        json_validator = custom_validator

    result = await do_it(
        instruction,
        task_description=task_description,
        validator=json_validator,
        **do_it_kwargs,
    )
    return parse_json(result)


def text_function(
    *,
    model_name: str = DEFAULT_FLAGSHIP_MODEL,
    parse_only: bool = False,
    temperature: float = 0.2,
):
    """
    Decorator that allows a function to be called with a natural language description.

    Args:
        model_name: The model to use for parsing the natural language
        parse_only: If True, only returns the parsed arguments without executing the function
        temperature: The temperature to use for generating completions

    Returns:
        A decorated function that can accept a natural language description
    """

    def decorator(func: Callable) -> Callable:
        function_schema = get_function_schema(func)
        input_schema = function_schema["input_schema"]

        @wraps(func)
        async def wrapper(text_description: str, **kwargs) -> Any:
            # Parse the natural language description into function arguments
            instruction = f"""
            Your task is to parse the following natural language description into arguments for a function.
            
            Here is the natural language description of what the function needs to do:
            \"\"\"
            {text_description}
            \"\"\"
            
            Here is the JSON schema of the function arguments:
            ```json
            {indent(json.dumps(input_schema, indent=2), level=12)}
            ```
            
            Extract the appropriate parameters from the description and return them in a JSON code block, like this: 
            
            ```json
            <json object goes here>
            ```
            """
            instruction = dedent(instruction).strip()

            try:

                def validator(response_content: str):
                    parsed = parse_json(response_content, raise_on_fail=False)
                    if parsed is None:
                        return (
                            False,
                            "Please provide a valid JSON object in a JSON code block, "
                            "like this:\n\n```json\n...\n```",
                        )
                    is_valid, error_message = validate_against_schema(parsed, input_schema)
                    if not is_valid:
                        return False, error_message
                    return True, ""

                parsed_args = await produce_json(
                    instruction,
                    model_name=model_name,
                    temperature=temperature,
                    add_json_instructions=False,
                    custom_validator=validator,
                )

                # Update the parsed arguments with any additional keyword arguments
                parsed_args.update(kwargs)

                if parse_only:
                    return parsed_args

                # Call the function with the parsed arguments
                if inspect.iscoroutinefunction(func):
                    return await func(**parsed_args)
                return func(**parsed_args)

            except Exception as e:
                logger.exception(f"Error in text_function for {func.__name__}")
                raise ValueError(
                    f"Failed to parse natural language description: {str(e)}"
                ) from e

        return wrapper

    return decorator
