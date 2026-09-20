
import json
import os
import urllib.request
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

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode("utf-8"))

    # Read the convenient output_text field when available
    if result.get("output_text"):
        return result["output_text"]

    # Fallback: extract text from the response structure
    text_parts = []

    for output_item in result.get("output", []):
        for content_item in output_item.get("content", []):
            if content_item.get("type") == "output_text":
                text_parts.append(content_item.get("text", ""))

    return "\n".join(text_parts)


def clean_json_response(response_text):
    response_text = response_text.strip()

    if response_text.startswith("```"):
        lines = response_text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        response_text = "\n".join(lines)

    return json.loads(response_text)


def run_agent():
    prompt = """
You are Luna, a digital business-planning assistant.

Create ONE realistic digital service opportunity that could be
prepared for human review.

Do not contact anyone.
Do not send messages.
Do not create accounts.
Do not make purchases.
Do not promise guaranteed income.

Return ONLY valid JSON using exactly these fields:

{
  "title": "",
  "target_customer": "",
  "customer_problem": "",
  "proposed_solution": "",
  "suggested_price_usd": 0,
  "estimated_delivery_days": 0,
  "next_action": "",
  "requires_human_approval": true
}
"""

    response_text = ask_luna(prompt)
    opportunity = clean_json_response(response_text)

    task_record = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending_human_review",
        "opportunity": opportunity
    }

    with open("tasks.json", "w", encoding="utf-8") as file:
        json.dump(
            {
                "tasks": [task_record],
                "completed": []
            },
            file,
            indent=2
        )

    print("Agent completed successfully.")
    print("Structured opportunity saved to tasks.json:")
    print(json.dumps(task_record, indent=2))


if __name__ == "__main__":
    run_agent()
