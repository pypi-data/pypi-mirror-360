from llmutil import Result, Tooling, new_response


def add(a, b):
    return a + b


class UseAdd(Tooling):
    def on_function_call(self, name, args):
        if name == "add":
            return Result(add(args["a"], args["b"]))

    def get_tools(self):
        return {
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

output = new_response(messages, model="gpt-4.1-mini", tooling=UseAdd())

# Alice and Bob have 30 apples in total.
print(output)
