from copy import copy
from dataclasses import asdict
import json
import os
import time
from typing import Any, Dict, List, Tuple, Union


from mloda_core.abstract_plugins.components.feature_set import FeatureSet
from mloda_plugins.feature_group.experimental.llm.llm_api.llm_base_request import LLMBaseApi
from mloda_plugins.feature_group.experimental.llm.llm_api.request_loop import RequestLoop
from mloda_plugins.feature_group.experimental.llm.tools.tool_collection import ToolCollection
from mloda_plugins.feature_group.experimental.llm.tools.tool_data_classes import ToolFunctionDeclaration

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import pandas as pd
except ImportError:
    pd = None


import logging

logger = logging.getLogger(__name__)


def python_type_to_openapi_type(python_type: str) -> str:
    """Converts Python type strings to OpenAPI/JSON Schema type strings."""
    type_mapping = {
        "float": "number",
        "int": "integer",
        "str": "string",
        "bool": "boolean",
        "number": "number",
    }
    return type_mapping.get(python_type, "string")  # Default to string if not found


def parse_tool_function_for_openai(function_declaration: ToolFunctionDeclaration) -> Dict[str, Any]:
    """Parses a ToolFunctionDeclaration into a dict formatted for OpenAI function calling.

    The output will have the following structure:
    {
        "type": "function",
        "function": {
            "name": <function name>,
            "description": <function description>,
            "parameters": {
                "type": "object",
                "properties": {
                    <param_name>: {
                        "type": <openai json schema type>,
                        "description": <param description>
                    },
                    ...
                },
                "required": [<list of required param names>],
                "additionalProperties": False
            },
            "strict": True
        }
    }
    """
    if not isinstance(function_declaration, ToolFunctionDeclaration):
        raise ValueError(f"Tool function {function_declaration} does not return a ToolFunctionDeclaration.")

    # Build the parameters schema.
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": function_declaration.required,
        "additionalProperties": False,
    }

    for param in function_declaration.parameters:
        param_dict = asdict(param)
        parameters_schema["properties"][param_dict["name"]] = {  # type: ignore
            "type": python_type_to_openapi_type(param_dict["type"]),
            "description": param_dict["description"],
        }

    # Construct the final tool structure.
    tool_dict = {
        "type": "function",
        "function": {
            "name": function_declaration.name,
            "description": function_declaration.description,
            "parameters": parameters_schema,
            "strict": True,
        },
    }

    return tool_dict


class OpenAIAPI(LLMBaseApi):
    @classmethod
    def request(
        cls,
        model: str,
        prompt: Union[str, List[Dict[str, str]]],
        model_parameters: Dict[str, Any],
        tools: ToolCollection | None,
    ) -> Any:
        if isinstance(prompt, str):
            raise ValueError("OpenAI requires a list of messages, not a single prompt.")

        try:
            openai_client = cls._setup_model_if_needed(model)
            if openai_client is not None:
                tools = cls.parse_tools(tools)  # type: ignore
                result = cls.generate_response(openai_client, model, prompt, tools)
                return result
        except Exception as e:
            logger.error(f"Error during OpenAI request: {e}")
            raise
        raise ValueError("OpenAI model is not set.")

    @classmethod
    def _setup_model_if_needed(cls, model: str) -> Any:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")

        client = OpenAI(api_key=api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        return client

    @classmethod
    def parse_tools(cls, tools: ToolCollection | None) -> List[Dict[str, Any]]:
        """Parses all tools in the ToolCollection for OpenAI."""
        parsed_tools: List[Dict[str, Any]] = []
        if tools is None:
            return parsed_tools
        for _, tool in tools.get_all_tools().items():
            parsed_tools.append(parse_tool_function_for_openai(tool))
        return parsed_tools

    @classmethod
    def handle_response(
        cls, response: Any, features: FeatureSet, tools: ToolCollection | None
    ) -> Tuple[List[Dict[str, str]], str]:
        responses = []
        used_tool = ""

        if hasattr(response, "choices") and response.choices:
            for choice in response.choices:
                message = choice.message

                if hasattr(message, "content") and message.content:
                    responses.append({"text": message.content})

                if message.tool_calls:  # Check for function call
                    if tools is None:
                        raise ValueError("Tools are not set.")

                    new_tools = []
                    for e in message.tool_calls:
                        tool_dict = {"name": e.function.name, "args": json.loads(e.function.arguments)}
                        new_tools.append(tool_dict)

                    tool_result = cls._execute_tools(new_tools, features, tools)
                    if tool_result:
                        responses.append({"tool": tool_result})
                        used_tool += tool_result

        else:
            logger.warning(f"Response has no text or choices attribute: {response}")
            return [], ""

        return responses, used_tool

    def generate_response(
        client: Any,
        model: str,
        messages: List[Dict[str, str]],
        tools: Any,
        max_retries: int = 5,
        initial_retry_delay: int = 10,
        max_retry_delay: int = 60,
    ) -> Any:
        """
        Generates content from OpenAI with retry logic for rate limits.
        """
        # Override defaults with environment variables if present
        max_retries = int(os.environ.get("OPENAI_MAX_RETRIES", str(max_retries)))
        initial_retry_delay = int(os.environ.get("OPENAI_INITIAL_RETRY_DELAY", str(initial_retry_delay)))
        max_retry_delay = int(os.environ.get("OPENAI_MAX_RETRY_DELAY", str(max_retry_delay)))

        retry_attempt = 0
        while retry_attempt <= max_retries:
            try:
                result = client.chat.completions.create(model=model, messages=messages, tools=tools)
                return result
            except Exception as e:
                # Check for an OpenAI rate limit error; adjust the error check as needed
                is_rate_limit_error = False
                if e.code == 429:  # type: ignore
                    is_rate_limit_error = True

                if is_rate_limit_error:
                    retry_attempt += 1
                    if retry_attempt > max_retries:
                        print(f"Maximum retries ({max_retries}) reached for OPENAI. Raising exception.")
                        raise
                    delay = min(initial_retry_delay * (2 ** (retry_attempt - 1)), max_retry_delay)
                    print(
                        f"Rate limit hit for OPENAI. Retrying in {delay:.2f} seconds (Attempt {retry_attempt}/{max_retries})."
                    )
                    time.sleep(delay)
                else:
                    print(f"An unexpected error occurred during OPENAI request: {e}")
                    raise

        raise Exception(f"Maximum retries ({max_retries}) reached for OPENAI without a successful response.")


class OpenAIRequestLoop(RequestLoop):
    @classmethod
    def api(cls) -> Any:
        return OpenAIAPI

    @classmethod
    def initial_prompt_message(cls, messages: Any, initial_prompt: str) -> Tuple[Any, Any]:
        if not messages:
            messages = [{"role": "user", "content": initial_prompt}]
            _messages = copy(messages)
        else:
            _messages = copy(messages)
            _messages.append({"role": "user", "content": cls.add_final_part_of_prompt()})

        return messages, _messages

    @classmethod
    def add_tool_response_to_messages(cls, messages: Any, response: str) -> Any:
        messages.append({"role": "user", "content": response})
        return messages

    @classmethod
    def add_text_response_to_messages(cls, messages: Any, response: str) -> Any:
        messages.append({"role": "assistant", "content": response})
        return messages
