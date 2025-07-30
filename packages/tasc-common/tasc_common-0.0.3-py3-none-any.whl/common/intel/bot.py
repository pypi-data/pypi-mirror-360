import asyncio
import inspect
import json
import os
import time
import uuid
from collections.abc import Callable, Iterable, Mapping
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
from hashlib import sha256
from typing import Any, Union, Dict

import backoff as backoff
import tiktoken
from loguru import logger
from pydantic import BaseModel, field_validator, Field, model_validator
from pydantic_core.core_schema import ValidationInfo

from common.core.utils import get_time
from common.tools.tools import Tool
from common.intel.utils import (
    CONTEXT_LENGTHS,
    DEFAULT_CONTEXT_LENGTH_FALLBACKS,
    DEFAULT_FLAGSHIP_MODEL,
    DEFAULT_SMALL_EMBEDDING_MODEL,
    OutOfTokenCapError,
    clip_text,
    count_tokens_in_str,
    load_prompt,
)
from common.utils import (
    find_markdown_header,
    find_text_under_header,
    format_string,
    get_session_id,
    image_to_base64,
    extract_tag_content,
)


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict[str, Any]

    def state_dict(self):
        return self.model_dump(mode="python")

    def load_state_dict(self, state_dict: dict):
        self.id = state_dict["id"]
        self.name = state_dict["name"]
        self.arguments = state_dict["arguments"]
        return self

    def render(self):
        return {
            "function": {"arguments": json.dumps(self.arguments), "name": self.name},
            "id": self.id,
            "type": "function",
        }

    def get_num_tokens(self, model_name: str) -> int:
        return count_tokens_in_str(
            self.name, model_name=model_name
        ) + count_tokens_in_str(json.dumps(self.arguments), model_name=model_name)

    def __str__(self):
        return f"{self.name}({self.arguments})"


