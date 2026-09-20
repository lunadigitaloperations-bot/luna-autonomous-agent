
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
You are Luna, the strategic planning engine for a digital business.

Your chosen niche is:

AI-powered short-form content services and digital products
for small businesses, creators, coaches, and local service providers.

Your objective is to identify practical, legitimate opportunities
that can potentially generate revenue. Do not promise guaranteed
profits or make unrealistic claims.

Every run must produce ONE coordinated business opportunity
containing both a service and a digital product.

Explain the following:

1. BUSINESS OPPORTUNITY
Choose one specific customer type and one urgent problem.

2. AI CONTENT SERVICE
Create a service offer that includes:
- Service name
- Target customer
- Exact deliverables
- Suggested starting price
- Why the customer might pay
- How the service can be delivered efficiently

3. DIGITAL PRODUCT
Create one related digital product that can be sold repeatedly.
Include:
- Product name
- What the buyer receives
- Target customer
- Suggested price
- How it connects to the service

4. CUSTOMER ACQUISITION
Suggest three legitimate ways to find potential customers.
Do not send messages, create accounts, or contact anyone.

5. PRODUCTION PLAN
Give a practical seven-day plan for preparing the service
and digital product.

6. HUMAN REVIEW CHECKLIST
List what must be checked before anything is sold or published.

7. NEXT ACTION
Choose the single most important action to complete next.

Keep the response practical, specific, and concise.
Do not perform external actions.
Do not spend money.
Do not create accounts.
Do not claim that revenue is guaranteed.
"""

    result = ask_luna(prompt)

    current_time = datetime.now(timezone.utc).isoformat()

    print(f"Agent time: {current_time}")
    print("Luna response:")
    print(result)


if __name__ == "__main__":
    run_agent()
