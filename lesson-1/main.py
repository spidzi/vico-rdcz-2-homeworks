import argparse
import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


def add_numbers(a: float, b: float) -> dict[str, Any]:
    return {"operation": "add", "a": a, "b": b, "result": a + b}


def multiply_numbers(a: float, b: float) -> dict[str, Any]:
    return {"operation": "multiply", "a": a, "b": b, "result": a * b}


def build_tools() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "add_numbers",
                "description": "Add two numbers and return the result.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "First number."},
                        "b": {"type": "number", "description": "Second number."},
                    },
                    "required": ["a", "b"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "multiply_numbers",
                "description": "Multiply two numbers and return the result.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "First number."},
                        "b": {"type": "number", "description": "Second number."},
                    },
                    "required": ["a", "b"],
                },
            },
        },
    ]


def run(prompt: str, model: str) -> str:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to your environment or .env file.")

    client = OpenAI(api_key=api_key)
    tools = build_tools()

    available_functions = {
        "add_numbers": add_numbers,
        "multiply_numbers": multiply_numbers,
    }

    messages: list[dict[str, Any]] = [
        {
            "role": "developer",
            "content": (
                "You are a concise assistant. "
                "Use math tools when a calculation is required."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    first_response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    assistant_message = first_response.choices[0].message

    if not assistant_message.tool_calls:
        return assistant_message.content or "No content returned."

    messages.append(
        {
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in assistant_message.tool_calls
            ],
        }
    )

    for tool_call in assistant_message.tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions.get(function_name)
        if function_to_call is None:
            tool_output = {"error": f"Unknown function: {function_name}"}
        else:
            try:
                function_args = json.loads(tool_call.function.arguments)
                tool_output = function_to_call(**function_args)
            except json.JSONDecodeError as error:
                tool_output = {"error": f"Invalid JSON arguments: {error}"}
            except TypeError as error:
                tool_output = {"error": f"Invalid function arguments: {error}"}

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": json.dumps(tool_output),
            }
        )

    second_response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    return second_response.choices[0].message.content or "No content returned."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lesson 1 homework: Chat Completions + tool calling")
    parser.add_argument(
        "--prompt",
        default="What is 17.5 multiplied by 4, then add 2?",
        help="Question for the assistant.",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI chat model name.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    answer = run(prompt=args.prompt, model=args.model)

    print("--- Final Answer ---")
    print(answer)


if __name__ == "__main__":
    main()
