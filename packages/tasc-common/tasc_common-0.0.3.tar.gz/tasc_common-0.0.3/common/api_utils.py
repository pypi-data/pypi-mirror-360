from enum import Enum
from typing import Any, Type, TypeVar

import httpx
import asyncio
from loguru import logger

from pydantic import BaseModel


PayloadModel = TypeVar("PayloadModel", bound=BaseModel)


class APIResponseStatus(str, Enum):
    OK = "ok"
    ERROR = "error"
    FAIL = "fail"


class OTPAPIResponse(BaseModel):
    status: APIResponseStatus
    message: str = None
    token: str
    otp: str


class APIConnectionError(ConnectionError):
    pass


class APIResponse(BaseModel):
    status: APIResponseStatus
    message: str = None
    payload: dict | None = None
    status_code: int | None = None
    token: str | None = None

    @classmethod
    def success(cls, message: str, payload: dict | None = None):
        return cls(status=APIResponseStatus.OK, message=message, payload=payload)

    @classmethod
    def error(cls, message: str, payload: dict | None = None):
        return cls(status=APIResponseStatus.ERROR, message=message, payload=payload)

    @classmethod
    def fail(cls, message: str, payload: dict | None = None):
        return cls(status=APIResponseStatus.FAIL, message=message, payload=payload)

    def raise_if_not_successful(self, exception_cls) -> "APIResponse":
        if self.status != APIResponseStatus.OK:
            raise exception_cls(self.message)
        return self

    def validate_payload(
        self, payload_model_cls: Type[PayloadModel], empty_if_none: bool = True
    ) -> PayloadModel | None:
        if self.payload is None:
            if empty_if_none:
                return payload_model_cls()
            else:
                return None
        else:
            return payload_model_cls.model_validate(self.payload)

    def to_dict(self) -> dict:
        return self.model_dump(exclude_unset=True)


class ParameterLocation(str, Enum):
    QUERY = "query"
    PATH = "path"
    HEADER = "header"
    BODY = "body"


class Parameter(BaseModel):
    name: str
    location: ParameterLocation
    description: str | None = None
    required: bool = False
    schema_type: str | None = None
    default: Any = None
    schema: dict | None = None

    @classmethod
    def from_openapi(cls, param_dict: dict) -> "Parameter":
        return cls(
            name=param_dict["name"],
            location=ParameterLocation(param_dict["in"]),
            description=param_dict.get("description"),
            required=param_dict.get("required", False),
            schema_type=param_dict.get("schema", {}).get("type"),
            default=param_dict.get("schema", {}).get("default"),
            schema=param_dict.get("schema"),
        )


class EndpointModel(BaseModel):
    url: str
    method: str = "POST"
    headers: dict = {}
    parameters: dict[str, Parameter] = {}

    @classmethod
    def from_openapi_path(
        cls,
        base_url: str,
        path: str,
        path_item: dict,
        token: str = None,
        api_key: str = None,
    ) -> "EndpointModel":
        """
        Construct an EndpointModel from an OpenAPI path specification.

        Args:
            base_url: The base URL of the API (e.g., 'https://api.example.com')
            path: The path string (e.g., '/pets/{petId}')
            path_item: The OpenAPI path item object containing the operation details
            token: An optional bearer token to include in the headers
            api_key: An optional API key to include in the headers

        Returns:
            EndpointModel: A configured endpoint model

        Raises:
            ValueError: If no valid HTTP method is found in the path item
        """
        # Find the first valid HTTP method in the path item
        valid_methods = {
            "get",
            "post",
            "put",
            "delete",
            "patch",
            "head",
            "options",
            "trace",
        }
        method = next((m for m in path_item.keys() if m.lower() in valid_methods), None)

        if not method:
            raise ValueError("No valid HTTP method found in path specification")

        operation = path_item[method]
        headers, parameters = parse_openapi_parameters(operation, token, api_key)
        full_url = base_url.rstrip("/") + "/" + path.lstrip("/")

        return cls(
            url=full_url,
            method=method.upper(),
            headers=headers,
            parameters=parameters,
        )

    async def call(self, payload: dict | BaseModel) -> APIResponse:
        """
        Call the endpoint with the given payload.

        Args:
            payload: A Pydantic BaseModel or a dictionary containing the data to send

        Returns:
            APIResponse: A wrapped response containing status and payload
        """
        if isinstance(payload, BaseModel):
            payload = payload.model_dump()

        # Apply default values for missing required parameters
        for param_name, param in self.parameters.items():
            if param_name not in payload and param.default is not None:
                payload[param_name] = param.default
            elif param.required and param_name not in payload:
                raise ValueError(f"Required parameter '{param_name}' is missing")

        query_params = {}
        body_payload = {}
        headers = self.headers.copy()
        url = self.url

        for key, value in payload.items():
            param = self.parameters.get(key)
            if param is None:
                # Default to body if parameter not specified
                body_payload[key] = value
                continue

            if param.location == ParameterLocation.QUERY:
                query_params[key] = value
            elif param.location == ParameterLocation.BODY:
                body_payload[key] = value
            elif param.location == ParameterLocation.HEADER:
                headers[key] = value
            elif param.location == ParameterLocation.PATH:
                url = url.replace(f"{{{key}}}", str(value))

        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=self.method,
                    url=url,
                    params=query_params,
                    headers=headers,
                    json=body_payload if body_payload else None,
                    timeout=180.0,
                )

                # Check if the response status code indicates success
                if response.is_success:
                    return APIResponse(
                        status=APIResponseStatus.OK,
                        payload=response.json(),
                        status_code=response.status_code,
                    )
                else:
                    # Try to get error message from response, fall back to status text
                    error_data = response.json() if response.text else {}
                    error_message = (
                        error_data.get("message")
                        or error_data.get("error")
                        or f"HTTP {response.status_code}: {response.reason_phrase}"
                    )
                    return APIResponse(
                        status=APIResponseStatus.ERROR,
                        message=error_message,
                        status_code=response.status_code,
                    )

        except httpx.RequestError as e:
            error_str = f"{e.__class__.__name__}: {str(e)}"
            return APIResponse(
                status=APIResponseStatus.FAIL, message=f"Request failed: {error_str}"
            )
        except Exception as e:
            return APIResponse(
                status=APIResponseStatus.FAIL, message=f"Unexpected error: {str(e)}"
            )

    async def __call__(
        self, payload: dict | BaseModel | None = None, **kwargs
    ) -> APIResponse:
        """
        Callable interface for the endpoint. Combines payload dict and kwargs.

        Args:
            payload: Optional dict or BaseModel containing the initial payload
            **kwargs: Additional parameters to add to the payload
        """
        # Start with empty dict if no payload provided
        final_payload = {}

        # Add payload dict if provided
        if payload:
            if isinstance(payload, BaseModel):
                final_payload.update(payload.model_dump())
            else:
                final_payload.update(payload)

        # Add kwargs (kwargs take precedence over payload)
        final_payload.update(kwargs)

        return await self.call(final_payload)


