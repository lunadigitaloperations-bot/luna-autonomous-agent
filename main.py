
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path


# ============================================================
# INFINITE SAUCE — LUNA BUSINESS OPERATING SYSTEM
# ============================================================

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
BUSINESS_NAME = "Infinite Sauce"
BUSINESS_EMAIL = "luna.digital.operations@gmail.com"
BUSINESS_WHATSAPP = "+14735341956"
BUSINESS_CURRENCY = "USD"

BASE_DIR = Path(__file__).resolve().parent

TASKS_FILE = BASE_DIR / "tasks.json"
LEADS_FILE = BASE_DIR / "leads.json"
OUTREACH_FILE = BASE_DIR / "outreach_queue.json"
CLIENTS_FILE = BASE_DIR / "clients.json"
ANALYTICS_FILE = BASE_DIR / "analytics.json"
CONFIG_FILE = BASE_DIR / "config.json"


# ============================================================
# GENERAL UTILITIES
# ============================================================

def utc_now():
    return datetime.now(timezone.utc)


def timestamp():
    return utc_now().isoformat()


def make_id(prefix):
    return f"{prefix}-{int(utc_now().timestamp() * 1000)}"


def load_json(path, default):
    try:
        if not path.exists():
            return default

        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    except (OSError, json.JSONDecodeError):
        return default


def save_json(path, data):
    temporary_path = Path(str(path) + ".tmp")

    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    temporary_path.replace(path)


def ensure_files():
    defaults = {
        TASKS_FILE: {
            "tasks": [],
            "completed": []
        },
        LEADS_FILE: {
            "instructions": [
                "Only use public or permission-based prospect information.",
                "Do not store sensitive personal information.",
                "Record opt-outs immediately.",
                "Review all outreach before sending."
            ],
            "leads": []
        },
        OUTREACH_FILE: {
            "queue": []
        },
        CLIENTS_FILE: {
            "clients": []
        },
        ANALYTICS_FILE: {
            "events": []
        }
    }

    for path, default in defaults.items():
        if not path.exists():
            save_json(path, default)


def record_event(event_type, details=None):
    analytics = load_json(
        ANALYTICS_FILE,
        {"events": []}
    )

    analytics.setdefault("events", [])

    analytics["events"].append({
        "id": make_id("event"),
        "created_at": timestamp(),
        "type": event_type,
        "details": details or {}
    })

    save_json(ANALYTICS_FILE, analytics)


# ============================================================
# OPENAI CONNECTION
# ============================================================

def ask_luna(prompt, temperature=None):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing from the environment."
        )

    request_data = {
        "model": MODEL,
        "input": prompt
    }

    if temperature is not None:
        request_data["temperature"] = temperature

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
        with urllib.request.urlopen(request, timeout=90) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as error:
        error_body = error.read().decode(
            "utf-8",
            errors="replace"
        )

        raise RuntimeError(
            f"OpenAI API error: {error_body}"
        ) from error

    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Network error while contacting OpenAI: {error}"
        ) from error

    if result.get("output_text"):
        return result["output_text"].strip()

    text_parts = []

    for output_item in result.get("output", []):
        for content_item in output_item.get("content", []):
            if content_item.get("type") == "output_text":
                text_parts.append(
                    content_item.get("text", "")
                )

    response_text = "\n".join(text_parts).strip()

    if not response_text:
        raise RuntimeError(
            "The AI returned an empty response."
        )

    return response_text


def clean_json_response(response_text):
    response_text = response_text.strip()

    if response_text.startswith("```"):
        lines = response_text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        response_text = "\n".join(lines).strip()

    start = response_text.find("{")
    end = response_text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "No JSON object was found in the AI response."
        )

    json_text = response_text[start:end + 1]

    return json.loads(json_text)


def ask_for_json(prompt):
    response = ask_luna(prompt)
    return clean_json_response(response)


# ============================================================
# BUSINESS OFFER ENGINE
# ============================================================

