"""Module for static caching of JSON rules data."""

import json
import pathlib

DATA = {}
dir_ = pathlib.Path(__file__).parent.resolve()
with open(f"{dir_}/rules.json", mode="r", encoding="utf8") as rules_json:
    DATA = json.load(rules_json)