WEBHOOK_PAYLOAD_STRING = "message"


class WebhookModel(EndpointModel):
    enabled: bool = True

    async def deliver(
        self, payload: BaseModel | dict, background: bool = False
    ) -> bool:
        """
        Asynchronously deliver a payload to the webhook endpoint.

        Args:
            payload: A Pydantic BaseModel or a dictionary containing the data to send
            background: If True, delivery happens in the background without waiting for completion

        Returns:
            bool: True if delivery was successful or started in background, False otherwise
        """
        if not self.enabled:
            return False

        if isinstance(payload, BaseModel):
            payload = payload.model_dump()

        if background:
            # Start delivery in background without awaiting the result
            async def _background_deliver():
                try:
                    await self.call({WEBHOOK_PAYLOAD_STRING: payload})
                    logger.info(f"Background webhook delivery succeeded to {self.url}")
                except Exception as e:
                    logger.exception(
                        f"Background webhook delivery failed to {self.url}"
                    )

            # Create the task but don't await it
            # We don't need to await create_task() itself, but we should keep a reference
            # to prevent garbage collection
            task = asyncio.create_task(_background_deliver())

            # Optional: Add a done callback to handle any exceptions
            def _handle_task_done(task):
                if task.exception():
                    logger.error(
                        f"Unhandled exception in background webhook task: {task.exception()}"
                    )

            task.add_done_callback(_handle_task_done)
            return True

        try:
            # Use the parent class's call method to properly handle parameters
            await self.call({WEBHOOK_PAYLOAD_STRING: payload})
            return True
        except Exception as e:
            logger.exception(f"Webhook delivery failed to {self.url}")
            return False


def parse_openapi_parameters(
    operation: dict,
    token: str = None,
    api_key: str = None,
) -> tuple[dict, dict]:
    """
    Parse OpenAPI operation parameters and security requirements into headers and parameters.

    Args:
        operation: The OpenAPI operation object
        token: Optional bearer token for authentication
        api_key: Optional API key for authentication

    Returns:
        tuple[dict, dict]: A tuple of (headers, parameters)
    """
    headers = {}
    parameters = {}

    # Extract security requirements
    if "security" in operation:
        for security_req in operation["security"]:
            if "bearerAuth" in security_req:
                assert token is not None, "Bearer token is required for this endpoint"
                headers["Authorization"] = f"Bearer {token}"
                parameters["Authorization"] = Parameter(
                    name="Authorization",
                    location=ParameterLocation.HEADER,
                    description="Bearer authentication token",
                    required=True,
                    schema_type="string",
                )
            elif "apiKey" in security_req:
                assert api_key is not None, "API key is required for this endpoint"
                headers["X-API-Key"] = api_key
                parameters["X-API-Key"] = Parameter(
                    name="X-API-Key",
                    location=ParameterLocation.HEADER,
                    description="API Key for authentication",
                    required=True,
                    schema_type="string",
                )

    # Parse regular parameters
    if "parameters" in operation:
        for param_dict in operation["parameters"]:
            param = Parameter.from_openapi(param_dict)
            parameters[param.name] = param

    # Parse request body parameters
    if "requestBody" in operation:
        content = operation["requestBody"].get("content", {})
        json_content = content.get("application/json", {})
        schema = json_content.get("schema", {})

        if schema.get("type") == "object":
            props = schema.get("properties", {})
            required_props = schema.get("required", [])

            for prop_name, prop_schema in props.items():
                parameters[prop_name] = Parameter(
                    name=prop_name,
                    location=ParameterLocation.BODY,
                    description=prop_schema.get("description"),
                    required=prop_name in required_props,
                    schema_type=prop_schema.get("type"),
                    schema=prop_schema,
                    default=prop_schema.get("default"),
                )

    return headers, parameters