def generate_offer():
    prompt = f"""
You are Luna, the business strategy engine for {BUSINESS_NAME}.

Business contact:
Email: {BUSINESS_EMAIL}
WhatsApp: {BUSINESS_WHATSAPP}

Skills available:
- Short-form video scripts
- TikTok content
- Instagram Reels
- YouTube Shorts
- Captions
- Content strategy
- Digital products
- Remote creative services

Create one realistic service offer for a small business or creator.

The offer must:
- Solve a specific problem.
- Have clear deliverables.
- Be deliverable remotely.
- Have a reasonable price.
- Be possible for one person to fulfill.
- Avoid guaranteed results.
- Avoid regulated financial advice.

Return ONLY valid JSON:

{{
  "title": "",
  "target_customer": "",
  "customer_problem": "",
  "solution": "",
  "deliverables": [],
  "suggested_price_usd": 0,
  "estimated_delivery_days": 0,
  "value_proposition": "",
  "sales_angle": "",
  "organic_discovery_methods": [],
  "qualification_criteria": [],
  "next_action": ""
}}
"""

    offer = ask_for_json(prompt)

    required_fields = [
        "title",
        "target_customer",
        "customer_problem",
        "solution",
        "deliverables",
        "suggested_price_usd",
        "estimated_delivery_days"
    ]

    for field in required_fields:
        offer.setdefault(field, "")

    return offer


# ============================================================
# SALES ASSET ENGINE
# ============================================================

def generate_sales_assets(offer):
    prompt = f"""
You are Luna, the sales content engine for {BUSINESS_NAME}.

Create reviewable sales assets based on this offer:

{json.dumps(offer, indent=2)}

Generate:
1. A social media post.
2. A short website sales description.
3. A respectful outreach template.
4. Five discovery questions.
5. A proposal outline.
6. A concise call to action.
7. A payment conversation template that does not claim
   payment has been received.

Rules:
- Do not send anything.
- Do not use spam.
- Do not impersonate people.
- Do not make guaranteed claims.
- Do not claim a prospect is interested.
- Include a respectful opt-out sentence.
- Require human approval before outreach.

Return ONLY valid JSON:

{{
  "social_post": "",
  "website_description": "",
  "outreach_template": "",
  "discovery_questions": [],
  "proposal_outline": [],
  "call_to_action": "",
  "payment_template": "",
  "requires_human_approval": true
}}
"""

    return ask_for_json(prompt)


# ============================================================
# LEAD QUALIFICATION ENGINE
# ============================================================

def normalize_lead(lead):
    return {
        "id": lead.get("id") or make_id("lead"),
        "created_at": lead.get("created_at") or timestamp(),
        "name": str(lead.get("name", "")).strip(),
        "business": str(lead.get("business", "")).strip(),
        "contact": str(lead.get("contact", "")).strip(),
        "website": str(lead.get("website", "")).strip(),
        "platform": str(lead.get("platform", "")).strip(),
        "notes": str(lead.get("notes", "")).strip(),
        "consent_status": str(
            lead.get("consent_status", "unknown")
        ).lower(),
        "status": str(
            lead.get("status", "new")
        ).lower(),
        "last_contacted_at": lead.get("last_contacted_at"),
        "next_follow_up_at": lead.get("next_follow_up_at"),
        "opted_out": bool(lead.get("opted_out", False))
    }


def qualify_lead(lead, offer):
    prompt = f"""
You are a careful lead qualification assistant.

Offer:
{json.dumps(offer, indent=2)}

Lead information:
{json.dumps(lead, indent=2)}

Assess whether this lead appears relevant based ONLY on
the information provided.

Do not invent facts.
Do not infer private information.
Do not assume the person wants to buy.
Do not recommend contact if the person opted out.
A consent status of "unknown" means human review is required.

Return ONLY valid JSON:

{{
  "fit": "high|medium|low|unknown",
  "reason": "",
  "possible_need": "",
  "recommended_next_step": "",
  "outreach_allowed": false,
  "requires_human_review": true
}}
"""

    result = ask_for_json(prompt)

    if lead.get("opted_out"):
        result["outreach_allowed"] = False
        result["reason"] = "Lead has opted out."

    if lead.get("consent_status") != "confirmed":
        result["requires_human_review"] = True

    return result


# ============================================================
# PERSONALIZED PROPOSAL ENGINE
# ============================================================

