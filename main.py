import json
from datetime import datetime


def load_json(filename):
    with open(filename, "r") as file:
        return json.load(file)


def run_agent():
    config = load_json("config.json")
    services = load_json("services.json")
    tasks = load_json("tasks.json")

    print(f"Agent: {config['agent_name']}")
    print(f"Mode: {config['mode']}")
    print(f"Time: {datetime.utcnow().isoformat()}")
    print(f"Available services: {len(services['services'])}")
    print(f"Pending tasks: {len(tasks['tasks'])}")
    print(f"Completed tasks: {len(tasks['completed'])}")


if __name__ == "__main__":
    run_agent()
