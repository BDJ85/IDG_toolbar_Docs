#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Controleert register.json vóór je pusht naar Cloudflare Pages.

Gebruik:  python check_register.py            (vanuit de site-map)

Een publiek document waarvan het bestand ontbreekt is altijd een fout: dat zou
een dode tegel op de site opleveren. (--strict wordt nog geaccepteerd, doet niets extra.)

Exitcode 0 = in orde, 1 = fouten gevonden.
"""
import json
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
REGISTER = os.path.join(HIER, "register.json")

SOORTEN_TOEGESTAAN = None  # wordt uit het register gelezen
STATUS_TOEGESTAAN = {"actief", "concept", "vervangen", "archief"}
FORMAAT_TOEGESTAAN = {"html", "pdf", "zip"}
CODE_PATROON = re.compile(r"^(IDG|BDJ)-[A-Z]{2,4}-[A-Z0-9]{2,6}$")
MAAND_PATROON = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
VERPLICHT = ("code", "titel", "versie", "soort", "omschrijving", "doelgroep",
             "bestand", "formaat", "status", "publiek", "bijgewerkt")


def main(strict):
    fouten, waarschuwingen = [], []

    try:
        with open(REGISTER, encoding="utf-8") as f:
            reg = json.load(f)
    except (OSError, ValueError) as e:
        print("FOUT: register.json onleesbaar: {}".format(e))
        return 1

    soorten = set(reg.get("soorten", {}).keys())
    docs = reg.get("documenten", [])
    codes = {}

    for i, d in enumerate(docs):
        label = d.get("code") or "document #{}".format(i + 1)

        for veld in VERPLICHT:
            if veld not in d:
                fouten.append("{}: veld '{}' ontbreekt".format(label, veld))
        if any(v not in d for v in VERPLICHT):
            continue

        if not CODE_PATROON.match(d["code"]):
            fouten.append("{}: code volgt niet het patroon IDG-SOORT-KORT".format(label))
        if d["code"] in codes:
            fouten.append("{}: code komt dubbel voor".format(label))
        codes[d["code"]] = d

        if d["soort"] not in soorten:
            fouten.append("{}: onbekende soort '{}'".format(label, d["soort"]))
        elif d["code"].split("-")[1] != d["soort"]:
            fouten.append("{}: soort '{}' past niet bij de code".format(label, d["soort"]))
        if d["status"] not in STATUS_TOEGESTAAN:
            fouten.append("{}: onbekende status '{}'".format(label, d["status"]))
        if not isinstance(d["publiek"], bool):
            fouten.append("{}: 'publiek' moet true of false zijn".format(label))
        if not MAAND_PATROON.match(str(d["bijgewerkt"])):
            fouten.append("{}: 'bijgewerkt' moet JJJJ-MM zijn".format(label))
        if not isinstance(d["formaat"], list) or not set(d["formaat"]) <= FORMAAT_TOEGESTAAN:
            fouten.append("{}: 'formaat' moet een lijst zijn uit {}".format(label, sorted(FORMAAT_TOEGESTAAN)))
        if len(d["omschrijving"]) > 160:
            waarschuwingen.append("{}: omschrijving is {} tekens; op een tegel leest <160 prettiger".format(label, len(d["omschrijving"])))

        if d["status"] == "vervangen" and not d.get("vervangen_door"):
            fouten.append("{}: status 'vervangen' zonder 'vervangen_door'".format(label))
        if d["status"] == "vervangen" and d["publiek"]:
            waarschuwingen.append("{}: vervangen document staat op publiek".format(label))

        paden = [d["bestand"]] if d["bestand"] else []
        paden += [b.get("bestand") for b in d.get("bijlagen", [])]
        for p in paden:
            if not p:
                fouten.append("{}: bijlage zonder 'bestand'".format(label))
                continue
            if not os.path.isfile(os.path.join(HIER, p)):
                # Publiek document zonder bestand = fout, altijd. Anders komt een
                # dode tegel op de site. Niet-publiek = waarschuwing.
                (fouten if d["publiek"] else waarschuwingen).append(
                    "{}: bestand '{}' niet gevonden".format(label, p))
        if d["publiek"] and d["status"] == "actief" and not d["bestand"]:
            waarschuwingen.append("{}: publiek en actief, maar zonder bestand (tegel wordt grijs)".format(label))

    for d in docs:
        vd = d.get("vervangen_door")
        if vd and vd not in codes:
            fouten.append("{}: vervangen_door verwijst naar onbekende code '{}'".format(d["code"], vd))

    publiek = [d for d in docs if d.get("publiek") and d.get("status") == "actief"]
    print("Register {}  ·  {} documenten, {} publiek".format(reg.get("versie_register", "?"), len(docs), len(publiek)))
    for w in waarschuwingen:
        print("  let op  {}".format(w))
    for f_ in fouten:
        print("  FOUT    {}".format(f_))
    print("Resultaat: {}".format("in orde" if not fouten else "{} fout(en)".format(len(fouten))))
    return 1 if fouten else 0


if __name__ == "__main__":
    sys.exit(main("--strict" in sys.argv[1:]))