class Event(BaseModel):
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4().hex))
    # Main attries
    role: str
    content: str | dict[str, str] | None
    tag: str | None = None
    timestamp: float = Field(default_factory=get_time)
    # This is for images
    image_url: str | None = None
    image_detail: str = "auto"
    tool_calls: list[ToolCall | dict] | None = None

    tool_call_id: str | None = None
    name: str | None = None
    # This is for function calls (only valid when role is "assistant")
    # This is for function returns (only valid when role is "function")
    # name: Optional[str] = None

    @field_validator("role", mode="before")  # noqa
    @classmethod
    def validate_role(cls, role: Any, info: ValidationInfo):  # noqa
        if role not in ["user", "assistant", "system", "function", "tool"]:
            raise ValueError(f"Invalid role: {role}")
        return role

    def model_post_init(self, __context: Any) -> None:
        if self.name is not None:
            assert self.role in ["function", "tool"]
        if self.tool_call_id is not None:
            assert self.role in ["tool", "function"]

    @field_validator("tool_calls", mode="before")  # noqa
    @classmethod
    def validate_tool_calls(cls, tool_calls: Any, info: ValidationInfo):  # noqa
        def tool_call_dict_to_tool_call(tool_call_dict: dict):
            if {"id", "name", "arguments"}.issubset(set(tool_call_dict.keys())):
                return ToolCall(**tool_call_dict)
            elif {"function", "id", "type"}.issubset(set(tool_call_dict.keys())):
                arguments = json.loads(tool_call_dict["function"]["arguments"])
                name = tool_call_dict["function"]["name"]
                id = tool_call_dict["id"]
                return ToolCall(id=id, name=name, arguments=arguments)
            else:
                raise ValueError(
                    f"Invalid tool call dict with keys: {set(tool_call_dict.keys())}"
                )

        if tool_calls is not None:
            new_tool_calls = []
            for tool_call in tool_calls:
                if isinstance(tool_call, dict):
                    tool_call = tool_call_dict_to_tool_call(tool_call)
                elif isinstance(tool_call, BaseModel):
                    tool_call = tool_call_dict_to_tool_call(tool_call.model_dump())
                assert isinstance(
                    tool_call, ToolCall
                ), f"Tool call {tool_call} is not valid"
                new_tool_calls.append(tool_call)
            return new_tool_calls
        return tool_calls

    @field_validator("image_url", mode="before")  # noqa
    @classmethod
    def validate_image_url(cls, image_url: Any, info: ValidationInfo):  # noqa
        if image_url is not None:
            if not isinstance(image_url, str):
                raise ValueError(f"Invalid image URL: {image_url}")
            if os.path.exists(image_url):
                return image_to_base64(image_url)
        return image_url

    @field_validator("timestamp", mode="before")  # noqa
    @classmethod
    def validate_timestamp(cls, timestamp: Any, info: ValidationInfo):  # noqa
        if timestamp is not None:
            if not isinstance(timestamp, int | float):
                raise ValueError(f"Invalid timestamp: {timestamp}")
            timestamp = float(timestamp)
        else:
            timestamp = time.time()
        return timestamp

    @classmethod
    def from_mapping(cls, mapping: Mapping):
        try:
            # Mapping might have extra keys that we don't need
            return cls.model_validate(mapping)
        except Exception:
            logger.exception("Error creating event (lembork?)")
            raise

    @property
    def content_string(self) -> str | None:
        if isinstance(self.content, str):
            return self.content
        elif isinstance(self.content, dict):
            return self.content.get("text", None)
        else:
            return None

    @content_string.setter
    def content_string(self, value: str):
        if isinstance(self.content, str) or self.content is None:
            self.content = value
        elif isinstance(self.content, dict):
            self.content["text"] = value
        else:
            raise TypeError

    def get_num_tokens(self, model_name: str) -> int:
        try:
            encoding = tiktoken.encoding_for_model(model_name=model_name)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        tokens_per_message = 3
        num_tokens = tokens_per_message
        if self.tool_calls is not None:
            num_tokens += sum(
                [
                    tool_call.get_num_tokens(model_name=model_name)
                    for tool_call in self.tool_calls
                ]
            )
        if self.content_string is not None:
            num_tokens += len(
                encoding.encode(
                    self.content_string, allowed_special=encoding.special_tokens_set
                )
            )
        if self.image_url is not None:
            if self.image_detail == "low":
                num_tokens += 65
            elif self.image_detail in ["auto", "high"]:
                # It's actually 129 per crop, but we'll just say 129
                num_tokens += 129
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, item, value):
        setattr(self, item, value)

    def __contains__(self, item):
        return item in self.__dict__

    def __str__(self):
        event_str = f"{self.role.upper()}: {self.content_string}"
        if self.image_url is not None:
            event_str = f"{event_str} [+ IMAGE, Detail {self.image_detail}]"
        if self.tool_calls is not None:
            event_str = f"{event_str} [TOOL CALLS: {' | '.join([str(tool_call) for tool_call in self.tool_calls])}]"
        if self.name is not None:
            event_str = f"{event_str} [FUNCTION: {self.name}]"
        return event_str

    def get_tool_calls(
        self,
    ) -> list[ToolCall] | None:
        if self.role != "assistant":
            return None
        return self.tool_calls

    def state_dict(self):
        return self.model_dump(mode="python")

    def find_markdown_header_in_content(self, header: str) -> bool:
        if self.content_string is None:
            return False
        if not header.startswith("#"):
            header = f"# {header}"
        return find_markdown_header(self.content_string, header)

    def find_content_under_header(
        self,
        header: str,
        keep_subheaders: bool = True,
        break_on_horizontal_rules: bool = False,
        default: str | None = None,
    ) -> str | None:
        if self.content_string is None:
            return default
        if not header.startswith("#"):
            header = f"# {header}"
        text_under_header = find_text_under_header(
            self.content_string,
            header,
            keep_subheaders=keep_subheaders,
            break_on_horizontal_rules=break_on_horizontal_rules,
        )
        if text_under_header is None:
            return default
        else:
            return text_under_header

    def find_content_in_tag(self, tag: str) -> str | None:
        if self.content_string is None:
            return None
        return extract_tag_content(
            text=self.content_string,
            tag_name=tag,
        )

    def load_state_dict(self, state_dict: dict):
        self.uuid = state_dict.get("uuid", self.uuid)
        self.role = state_dict["role"]
        self.content = state_dict["content"]
        self.tag = state_dict["tag"]
        self.timestamp = state_dict["timestamp"]
        self.image_url = state_dict.get("image_url", None)
        self.image_detail = state_dict.get("image_detail", "auto")
        # This is to ensure that we can load old events in a consistent way
        if self.role == "assistant":
            self.tool_calls = [ToolCall(**state) for state in state_dict["tool_calls"]]
        else:
            self.tool_calls = None
        if self.role in ["tool", "function"]:
            self.name = state_dict["name"]
            self.tool_call_id = state_dict.get("tool_call_id", None)
        else:
            self.name = None
            self.tool_call_id = None
        return self

    def render(self) -> dict[str, str]:
        kwargs = {}
        if self.role == "assistant" and self.tool_calls is not None:
            kwargs["tool_calls"] = [tool_call.render() for tool_call in self.tool_calls]
        if self.role in ["tool", "function"]:
            kwargs["name"] = self.name
            kwargs["tool_call_id"] = self.tool_call_id

        # First determine the base content
        if isinstance(self.content, dict):
            # A single dict content should be wrapped in a list
            content = [self.content]
        elif self.content_string is not None:
            content = self.content_string
        else:
            content = None

        # Then handle image if present
        if self.image_url is not None:
            image_content = dict(
                type="image_url",
                image_url=dict(url=self.image_url, detail=self.image_detail),
            )
            if content is not None:
                # If we have both content and image
                if isinstance(content, str):
                    content = [dict(type="text", text=content), image_content]
                else:  # content is already a list
                    content.append(image_content)
            else:
                # Just image
                content = [image_content]

        return dict(role=self.role, content=content, **kwargs)

    def get_content_hash(self, exclude_timestamp: bool = False) -> str:
        content = [
            str(self.content_string),
            str(self.role),
            str(self.tag),
        ]
        if not exclude_timestamp:
            content.append(str(self.timestamp))
        if self.tool_calls is not None:
            content.extend(
                [tool_call.model_dump_json() for tool_call in self.tool_calls]
            )
        else:
            content.append("None")
        if self.name is not None:
            content.append(str(self.name))
        else:
            content.append("None")
        if self.image_url is not None:
            content.append(str(self.image_url))
        else:
            content.append("None")
        if self.image_detail is not None:
            content.append(str(self.image_detail))
        else:
            content.append("None")
        return sha256("+".join(content).encode("utf-8")).hexdigest()

    def add_tag(self, tag: str) -> "Event":
        if self.tag is None:
            self.tag = tag
        else:
            self.tag = f"{self.tag};{tag}"
        return self

    def contains_tag(self, tag: str) -> bool:
        if self.tag is None:
            return False
        return tag in self.tag.split(";")


