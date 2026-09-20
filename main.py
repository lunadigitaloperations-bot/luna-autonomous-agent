
import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone


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

    try:
        with urllib.request.urlopen(request) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

        if result.get("output_text"):
            return result["output_text"]

        for item in result.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    return content.get("text", "")

        return json.dumps(result)

    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8")
        return f"API error {error.code}: {error_body}"


def run_agent():
    prompt = """
You are Luna's task-planning engine.

Identify one legitimate digital service task
that could be prepared for human review.

Explain:
1. The task
2. Who might pay for it
3. What needs to be prepared

Do not send messages, create accounts,
make purchases, or perform external actions.
"""

    result = ask_luna(prompt)

    current_time = datetime.now(timezone.utc).isoformat()

    print(f"Agent time: {current_time}")
    print("Luna response:")
    print(result)


if __name__ == "__main__":
    run_agent()
