from llmutil import new_response, build_function_call_messages


def add(a, b):
    return a + b


tools = {
    "add": {
        "a": "number",
        "b": "number",
    }
}

messages = [
    {
        "role": "system",
        "content": "you cannot do math. you must use the add() function to add numbers.",
    },
    {
        "role": "user",
        "content": "alice has 10 apples, bob has 20 apples, how many apples do they have in total?",
    },
]

output = new_response(messages, model="gpt-4.1-mini", tools=tools)

# {'type': 'function_call', 'name': 'add', 'args': {'a': 10, 'b': 20}}
print(output)

output["result"] = 30
output = new_response(
    messages + build_function_call_messages(output),
    model="gpt-4.1-mini",
    tools=tools,
)

# {'type': 'message', 'content': 'Alice and Bob have 30 apples in total.'}
print(output)
