import json
from typing import Protocol

from openai import NOT_GIVEN, NotGiven, OpenAI
from openai.types.responses import (
    FileSearchToolParam,
    FunctionToolParam,
    ResponseOutputItem,
    ResponseTextConfigParam,
)
from schemautil import object_schema


class Result:
    def __init__(self, result):
        self.result = result


class Tooling(Protocol):
    def on_function_call(self, name: str, args: dict): ...
    def get_tools(self): ...


_client = None


def get_client():
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def build_tools(
    tooling: Tooling | None, memory: str | None
) -> list[FunctionToolParam | FileSearchToolParam]:
    tools = []
    if tooling:
        for name, params in tooling.get_tools().items():
            tools.append(
                {
                    "type": "function",
                    "name": name,
                    "parameters": object_schema(params),
                    "strict": True,
                }
            )
    if memory:
        tools.append(
            {
                "type": "file_search",
                "vector_store_ids": [memory],
            }
        )
    return tools


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


def format_output(output: list[ResponseOutputItem], *, has_schema: bool):
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


def new_response(
    messages, *, model, tooling=None, schema=None, memory=None, timeout=30
) -> dict:
    extra = []
    while True:
        res = get_client().responses.create(
            model=model,
            input=messages + extra,
            tools=build_tools(tooling, memory),
            parallel_tool_calls=False,
            text=build_text(schema),
            timeout=timeout,
            user="llmutil",  # improve cache hit rates
            store=False,
        )
        match format_output(res.output, has_schema=bool(schema)):
            case {"type": "function_call", "name": name, "args": args}:
                ret = tooling.on_function_call(name, args)
                if not isinstance(ret, Result):
                    return ret

                call_id = str(len(extra))
                extra.append(
                    {
                        "type": "function_call",
                        "call_id": call_id,
                        "name": name,
                        "arguments": json.dumps(args),
                    }
                )
                extra.append(
                    {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": ret.result
                        if isinstance(ret.result, str)
                        else json.dumps(ret.result),
                    }
                )
            case {"type": "message", "content": content}:
                return content
            case _:
                assert False
