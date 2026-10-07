#!/usr/bin/env python3
"""Validatore di documenti ecc.memory.v1 — libreria standard soltanto.

Lo schema e' di `affaan-m/ECC` (MIT), copiato con hash in PROVENIENZA.md.
Il loro runtime NON viene eseguito: e' codice scaricato, e per validare dei
dati non serve.

    python3 valida_ecc.py <documento.json> [...]
    python3 valida_ecc.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
SCHEMA = QUI / "ecc.memory.v1.schema.json"


def carica_schema() -> dict:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def _controlla(valore, regola: dict, defs: dict, dove: str) -> list[str]:
    g: list[str] = []
    if "$ref" in regola:
        nome = regola["$ref"].rsplit("/", 1)[-1]
        return _controlla(valore, defs[nome], defs, dove)
    if "const" in regola and valore != regola["const"]:
        g.append(f"{dove}: vale {valore!r}, atteso {regola['const']!r}")
    if "enum" in regola and valore not in regola["enum"]:
        g.append(f"{dove}: {valore!r} non in {regola['enum']}")
    t = regola.get("type")
    if t == "string":
        if not isinstance(valore, str):
            return g + [f"{dove}: non e' una stringa"]
        if "minLength" in regola and len(valore) < regola["minLength"]:
            g.append(f"{dove}: piu' corto di {regola['minLength']}")
        if "maxLength" in regola and len(valore) > regola["maxLength"]:
            g.append(f"{dove}: {len(valore)} caratteri, massimo {regola['maxLength']}")
        if "pattern" in regola and not re.search(regola["pattern"], valore):
            g.append(f"{dove}: non corrisponde al pattern")
    elif t == "array":
        if not isinstance(valore, list):
            return g + [f"{dove}: non e' un array"]
        if "minItems" in regola and len(valore) < regola["minItems"]:
            g.append(f"{dove}: meno di {regola['minItems']} elementi")
        if "maxItems" in regola and len(valore) > regola["maxItems"]:
            g.append(f"{dove}: piu' di {regola['maxItems']} elementi")
        if regola.get("uniqueItems") and len(set(map(str, valore))) != len(valore):
            g.append(f"{dove}: elementi duplicati")
        for i, v in enumerate(valore):
            g += _controlla(v, regola.get("items", {}), defs, f"{dove}[{i}]")
    return g


def valida(doc: dict) -> list[str]:
    s = carica_schema()
    defs = s.get("definitions", {})
    g: list[str] = []
    if not isinstance(doc, dict):
        return ["il documento non e' un oggetto"]
    for k in s["required"]:
        if k not in doc:
            g.append(f"campo obbligatorio mancante: {k}")
    if s.get("additionalProperties") is False:
        extra = sorted(set(doc) - set(s["properties"]))
        for k in extra:
            g.append(f"campo NON ammesso: {k} (additionalProperties: false)")
    for k, v in doc.items():
        if k in s["properties"]:
            g += _controlla(v, s["properties"][k], defs, k)
    return g


def self_test() -> int:
    base = {
        "schema": "ecc.memory.v1", "id": "mem_prova-001", "title": "Prova",
        "kind": "lesson", "scope": "project", "trust": "unreviewed",
        "status": "active", "sourceHarness": "claude-code",
        "targetHarnesses": ["codex"], "tags": ["r3"], "links": [],
        "createdAt": "2026-10-07T10:00:00.000Z",
        "updatedAt": "2026-10-07T10:00:00.000Z", "body": "corpo",
    }
    casi = [
        ("documento conforme", base, True),
        ("campo in piu'", {**base, "disaccordi": ["x"]}, False),
        ("trust diverso da unreviewed", {**base, "trust": "verified"}, False),
        ("kind inventato", {**base, "kind": "autobiografia"}, False),
        ("id senza prefisso mem_", {**base, "id": "auto-2026-10-04-01"}, False),
        ("timestamp senza millisecondi", {**base, "createdAt": "2026-10-07T10:00:00Z"}, False),
        ("targetHarnesses vuoto", {**base, "targetHarnesses": []}, False),
        ("campo obbligatorio mancante", {k: v for k, v in base.items() if k != "links"}, False),
        ("body vuoto", {**base, "body": ""}, False),
    ]
    ok = True
    for nome, doc, atteso in casi:
        g = valida(doc)
        passa = not g
        if passa != atteso:
            ok = False
        print(f"  {nome:34s} {'conforme' if passa else 'respinto':9s} "
              f"{'OK' if passa == atteso else 'NO'}")
    print("  esito:", "OK" if ok else "VALIDATORE INAFFIDABILE")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("documenti", nargs="*", type=Path)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.documenti:
        ap.error("serve almeno un documento")
    rc = 0
    for p in a.documenti:
        g = valida(json.loads(p.read_text(encoding="utf-8")))
        if g:
            rc = 1
            print(f"NON CONFORME — {p.name}")
            for x in g:
                print(f"  - {x}")
        else:
            print(f"CONFORME — {p.name}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