class EventContainer(BaseModel):
    events: list[Event] = []

    def __len__(self):
        return len(self.events)

    def append(self, event: Event | dict[str, Any]):
        if isinstance(event, dict):
            event = Event(**event)
        self.events.append(event)

    def add(self, event: Event | dict[str, Any]) -> "EventContainer":
        self.append(event)
        return self

    def insert(self, index: int, event: Event | dict[str, Any]):
        if isinstance(event, dict):
            event = Event(**event)
        self.events.insert(index, event)

    def __iter__(self) -> Iterable[Event]:
        return iter(self.events)

    def __getitem__(self, index):
        return self.events[index]

    def __setitem__(self, index, value):
        self.events[index] = value

    def __delitem__(self, index):
        del self.events[index]

    def __contains__(self, item):
        return item in self.events

    def __reversed__(self):
        new_event = deepcopy(self)
        new_event.events = list(reversed(new_event.events))
        return new_event

    def __str__(self):
        lines = []
        for event in self:
            lines.append(str(event))
        return "\n\n------\n\n".join(lines)

    def extend(self, other: "EventContainer") -> "EventContainer":
        self.events.extend(other.events)
        return self

    def delete_at_indices(self, indices: list[int]) -> "EventContainer":
        for index in sorted(indices, reverse=True):
            del self.events[index]
        return self

    def get_num_tokens(self, model_name: str):
        return sum(event.get_num_tokens(model_name) for event in self.events)

    def state_dict(self) -> dict:
        return dict(events=[event.state_dict() for event in self.events])

    def load_state_dict(self, state_dict: dict):
        self.events = []
        for state in state_dict["events"]:
            self.events.append(Event.from_mapping(state))
        return self

    def clone(self) -> "EventContainer":
        return deepcopy(self)

    def render(self) -> list[dict[str, str]]:
        return [event.render() for event in self.events]

    def detect_duplicate_events(
        self,
        start_index: int = 0,
        stop_index: int | None = None,
        step: int = 1,
        event_filter: Callable[[Event], bool] | None = None,
    ) -> bool:
        events = self.events[start_index:stop_index:step]
        # Filter based on the filter function
        if event_filter is not None:
            events = [event for event in events if event_filter(event)]
        # Get the hashes
        hashes = [event.get_content_hash(exclude_timestamp=True) for event in events]
        # Check if there are duplicates
        return len(hashes) != len(set(hashes))


class HistoryProcessor:
    async def process(self, container: EventContainer, **kwargs) -> EventContainer:
        raise NotImplementedError

    async def __call__(self, container: EventContainer, **kwargs) -> EventContainer:
        return await self.process(container, **kwargs)

    @staticmethod
    async def apply_pipeline(
        history_processors: list["HistoryProcessor"],
        container: EventContainer,
        **kwargs,
    ) -> EventContainer:
        for processor in history_processors:
            container = await processor(container, **kwargs)
        return container


