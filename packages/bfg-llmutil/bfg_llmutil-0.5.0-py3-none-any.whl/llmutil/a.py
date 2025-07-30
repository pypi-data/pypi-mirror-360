import json

from openai import NOT_GIVEN, NotGiven, OpenAI
from openai.types.responses import (
    ResponseOutputItem,
    ResponseTextConfigParam,
    FunctionToolParam,
    FileSearchToolParam,
    ResponseFunctionToolCallParam,
)
from openai.types.responses.response_input_param import FunctionCallOutput
from schemautil import object_schema

_client = None


def get_client():
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def build_tools(
    tools: dict | None, memory: str | None
) -> list[FunctionToolParam | FileSearchToolParam]:
    output = []
    if tools:
        output.extend(
            [
                {
                    "type": "function",
                    "name": name,
                    "parameters": object_schema(params),
                    "strict": True,
                }
                for name, params in tools.items()
            ]
        )
    if memory:
        output.append(
            {
                "type": "file_search",
                "vector_store_ids": [memory],
            }
        )
    return output


def build_text(schema: dict | None) -> ResponseTextConfigParam | NotGiven:
    if not schema:
        return NOT_GIVEN
    return {
        "format": {
            "type": "json_schema",
            "name": "output",
            "schema": object_schema(schema),
            "strict": True,
        }
    }


def format_output(output: list[ResponseOutputItem], *, has_schema: bool) -> dict:
    """Format the output list into a single message.

    Expects the output list to contain zero, one, or more text messages followed by
    at most one function call. If both text and function call are present, returns
    the function call. Otherwise, returns a combined text message."""
    text_output = []
    for i, item in enumerate(output):
        if item.type == "function_call":
            assert i == len(output) - 1, "function call must be the last output"
            return {
                "type": "function_call",
                "name": item.name,
                "args": json.loads(item.arguments),
            }
        elif item.type == "message":
            text = item.content[0].text
            assert isinstance(text, str) and len(text) > 0, text
            text_output.append(text)
        else:
            raise ValueError(f"Unexpected output type: {item.type}")

    if has_schema:
        assert len(text_output) == 1
        content = json.loads(text_output[0])
    else:
        content = "\n".join(text_output)

    return {
        "type": "message",
        "content": content,
    }


def build_function_call_messages(
    *function_calls,
) -> list[ResponseFunctionToolCallParam | FunctionCallOutput]:
    call_id = 0
    output = []
    for c in function_calls:
        output.append(
            {
                "type": "function_call",
                "name": c["name"],
                "arguments": json.dumps(c["args"]),
                "call_id": str(call_id),
            }
        )
        output.append(
            {
                "type": "function_call_output",
                "call_id": str(call_id),
                "output": c["result"]
                if isinstance(c["result"], str)
                else json.dumps(c["result"]),
            }
        )
        call_id += 1
    return output


def new_response(
    messages, *, model, tools=None, schema=None, memory=None, timeout=30
) -> dict:
    res = get_client().responses.create(
        model=model,
        input=messages,
        tools=build_tools(tools, memory),
        parallel_tool_calls=False,
        text=build_text(schema),
        timeout=timeout,
        user="llmutil",  # improve cache hit rates
        store=False,
    )
    return format_output(res.output, has_schema=bool(schema))
