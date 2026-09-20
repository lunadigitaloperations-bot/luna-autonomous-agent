
import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone


BUSINESS_STRATEGY = """
We are building a digital business focused on LOCAL HOME-SERVICE BUSINESSES.

Target customers:
- Plumbers
- Electricians
- Cleaning companies
- Landscapers
- Handymen
- Small contractors

Our business has TWO revenue streams:

1. AI CONTENT SERVICES
We create social media posts, short-form video scripts,
captions, content calendars, promotional ideas, and blog content.

2. DIGITAL PRODUCTS
We sell reusable content templates, caption packs,
marketing checklists, promotional calendars, and simple
guides that help local businesses attract customers.

Choose practical offers that can realistically be created,
reviewed, marketed, and delivered by a small business.
Do not promise guaranteed sales, guaranteed growth, or guaranteed profit.
"""


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
            result = json.loads(response.read().decode("utf-8"))

        # Read the convenient output_text field if available.
        if result.get("output_text"):
            return result["output_text"]

        # Fallback: extract text from the response structure.
        text_parts = []

        for output_item in result.get("output", []):
            for content_item in output_item.get("content", []):
                if content_item.get("type") == "output_text":
                    text_parts.append(content_item.get("text", ""))

        return "\n".join(text_parts).strip()

    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8")
        return f"API error {error.code}: {error_body}"

    except Exception as error:
        return f"Unexpected error: {error}"


def run_agent():
    prompt = f"""
You are Luna, the strategic planning engine for a small digital business.

{BUSINESS_STRATEGY}

Create ONE practical business opportunity for today.

Your response must contain these sections:

### 1. AI CONTENT SERVICE
- Service name
- Exact target customer
- Customer problem
- What the customer receives
- Suggested starting price
- How long delivery should take
- Why the customer might pay for it

### 2. DIGITAL PRODUCT
- Product name
- Exact buyer
- Problem it solves
- Everything included in the product
- Suggested price
- How it connects to the AI content service

### 3. PRODUCTION PLAN
Give a simple 7-day plan for creating the service
and digital product.

### 4. SAMPLE DELIVERABLE
Create one example:
- One short-form video hook
- One 30-second video script
- One social media caption
- One digital product template idea

### 5. CUSTOMER ACQUISITION
Give three ethical ways to find potential customers.
Do not send messages or contact anyone.

### 6. HUMAN REVIEW CHECKLIST
List what I must check before selling or delivering anything.

### 7. NEXT ACTION
Give me exactly ONE action to complete next.

Do not create accounts, make purchases, send messages,
or perform external actions. Your role is to prepare
a realistic business plan and usable draft materials.
"""

    result = ask_luna(prompt)

    current_time = datetime.now(timezone.utc).isoformat()

    print(f"Agent time: {current_time}")
    print("Luna response:")
    print(result)


if __name__ == "__main__":
    run_agent()
