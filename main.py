from datetime import datetime


def run_agent():
    now = datetime.utcnow().isoformat()

    tasks = [
        "Check available digital service opportunities",
        "Prepare potential service deliverables",
        "Review tasks requiring human approval",
    ]

    print(f"Luna Agent active: {now}")

    for number, task in enumerate(tasks, start=1):
        print(f"{number}. {task}")


if __name__ == "__main__":
    run_agent()
