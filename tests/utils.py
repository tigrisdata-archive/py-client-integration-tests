import json
from dataclasses import asdict


def pretty(obj):
    print(json.dumps(asdict(obj), default=str, indent=2))
