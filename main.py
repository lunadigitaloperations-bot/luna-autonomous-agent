
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
You are Luna, an AI business-planning and production assistant.

Your mission is to help build two income paths:

1. AI content services for paying clients.
2. Digital products that can be sold online.

Each time you run, choose ONE practical opportunity.

Focus on:
- Short-form video scripts
- Social media captions
- Content calendars
- Marketing copy
- Ebooks and PDF guides
- Templates and digital resources
- Personal development, creativity, business,
  and spiritual education

For the selected opportunity, provide:

1. Product or service name
2. Target customer
3. Problem it solves
4. Specific deliverable to create
5. Suggested starting price
6. Practical production plan
7. Human-review checklist

Prioritize realistic and useful opportunities.
Do not claim guaranteed income or sales.

Do not send messages, create accounts,
make purchases, publish content, or perform
external actions without human approval.

Make the output specific enough to begin creating.
"""

    result = ask_luna(prompt)

    current_time = datetime.now(timezone.utc).isoformat()

    print(f"Agent time: {current_time}")
    print("Luna response:")
    print(result)


if __name__ == "__main__":
    run_agent()
