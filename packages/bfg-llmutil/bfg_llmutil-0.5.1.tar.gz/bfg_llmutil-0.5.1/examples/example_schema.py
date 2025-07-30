from llmutil import new_response

output = new_response(
    [
        {
            "role": "user",
            "content": "normalize this address: 1 hacker way, menlo park, california",
        }
    ],
    model="gpt-4.1-mini",
    schema={
        "street": "string",
        "city": "string",
        "state": "string",
    },
)

# {'street': '1 Hacker Way', 'city': 'Menlo Park', 'state': 'CA'}
print(output)
