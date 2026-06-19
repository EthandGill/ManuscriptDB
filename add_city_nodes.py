#!/usr/bin/env python3
"""
add_city_nodes.py — append the manuscript find-site city nodes that
check_city_nodes.py flagged as orphans to static/data/custom_locations.json.
Idempotent (skips any node already present by id or ~same coordinate) and fully
offline. Run it, then re-run check_city_nodes.py to confirm ORPHAN drops.
"""
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "static", "data", "custom_locations.json")

# name + modern derived from the EDH/HGV find-spot label; coordinate is the
# orphan coordinate reported by check_city_nodes.py (so the manuscripts snap to it).
NEW = [
    {"id": "thebes_region",   "name": "Thebes",                  "modern": "Luxor, Egypt",                  "lat": 27.5,     "lon": 32.5},
    {"id": "kysis_dush",      "name": "Kysis (Dush)",            "modern": "Dush, Kharga Oasis, Egypt",     "lat": 25.7837,  "lon": 30.5539},
    {"id": "prosopite_nome",  "name": "Prosopite Nome",          "modern": "Nile Delta, Egypt",             "lat": 30.4375,  "lon": 30.7466},
    {"id": "kysis_oasis",     "name": "Kysis (Kharga Oasis)",    "modern": "Kharga Oasis, Egypt",           "lat": 24.5804,  "lon": 30.7166},
    {"id": "hibis_oasis",     "name": "Hibis (Kharga Oasis)",    "modern": "Kharga Oasis, Egypt",           "lat": 25.4764,  "lon": 30.5552},
    {"id": "akoris",          "name": "Akoris",                  "modern": "Tihna el-Gebel, Egypt",         "lat": 28.189,   "lon": 30.7713},
    {"id": "markopolis",      "name": "Markopolis (Osrhoene)",   "modern": "Şanlıurfa region, Turkey",      "lat": 36.9764,  "lon": 38.4244},
    {"id": "mons_claudianus", "name": "Mons Claudianus",         "modern": "Eastern Desert, Egypt",         "lat": 26.8092,  "lon": 33.4869},
    {"id": "moirai",          "name": "Moirai (Hermopolites)",   "modern": "Hermopolite nome, Egypt",       "lat": 27.4417,  "lon": 30.7473},
    {"id": "ammoniake",       "name": "Ammoniake",               "modern": "Western Desert, Egypt",         "lat": 29.2052,  "lon": 25.5435},
    {"id": "terenuthis",      "name": "Terenuthis",              "modern": "Kom Abu Billo, Egypt",          "lat": 30.4324,  "lon": 30.8158},
    {"id": "omboi",           "name": "Omboi (Kom Ombo)",        "modern": "Kom Ombo, Egypt",               "lat": 24.4521,  "lon": 32.9284},
    {"id": "rhinokorura",     "name": "Rhinokorura",             "modern": "El-Arish, Egypt",               "lat": 31.1118,  "lon": 33.7969},
    {"id": "metelite_nome",   "name": "Metelite Nome",           "modern": "Nile Delta, Egypt",             "lat": 31.25,    "lon": 30.25},
    {"id": "naukratis",       "name": "Naukratis",               "modern": "Kom Gieif, Egypt",              "lat": 30.9005,  "lon": 30.5919},
    {"id": "nikiu",           "name": "Nikiu (Prosopites)",      "modern": "Nile Delta, Egypt",             "lat": 30.4115,  "lon": 30.851},
    {"id": "primis",          "name": "Primis (Qasr Ibrim)",     "modern": "Nubia, Egypt",                  "lat": 22.6497,  "lon": 31.9928},
    {"id": "oasis_parva",     "name": "Oasis Parva (Bahariya)",  "modern": "Bahariya Oasis, Egypt",         "lat": 28.3733,  "lon": 28.8971},
    {"id": "hermopolite_nome","name": "Hermopolite Nome",        "modern": "Hermopolite nome, Egypt",       "lat": 28.2119,  "lon": 30.717},
    {"id": "menelaite_nome",  "name": "Menelaite Nome",          "modern": "Nile Delta, Egypt",             "lat": 31.1752,  "lon": 30.3559},
]

data = json.load(open(PATH, encoding="utf-8"))
ids = {c.get("id") for c in data}

def near(a):
    return any(abs(c["lat"] - a["lat"]) < 0.01 and abs(c["lon"] - a["lon"]) < 0.01 for c in data)

added = 0
for n in NEW:
    if n["id"] in ids or near(n):
        continue
    data.append(n)
    ids.add(n["id"])
    added += 1

json.dump(data, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"Added {added} city nodes (file now has {len(data)}). Re-run: py check_city_nodes.py")