class EventTruncater(HistoryProcessor):
    def __init__(
        self,
        model_name: str = DEFAULT_FLAGSHIP_MODEL,
        context_length: int | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.model_name = model_name
        if context_length is not None:
            self.context_length = context_length
        else:
            self.context_length = CONTEXT_LENGTHS.get(self.model_name, 4096)

    def is_noop(self, total_tokens: int) -> bool:
        if total_tokens < self.context_length:
            return True
        return False

    async def process(self, container: EventContainer, **kwargs) -> EventContainer:
        raise NotImplementedError


class ResponseProcessor:
    def __init__(self, fn: callable, one_time_use: bool = False, static: bool = True):
        # Make sure fn is a coro
        if not inspect.iscoroutinefunction(fn):
            raise ValueError("ResponseProcessor function must be natively async.")
        # Public
        self.fn = fn
        self.one_time_use = one_time_use
        self.static = static
        # Privates
        self._is_used = False

    @property
    def is_used(self):
        if self._is_used and self.one_time_use:
            return True
        return False

    async def __call__(self, event: Event, **kwargs) -> Event:
        if self.is_used:
            return event
        self._is_used = True
        if self.static:
            return await self.fn(event, **kwargs)
        else:
            return await self.fn(self, event, **kwargs)

    @staticmethod
    async def apply_pipeline(
        response_processors: list["ResponseProcessor"],
        event: Event,
        remove_used_processors_in_place: bool = True,
        **kwargs,
    ) -> Event:
        # Remove the used processors
        if remove_used_processors_in_place:
            # Loop over the processors and delete the ones that are used
            response_processors[:] = [
                processor for processor in response_processors if not processor.is_used
            ]
        else:
            # Loop over the processors and delete the ones that are used
            response_processors = [
                processor for processor in response_processors if not processor.is_used
            ]

        for processor in response_processors:
            event = await processor(event, **kwargs)
        return event


class ChatHistory:
    def __init__(
        self,
        system_prompt: str | None = None,
        history_processors: list["HistoryProcessor"] = None,
        response_processors: list["ResponseProcessor"] = None,
    ):
        # Private
        self._container = EventContainer()
        # Public
        self.history_processors = history_processors or []
        self.response_processors = response_processors or []
        # Logics
        if system_prompt is not None:
            self.add_system_event(system_prompt)

    @staticmethod
    def create_api_event(
        role: str, content: str, tag: str | None = None, **kwargs
    ) -> Event:
        event = Event(role=role, content=str(content), tag=tag, **kwargs)
        return event

    @property
    def system_prompt(self) -> str | None:
        for event in self._container:
            if event["role"] == "system":
                return event["content"]

    def update_system_prompt(self, prompt: str) -> None:
        for event in self._container:
            if event["role"] == "system":
                event["content"] = prompt
                return

    @property
    def events(self) -> EventContainer:
        return self._container.clone()

    def register_history_processor(self, history_processor: HistoryProcessor):
        self.history_processors.append(history_processor)
        return self

    def register_response_processor(self, response_processor: ResponseProcessor):
        self.response_processors.append(response_processor)
        return self

    def add_event(self, content: str, role: str, **kwargs) -> "ChatHistory":
        self._container.append(self.create_api_event(role, content, **kwargs))
        return self

    def add_system_event(self, content: str, **kwargs) -> "ChatHistory":
        self.add_event(content, role="system", **kwargs)
        return self

    def add_user_event(self, content: str, **kwargs) -> "ChatHistory":
        self.add_event(content, role="user", **kwargs)
        return self

    def add_function_event(
        self, function_name: str, function_result: Any
    ) -> "ChatHistory":
        self.add_event(
            json.dumps(function_result, indent=2),
            role="function",
            name=function_name,
        )
        return self

    def add_tool_event(
        self, tool_name: str, tool_call_id: str, tool_result: Any, role: str = "tool"
    ) -> "ChatHistory":
        self.add_event(
            content=json.dumps(tool_result, indent=2),
            role=role,
            name=tool_name,
            tool_call_id=tool_call_id,
        )
        return self

    async def record_response(self, event: Mapping) -> "Event":
        assert "role" in event
        assert "content" in event
        event = Event.from_mapping(event)
        # Process the event
        event = await ResponseProcessor.apply_pipeline(
            self.response_processors, event, remove_used_processors_in_place=True
        )
        self._container.append(event)
        return event

    def get_most_recent_assistant_event(self) -> Event | None:
        for event in reversed(self._container):
            if event["role"] == "assistant":
                return event
        return None

    def get_most_recent_assistant_event_by_content_match(
        self, content_to_match: str
    ) -> Event | None:
        for event in reversed(self._container):
            if event["role"] == "assistant" and content_to_match in event["content"]:
                return event
        return None

    def get_most_recent_event(self) -> Event | None:
        if len(self._container) == 0:
            return None
        return self._container[-1]

    async def render(
        self,
        system_prompt_format_kwargs: dict | None = None,
        num_additional_tokens: int = 1024,
        render_container: bool = True,
    ) -> list[dict[str, Any]] | EventContainer:
        # Format with system prompt. This needs to happen first because it
        # adds tokens.
        container = deepcopy(self._container)
        if system_prompt_format_kwargs is not None:
            for event in container:
                if event["role"] == "system":
                    event["content"] = format_string(
                        event["content"], **system_prompt_format_kwargs
                    )
        # Process the container
        container = await HistoryProcessor.apply_pipeline(
            self.history_processors,
            container=container,
            num_additional_tokens=num_additional_tokens,
        )
        # Render the container
        if render_container:
            return container.render()
        else:
            return container

    def state_dict(self) -> dict:
        return dict(container=self._container.state_dict())

    def load_state_dict(self, state_dict: dict) -> "ChatHistory":
        self._container.load_state_dict(state_dict["container"])
        return self

    def __str__(self):
        return str(self._container)


class Bot:
    VERSION_PREFERENCES = {}
    TOKEN_CAP = 100_000

    def __init__(
        self,
        name,
        model_name,
        *,
        system_prompt: str | None = None,
        context_length: int | None = None,
        fallback_when_out_of_context: bool = False,
        out_of_context_fallback_model_name: str | None = None,
        on_error_fallback_model_name: str | None = None,
        max_num_parsing_attempts_per_completion: int = 1,
        system_prompt_format_kwargs: dict | None = None,
        token_cap: int | None = None,
        prompt_version: str | None = None,
        prompt_dir: str | None = None,
    ):
        # Get the names
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.name = f"{name}__{model_name}__{get_session_id()}__{timestamp}__{str(uuid.uuid4().hex[:5])}"
        self.model_name = model_name
        if out_of_context_fallback_model_name is None and fallback_when_out_of_context:
            out_of_context_fallback_model_name = DEFAULT_CONTEXT_LENGTH_FALLBACKS.get(
                model_name
            )
        self.out_of_context_fallback_model_name = out_of_context_fallback_model_name
        self.on_error_fallback_model_name = on_error_fallback_model_name
        self.max_num_parsing_attempts_per_completion = (
            max_num_parsing_attempts_per_completion
        )

        # History business
        self.user_prompt = None
        if context_length is None:
            self.context_length = CONTEXT_LENGTHS.get(model_name, 4096)
        else:
            self.context_length = context_length
        if token_cap is None:
            self.token_cap = self.TOKEN_CAP
        else:
            self.token_cap = token_cap

        # Try to load the system prompt from disk if it's not provided
        if system_prompt is None:
            try:
                prompt_version = prompt_version or self.VERSION_PREFERENCES.get(
                    name, None
                )
                system_prompt, user_prompt = load_prompt(
                    name, prompt_version, prompt_dir=prompt_dir
                )
                self.user_prompt = user_prompt
            except FileNotFoundError:
                logger.warning(
                    "Initializing bot without system prompt. This is OK if loading a bot from history."
                )
        if system_prompt_format_kwargs is not None:
            system_prompt = format_string(system_prompt, **system_prompt_format_kwargs)

        # History
        self.history = ChatHistory(system_prompt=system_prompt)

        # Functions
        self._functions = {}
        self._enabled_functions = set()

    @property
    def system_prompt(self):
        return self.history.system_prompt

    def format_user_prompt(self, **kwargs) -> str:
        if self.user_prompt is None:
            raise ValueError("User prompt not set.")
        return format_string(self.user_prompt, **kwargs)

    def add_user_event(self, content: str, **kwargs) -> "Bot":
        self.history.add_user_event(content, **kwargs)
        return self

    def format_and_add_user_event(self, **kwargs) -> "Bot":
        if self.user_prompt is None:
            raise ValueError("User prompt is not set.")
        user_prompt = self.format_user_prompt(**kwargs)
        self.add_user_event(user_prompt)
        return self

    @classmethod
    def register_version_preference(cls, name: str, version_string: str) -> type:
        cls.VERSION_PREFERENCES[name] = version_string
        return cls

    def register_history_processor(self, history_processor: HistoryProcessor):
        self.history.register_history_processor(history_processor)
        return self

    def register_function(
        self,
        function: Tool | Callable[[Any], Any],
        enabled: bool = True,
    ) -> "Bot":
        if isinstance(function, Tool):
            tool = function
        else:
            tool = Tool.from_function(function)
        self._functions[tool.name] = tool
        if enabled:
            self.enable_function(tool.name)
        return self

    def enable_function(self, name: str) -> "Bot":
        self._enabled_functions.add(name)
        return self

    def enable_all_functions(self):
        self._enabled_functions = set(self._functions.keys())
        return self

    def disable_function(self, name: str) -> "Bot":
        self._enabled_functions.remove(name)
        return self

    def disable_all_functions(self):
        self._enabled_functions = set()
        return self

    def get_function(self, name: str) -> "Tool":
        return self._functions[name]

    @contextmanager
    def these_functions_enabled(self, functions: list[str]):
        enabled_functions = self._enabled_functions
        self._enabled_functions = set(functions)
        yield
        self._enabled_functions = enabled_functions

    def get_schema_for_enabled_functions(self):
        for name in self._enabled_functions:
            yield self._functions[name].generate_openai_schema()

    def load_system_prompt(self, name: str, prompt_version: str | None = None):
        prompt_version = prompt_version or self.VERSION_PREFERENCES.get(name, None)
        system_prompt, user_prompt = load_prompt(name, prompt_version)
        self.history.update_system_prompt(system_prompt)
        self.user_prompt = user_prompt
        return self

    async def async_complete(
        self,
        max_tokens: int = 1024,
        temperature: float | None = 0.0,
        stop: str | list[str] | None = None,
        system_prompt_format_kwargs: dict | None = None,
        max_num_parsing_attempts: int = 1,
        completion_logger: Union[Callable, None] = None,
        completion_kwargs_keymap: Dict[str, str] = None,
        **completion_kwargs,
    ) -> Event:
        # Litellm fetches stuff, which means the code becomes
        # unrunnable without an internet connection if the import is global.
        import litellm

        litellm.drop_params = True
        # litellm.modify_params = True

        # Build kwargs for litellm
        kwargs = dict(max_tokens=max_tokens)
        if temperature is not None:
            kwargs["temperature"] = temperature

        # Functions
        functions = list(self.get_schema_for_enabled_functions())
        if len(functions) > 0:
            kwargs["tools"] = functions

        # Stop tokens
        if stop is not None:
            if isinstance(stop, str):
                stop = [stop]
            kwargs["stop"] = stop

        # num_function_tokens = num_tokens_from_functions(functions, self.model_name)
        num_function_tokens = 0
        token_buffer_size = 25
        history_container = await self.history.render(
            system_prompt_format_kwargs=system_prompt_format_kwargs,
            num_additional_tokens=max_tokens + num_function_tokens,
            render_container=False,
        )

        if self.out_of_context_fallback_model_name is not None:
            total_tokens = (
                history_container.get_num_tokens(self.model_name)
                + max_tokens
                + num_function_tokens
                + token_buffer_size
            )
            # Check if we'll run out of context
            if total_tokens > self.context_length:
                model_name = self.out_of_context_fallback_model_name
            else:
                model_name = self.model_name
        else:
            model_name = self.model_name

        rendered_history = history_container.render()
        num_history_tokens = history_container.get_num_tokens(model_name)
        total_possible_tokens = (
            num_history_tokens + max_tokens + num_function_tokens + 25
        )

        if total_possible_tokens > self.token_cap:
            raise OutOfTokenCapError(
                f"Total possible tokens ({total_possible_tokens}) exceeds token cap ({self.token_cap})."
            )

        logger.debug(
            f"Passing into {model_name} num_history_tokens: {num_history_tokens}, "
            f"num_generation_tokens: {max_tokens}, "
            f"num_function_tokens: {num_function_tokens}; "
            f"total_possible_tokens: {total_possible_tokens}"
        )

        @backoff.on_exception(
            backoff.expo,
            (
                litellm.exceptions.RateLimitError,
                litellm.exceptions.ServiceUnavailableError,
                litellm.exceptions.Timeout,
                litellm.exceptions.APIError,
                litellm.exceptions.APIConnectionError,
                litellm.exceptions.InternalServerError,
            ),
            max_time=45,
        )
        async def _acompletion(_model_name):
            all_completion_kwargs = {**kwargs, **completion_kwargs}
            if completion_kwargs_keymap is not None:
                all_completion_kwargs = {
                    completion_kwargs_keymap.get(key, key): value
                    for key, value in all_completion_kwargs.items()
                    if completion_kwargs_keymap.get(key, key) is not None
                }
            return await litellm.acompletion(
                model=_model_name,
                messages=deepcopy(rendered_history),
                **all_completion_kwargs,
            )

        try_count = 0
        completion_error_count = 0
        event = None
        max_num_parsing_attempts = max(
            max_num_parsing_attempts, self.max_num_parsing_attempts_per_completion
        )
        while True:
            try_count += 1

            try:
                response = await _acompletion(model_name)
            except Exception as e:
                completion_error_count += 1

                if self.on_error_fallback_model_name is None:
                    logger.exception(
                        f"Exception with model: {model_name}. "
                        f"No fallback model found, raising."
                    )
                    # If we're here, there's no model to fall back to so we raise
                    # the exception.
                    raise
                elif completion_error_count > 1:
                    logger.exception(
                        f"Exception with fallback model: {model_name}. Well, shit."
                    )
                    # If we're here, then the fallback model has failed.
                    raise
                else:
                    # Swap out the model
                    logger.error(
                        f"Original model call raised: {str(e)}. "
                        f"Swapping out model {model_name} with fallback "
                        f"model: {self.on_error_fallback_model_name}."
                    )
                    model_name = self.on_error_fallback_model_name
                    continue

            if completion_logger is not None:
                try:
                    if inspect.iscoroutinefunction(completion_logger):
                        await completion_logger(
                            deepcopy(rendered_history),
                            response.model_dump(),
                            model_name,
                        )
                    else:
                        completion_logger(
                            deepcopy(rendered_history),
                            response.model_dump(),
                            model_name,
                        )
                except Exception as e:
                    logger.error(f"Ignoring exception in completion logger: {str(e)}")

            try:
                message = response.choices[0].message
                # This might transform the response, depending on the attached processors.
                # We want this to be async because there might be more lem calls involved,
                # and we don't want that to block the event loop.
                event = await self.history.record_response(message.model_dump())
                break
            except Exception:
                logger.exception("Failed to parse.")
                if try_count >= max_num_parsing_attempts:
                    raise
                else:
                    logger.debug("Retrying completion.")
                    continue

        assert event is not None, "Event is None after completion."

        return event

    def complete(
        self,
        max_tokens: int = 1024,
        temperature: float = 0.0,
        stop: str | list[str] | None = None,
        system_prompt_format_kwargs: dict | None = None,
    ):
        return asyncio.run(
            self.async_complete(
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop,
                system_prompt_format_kwargs=system_prompt_format_kwargs,
            )
        )

    async def async_call_requested_tools(
        self,
        add_to_history: bool = True,
        run_in_parallel: bool = True,
        raise_on_fail: bool = False,
        exception_logger: Union[Callable, None] = None,
    ) -> dict[str, Any] | None:
        event = self.history.get_most_recent_assistant_event()

        if event.tool_calls is None:
            # No tools to call
            return None

        tool_calls = event.get_tool_calls()
        tool_call_response_pairs = []

        async def call_tool(tool_call: ToolCall):
            tool = None
            try:
                # Get the tool first
                tool = self._functions.get(tool_call.name)
                if tool is None:
                    return dict(
                        status="error",
                        info=(
                            f"Tool '{tool_call.name}' was not found. "
                            f"Possible tools are: {', '.join(self._functions.keys())}"
                        ),
                    )
                logger.debug(f"Tool call: {tool_call.name}({tool_call.arguments})")
                tool_response = await tool(**tool_call.arguments)
            except Exception as e:
                # Now the linter knows tool is definitely defined
                logger.exception("Error calling tool.")
                tool_response = dict(
                    status="error",
                    error_type=e.__class__.__name__,
                    error_message=str(e),
                    tool_info=dict(
                        name=getattr(tool, "name", None),
                        argument_schema=getattr(tool, "argument_schema", None),
                    ),
                )
                if exception_logger is not None:
                    try:
                        if inspect.iscoroutinefunction(exception_logger):
                            await exception_logger(tool_call, tool_response, e)
                        else:
                            exception_logger(tool_call, tool_response, e)
                    except Exception as e:
                        logger.error(
                            f"Ignoring exception in exception logger: {str(e)}"
                        )
                if raise_on_fail:
                    raise
            return tool_response

        if run_in_parallel:
            tool_responses = await asyncio.gather(
                *[call_tool(tool_call) for tool_call in tool_calls]
            )
            tool_call_response_pairs = [
                (tool_call, tool_response)
                for tool_call, tool_response in zip(
                    tool_calls, tool_responses, strict=False
                )
            ]
        else:
            for tool_call in tool_calls:
                tool_response = await call_tool(tool_call)
                tool_call_response_pairs.append((tool_call, tool_response))

        if add_to_history:
            for tool_call, tool_response in tool_call_response_pairs:
                # Store in history if needed
                self.history.add_tool_event(
                    tool_name=tool_call.name,
                    tool_call_id=tool_call.id,
                    tool_result=tool_response,
                    role="tool",
                )

        return {
            tool_call.name: tool_response
            for tool_call, tool_response in tool_call_response_pairs
        }

    def call_requested_tools(
        self, add_to_history: bool = True, run_in_parallel: bool = True
    ) -> Any:
        return asyncio.run(
            self.async_call_requested_tools(add_to_history, run_in_parallel)
        )

    def enable_context_length_fallback(self) -> "Bot":
        self.out_of_context_fallback_model_name = DEFAULT_CONTEXT_LENGTH_FALLBACKS.get(
            self.model_name
        )
        return self

    def state_dict(self) -> dict:
        state = dict(
            name=self.name,
            model_name=self.model_name,
            out_of_context_fallback_model_name=self.out_of_context_fallback_model_name,
        )
        state["history"] = self.history.state_dict()
        return state

    def load_state_dict(self, state_dict: dict, strict: bool = False) -> "Bot":
        if strict:
            assert (
                self.model_name == state_dict["model_name"]
            ), f"Model name mismatch: {self.model_name} != {state_dict['model_name']}"
        if "history" in state_dict:
            self.history.load_state_dict(state_dict["history"])
        elif strict:
            raise ValueError("State dict does not have 'history' key.")
        return self

    @classmethod
    def from_path(
        cls,
        path: str,
        bot_name: str | None = None,
        model_name: str | None = None,
    ) -> "Bot":
        if os.path.isfile(path):
            file = path
        else:
            raise ValueError(f"Invalid path: {path}")
        with open(file) as f:
            state_dict = json.load(f)
        logger.debug(f"Loaded state dict from {file}.")
        return cls.from_dict(state_dict, bot_name=bot_name, model_name=model_name)

    @classmethod
    def from_dict(
        cls,
        state_dict: dict,
        bot_name: str | None = None,
        model_name: str | None = None,
    ) -> "Bot":
        if bot_name is None:
            bot_name = state_dict["name"].split("__")[0]

        if model_name is None:
            model_name = state_dict["model_name"]

        logger.debug(f"Creating bot {bot_name} with model {model_name}.")

        bot = cls(name=bot_name, model_name=model_name)
        bot.load_state_dict(state_dict)
        return bot


async def async_embed(
    text: str,
    model_name: str = "text-embedding-3-small",
    clip_if_too_long: bool = True,
    **embedder_kwargs,
) -> list[float]:
    import litellm

    litellm.drop_params = True
    # litellm.modify_params = True

    if clip_if_too_long:
        # TODO: Make this work for other embedding models
        # Clip text to a maximum of 8192 tokens
        text = clip_text(text, 8192, model_name)

    @backoff.on_exception(
        backoff.expo,
        (
            litellm.exceptions.RateLimitError,
            litellm.exceptions.ServiceUnavailableError,
            litellm.exceptions.Timeout,
            litellm.exceptions.APIError,
        ),
        max_time=180,
    )
    async def _get_embedding(_text):
        # we need to handle the case where the text is empty and still return an embedding, perhaps by using " "
        if _text == "":
            _text = " "
        response = await litellm.aembedding(
            model=model_name, input=[_text], **embedder_kwargs
        )
        embedding = response["data"][0]["embedding"]
        return embedding

    return await _get_embedding(text)


async def async_batch_embed(
    texts: list[str],
    model_name: str = DEFAULT_SMALL_EMBEDDING_MODEL,
    clip_if_too_long: bool = True,
    **kwargs,
) -> list[list[float]]:
    import litellm

    if clip_if_too_long:
        # Clip text to a maximum of 8192 tokens
        texts = [clip_text(text, 8192, model_name) for text in texts]

    @backoff.on_exception(
        backoff.expo,
        (
            litellm.exceptions.RateLimitError,
            litellm.exceptions.ServiceUnavailableError,
            litellm.exceptions.Timeout,
            litellm.exceptions.APIError,
        ),
        max_time=180,
    )
    async def _get_embedding(_texts):
        return await litellm.aembedding(input=_texts, model=model_name, **kwargs)

    embeddings = await _get_embedding(texts)
    embeddings = [embedding["embedding"] for embedding in embeddings["data"]]
    return embeddings
