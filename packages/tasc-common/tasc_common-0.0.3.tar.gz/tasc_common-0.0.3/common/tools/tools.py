import inspect
from enum import Enum
from typing import Callable, Any, Dict, List, Union

import docstring_parser
import jsonref
from pydantic import BaseModel, field_validator, create_model
from pydantic_core.core_schema import ValidationInfo

from common.utils import camel_to_snake


class ToolDataType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    NULL = "null"
    ARRAY = "array"
    OBJECT = "object"
    ANY_OF = "anyOf"
    ANY = "any"


class ToolArgument(BaseModel):
    name: str
    description: str | None = None
    props: Union[ToolDataType, Dict[str, Any]]
    required: bool = False
    default: Any = None

    @property
    def type(self):
        return (
            self.props.get("type", ToolDataType.ANY)
            if isinstance(self.props, dict)
            else self.props
        )

    def to_dict(self) -> dict:
        if isinstance(self.props, str):
            result = {"type": self.props}
        elif isinstance(self.props, dict):
            result = self.props.copy()  # Use the entire dictionary
        else:
            result = {
                "type": "any"
            }  # Fallback to 'any' if type is neither string nor dict

        if self.description:
            result["description"] = self.description
        if self.default is not None:
            result["default"] = self.default
        return result


class Tool(BaseModel):
    name: str
    description: str | None = None
    arguments: List[ToolArgument] = []
    tool_fn: Callable[..., Any] | None = None

    @property
    def argument_schema(self) -> dict:
        """Returns a schema describing the tool's arguments."""
        return {
            "type": "object",
            "properties": {
                arg.name: arg.to_dict() for arg in self.arguments
            },
            "required": [arg.name for arg in self.arguments if arg.required]
        }

    async def __call__(self, *args, **kwargs) -> Any:
        if self.tool_fn is None:
            raise NotImplementedError("Tool function not defined.")
        arguments = kwargs
        for arg, arg_spec in zip(args, self.arguments, strict=False):
            arguments[arg_spec.name] = arg
        return await self.tool_fn(**arguments)

    @staticmethod
    def signature_to_json_schema(func: Callable) -> dict:
        sig = inspect.signature(func)
        fields = {}

        for name, param in sig.parameters.items():
            if param.annotation is inspect.Parameter.empty:
                raise ValueError(f"Parameter '{name}' is missing type annotation")

            default = ... if param.default is inspect.Parameter.empty else param.default
            fields[name] = (param.annotation, default)

        model_name = f"{func.__name__.capitalize()}Model"
        model = create_model(model_name, **fields)
        schema = model.model_json_schema()

        if "$defs" in schema:
            # Resolve jsonrefs
            schema = jsonref.replace_refs(schema)

        # Remove 'title' from the main schema
        schema.pop("title", None)

        # Remove 'title' from each property
        for prop in schema["properties"].values():
            prop.pop("title", None)

        return schema

    @classmethod
    def from_function(cls, func: Callable):
        # Check if func is a callable class object
        if inspect.isfunction(func) or inspect.iscoroutinefunction(func):
            fn_name = func.__name__
        else:
            # This is the case where func is a callable class or method
            assert callable(func)
            if getattr(func, "tool_name", None) is not None:
                fn_name = func.tool_name
            else:
                # Handle instance methods
                if hasattr(func, '__func__'):  # Instance method
                    fn_name = func.__func__.__name__
                else:
                    fn_name = camel_to_snake(func.__class__.__name__)  # noqa
                    func = func.__call__  # noqa

        # For instance methods, we need to check __func__
        is_async = inspect.iscoroutinefunction(func) or (
            hasattr(func, '__func__') and inspect.iscoroutinefunction(func.__func__)
        )
        if not is_async:
            raise ValueError("Tool functions must be async.")

        docstring = docstring_parser.parse(inspect.getdoc(func))
        description = docstring.short_description
        if docstring.long_description:
            description += "\n\n" + docstring.long_description

        schema = cls.signature_to_json_schema(func)

        arguments = []
        for name, prop in schema["properties"].items():
            arg = ToolArgument(
                name=name,
                description=next(
                    (p.description for p in docstring.params if p.arg_name == name),
                    None,
                ),
                props=prop,  # Store the entire property dictionary
                required=name in schema.get("required", []),
                default=prop.get("default"),
            )
            arguments.append(arg)

        return cls(
            name=fn_name, description=description, arguments=arguments, tool_fn=func
        )

    @classmethod
    def from_openai_schema(cls, schema: dict) -> "Tool":
        if schema["type"] != "function":
            raise ValueError("Schema must be of type 'function'")

        function_data = schema["function"]
        name = function_data["name"]
        description = function_data.get("description", "")

        parameters = function_data["parameters"]
        if parameters["type"] != "object":
            raise ValueError("Parameters must be of type 'object'")

        arguments = []
        for arg_name, arg_schema in parameters["properties"].items():
            argument = ToolArgument(
                name=arg_name,
                description=arg_schema.get("description"),
                props=arg_schema,  # Store the entire schema as the type
                required=arg_name in parameters.get("required", []),
                default=arg_schema.get("default"),
            )
            arguments.append(argument)

        return cls(name=name, description=description, arguments=arguments)

    def generate_openai_schema(self) -> dict:
        parameters = {"type": "object", "properties": {}, "required": []}

        for arg in self.arguments:
            parameters["properties"][arg.name] = arg.to_dict()
            if arg.required:
                parameters["required"].append(arg.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description if self.description else "",
                "parameters": parameters,
            },
        }


class ToolCollection(BaseModel):
    tools: list[Tool]

    def generate_openai_schema(self) -> list[dict]:
        return [tool.generate_openai_schema() for tool in self.tools]

    @classmethod
    def from_openai_schema(cls, schema: list[dict]) -> "ToolCollection":
        tools = [Tool.from_openai_schema(tool_schema) for tool_schema in schema]
        return cls(tools=tools)

    @classmethod
    def from_openapi_schema(cls, schema: dict) -> "ToolCollection":
        openai_schema = openapi_schema_to_openai_schema(schema)
        return cls.from_openai_schema(openai_schema)


def openapi_schema_to_openai_schema(schema: dict) -> list[dict]:
    functions = []

    for path, methods in schema["paths"].items():
        for method, spec_with_ref in methods.items():
            # 1. Resolve JSON references.
            spec = jsonref.replace_refs(spec_with_ref)

            # 2. Extract a name for the functions.
            function_name = spec.get("operationId")

            # 3. Extract a description and parameters.
            desc = spec.get("description") or spec.get("summary", "")

            schema = {"type": "object", "properties": {}}

            req_body = (
                spec.get("requestBody", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema")
            )
            if req_body:
                schema["properties"]["requestBody"] = req_body

            params = spec.get("parameters", [])
            if params:
                param_properties = {
                    param["name"]: param["schema"]
                    for param in params
                    if "schema" in param
                }
                schema["properties"]["parameters"] = {
                    "type": "object",
                    "properties": param_properties,
                }

            functions.append(
                {
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "description": desc,
                        "parameters": schema,
                    },
                }
            )

    return functions


class PluginMessage(BaseModel):
    from_plugin: str
    payload: Dict[str, Any]