def generate_proposal(lead, offer, qualification):
    prompt = f"""
You are Luna, preparing a draft proposal for human review.

Business:
{BUSINESS_NAME}

Offer:
{json.dumps(offer, indent=2)}

Lead:
{json.dumps(lead, indent=2)}

Qualification:
{json.dumps(qualification, indent=2)}

Create a short, honest proposal.

Rules:
- Do not claim the lead requested a proposal.
- Do not claim to know unverified business details.
- Do not promise views, sales, followers, or income.
- Do not send the proposal.
- Include a clear deliverables section.
- Include price and estimated delivery.
- Include a request for confirmation.
- Keep it professional and natural.

Return ONLY valid JSON:

{{
  "subject": "",
  "opening": "",
  "identified_need": "",
  "proposed_solution": "",
  "deliverables": [],
  "price": 0,
  "delivery_days": 0,
  "next_step": "",
  "draft_status": "pending_human_approval"
}}
"""

    return ask_for_json(prompt)


# ============================================================
# FOLLOW-UP ENGINE
# ============================================================

def parse_date(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        return None


def follow_up_is_due(lead):
    if lead.get("opted_out"):
        return False

    if lead.get("status") in [
        "closed",
        "lost",
        "opted_out"
    ]:
        return False

    next_follow_up = parse_date(
        lead.get("next_follow_up_at")
    )

    if not next_follow_up:
        return False

    return next_follow_up <= utc_now()


def generate_follow_up(lead, offer):
    prompt = f"""
Create a short follow-up message draft for human review.

Business offer:
{json.dumps(offer, indent=2)}

Lead:
{json.dumps(lead, indent=2)}

Rules:
- Do not send the message.
- Do not pressure the recipient.
- Do not use deceptive urgency.
- Do not claim the recipient showed interest.
- Include an easy way to decline further contact.
- Keep it under 100 words.

Return ONLY valid JSON:

{{
  "message": "",
  "requires_human_approval": true,
  "do_not_send_automatically": true
}}
"""

    return ask_for_json(prompt)


# ============================================================
# DELIVERY ENGINE
# ============================================================

def create_delivery_plan(offer, client_details):
    prompt = f"""
Create a practical delivery plan for a confirmed paying client.

Offer:
{json.dumps(offer, indent=2)}

Client details:
{json.dumps(client_details, indent=2)}

Return ONLY valid JSON:

{{
  "project_title": "",
  "milestones": [
    {{
      "name": "",
      "description": "",
      "deadline_days_after_start": 0
    }}
  ],
  "client_inputs_required": [],
  "quality_checklist": [],
  "completion_message": ""
}}

Do not claim that payment was received.
Do not begin work unless payment and client approval
have been verified by a human or trusted payment integration.
"""

    return ask_for_json(prompt)


# ============================================================
# TASK PROCESSING
# ============================================================

def create_daily_business_task():
    offer = generate_offer()
    sales_assets = generate_sales_assets(offer)

    task = {
        "id": make_id("task"),
        "created_at": timestamp(),
        "type": "business_growth",
        "status": "pending_human_review",
        "offer": offer,
        "sales_assets": sales_assets
    }

    tasks = load_json(
        TASKS_FILE,
        {"tasks": [], "completed": []}
    )

    tasks.setdefault("tasks", [])
    tasks.setdefault("completed", [])
    tasks["tasks"].append(task)

    save_json(TASKS_FILE, tasks)

    record_event(
        "offer_created",
        {"task_id": task["id"]}
    )

    return task


def process_leads(offer):
    lead_data = load_json(
        LEADS_FILE,
        {"leads": []}
    )

    leads = lead_data.get("leads", [])
    outreach = load_json(
        OUTREACH_FILE,
        {"queue": []}
    )

    outreach.setdefault("queue", [])

    processed = []

    for raw_lead in leads:
        lead = normalize_lead(raw_lead)

        if lead["opted_out"]:
            continue

        if lead["status"] in [
            "closed",
            "lost",
            "opted_out"
        ]:
            continue

        qualification = qualify_lead(lead, offer)

        record = {
            "id": make_id("review"),
            "created_at": timestamp(),
            "lead_id": lead["id"],
            "lead": lead,
            "qualification": qualification,
            "status": "pending_human_review"
        }

        if qualification.get("fit") in ["high", "medium"]:
            proposal = generate_proposal(
                lead,
                offer,
                qualification
            )

            record["proposal"] = proposal

        if follow_up_is_due(lead):
            record["follow_up"] = generate_follow_up(
                lead,
                offer
            )

        outreach["queue"].append(record)
        processed.append(record)

        record_event(
            "lead_processed",
            {
                "lead_id": lead["id"],
                "qualification": qualification.get("fit")
            }
        )

    save_json(OUTREACH_FILE, outreach)

    return processed


def create_delivery_plans():
    clients_data = load_json(
        CLIENTS_FILE,
        {"clients": []}
    )

    tasks = load_json(
        TASKS_FILE,
        {"tasks": [], "completed": []}
    )

    plans_created = []

    for client in clients_data.get("clients", []):
        if client.get("status") != "paid":
            continue

        if client.get("delivery_plan"):
            continue

        offer = client.get("offer", {})
        delivery_plan = create_delivery_plan(
            offer,
            client
        )

        client["delivery_plan"] = delivery_plan
        client["delivery_plan_created_at"] = timestamp()
        client["status"] = "delivery_planned"

        plans_created.append(client.get("id"))

    save_json(CLIENTS_FILE, clients_data)

    if plans_created:
        record_event(
            "delivery_plans_created",
            {"client_ids": plans_created}
        )

    return plans_created


# ============================================================
# BUSINESS ANALYTICS
# ============================================================

def generate_analytics_report():
    leads_data = load_json(
        LEADS_FILE,
        {"leads": []}
    )

    clients_data = load_json(
        CLIENTS_FILE,
        {"clients": []}
    )

    tasks_data = load_json(
        TASKS_FILE,
        {"tasks": [], "completed": []}
    )

    leads = leads_data.get("leads", [])
    clients = clients_data.get("clients", [])
    tasks = tasks_data.get("tasks", [])

    paid_clients = [
        client for client in clients
        if client.get("status") in [
            "paid",
            "delivery_planned",
            "in_progress",
            "completed"
        ]
    ]

    total_revenue = 0

    for client in paid_clients:
        try:
            total_revenue += float(
                client.get("amount_paid", 0)
            )
        except (TypeError, ValueError):
            continue

    report = {
        "generated_at": timestamp(),
        "total_leads": len(leads),
        "total_tasks": len(tasks),
        "total_clients": len(clients),
        "paid_clients": len(paid_clients),
        "recorded_revenue_usd": round(total_revenue, 2),
        "lead_statuses": {},
        "client_statuses": {}
    }

    for lead in leads:
        status = lead.get("status", "unknown")
        report["lead_statuses"][status] = (
            report["lead_statuses"].get(status, 0) + 1
        )

    for client in clients:
        status = client.get("status", "unknown")
        report["client_statuses"][status] = (
            report["client_statuses"].get(status, 0) + 1
        )

    save_json(
        ANALYTICS_FILE,
        {
            "latest_report": report,
            "events": load_json(
                ANALYTICS_FILE,
                {"events": []}
            ).get("events", [])
        }
    )

    return report


# ============================================================
# MAIN ORCHESTRATOR
# ============================================================

def run_agent():
    print("Starting Luna Business Operating System...")
    ensure_files()

    print("1. Creating business opportunity...")
    task = create_daily_business_task()

    offer = task.get("offer", {})

    print("2. Processing available leads...")
    processed_leads = process_leads(offer)

    print("3. Creating delivery plans for verified paid clients...")
    delivery_plans = create_delivery_plans()

    print("4. Generating analytics...")
    report = generate_analytics_report()

    print("\nLUNA RUN COMPLETED")
    print("=" * 50)
    print(f"Offer: {offer.get('title', 'N/A')}")
    print(f"Lead reviews created: {len(processed_leads)}")
    print(f"Delivery plans created: {len(delivery_plans)}")
    print(
        f"Recorded revenue: "
        f"${report.get('recorded_revenue_usd', 0):.2f}"
    )
    print("All outbound communication remains pending review.")
    print("No payment status is assumed.")
    print("=" * 50)


if __name__ == "__main__":
    try:
        run_agent()
    except Exception as error:
        record_event(
            "agent_error",
            {"error": str(error)}
        )
        print(f"Agent failed safely: {error}")
        raise
