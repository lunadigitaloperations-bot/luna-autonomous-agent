import json
import os
import urllib.request
import urllib.error
from datetime import datetime


def ask_luna(prompt):
    api_key = os.environ["OPENAI_API_KEY"]

    request_data = {
        "model": "gpt-4o-mini",
        "input": prompt
    }

    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(request_data).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result.get("output_text", "")


def run_agent():
    prompt = """
    You are Luna's task-planning engine.

    Identify one legitimate digital service task
    that could be prepared for human review.

    Do not send messages, create accounts,
    make purchases, or perform external actions.
    """

    result = ask_luna(prompt)

    print(f"Agent time: {datetime.utcnow().isoformat()}")
    print("Luna response:")
    print(result)


if __name__ == "__main__":
    run_agent()
