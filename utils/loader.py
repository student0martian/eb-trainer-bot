import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

_tickets = {}


def load_tickets():
    _tickets.clear()
    for path in sorted(DATA_DIR.glob("test*.json")):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        _tickets[data["ticket_id"]] = data
    return _tickets


def get_ticket(ticket_id):
    return _tickets.get(ticket_id)


def get_ticket_ids():
    return sorted(_tickets)
