#!/usr/bin/env python3
"""Valida un artefatto contro R3 EXPORT GATE — OGNI NODO.

Il gate e' scritto in un documento. Un cancello che nessuno controlla e' un
`continue-on-error`: la regola resta vera sulla carta mentre il lavoro
inconforme passa. Questo script lo rende applicato invece che dichiarato.

    python3 verifica_export.py <artefatto.txt>     # 0 = CONFORME
    python3 verifica_export.py --self-test

Non giudica la qualita' del lavoro. Controlla che i campi obbligatori ci siano
e che l'artefatto sia **coerente con se stesso** — che e' l'unica cosa
verificabile dall'esterno senza fidarsi del nodo.

Formato: `CHIAVE: valore` su una riga, oppure `CHIAVE:` seguito dalle righe
successive fino alla chiave seguente. Una chiave e' una riga che inizia a
colonna zero e corrisponde a ^[A-Z][A-Z0-9_/]*:

Stdlib only.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

CHIAVE = re.compile(r"^([A-Z][A-Z0-9_/]*):[ \t]*(.*)$")

# Gate unificato, accettato il 2026-10-04: f848f19 piu' GIT_STATUS e
# REAL_POSTGRES_BACKEND, zero rimozioni.
SEMPRE = [
    "NODE_ID", "SESSION_DATE", "ARTIFACT_TYPE", "CLAIMED_BASE_SHA",
    "LOCAL_HEAD_SHA", "BRANCH", "GIT_STATUS", "REPRODUCIBILITY",
    "TEST_COMMANDS", "TEST_OUTPUT_RAW", "PASS/FAIL/SKIP", "SANDBOX_BACKEND",
    "REAL_POSTGRES_BACKEND", "DESIGN_ONLY_DECLARATION", "KNOWN_ISSUES",
    "CLAIM_RETRACTIONS",
]
SOLO_PATCH = ["CHANGED_FILES", "DIFF_STAT", "PATCH", "PATCH_SHA256", "PATCH_BYTES"]

TIPI = {"PATCH", "DESIGN", "REVIEW", "TEST"}
ESITI = {"PASS", "FAIL", "SKIP"}
DICHIARAZIONI = {"IMPLEMENTED", "DESIGN_ONLY", "MIXED"}
GIT_STATI = {"CLEAN", "DIRTY"}
PG_STATI = {"PENDING", "RUN", "FAILED", "PASSED", "NOT_APPLICABLE"}
SHA_O_NA = re.compile(r"^(?:[0-9a-f]{7,64}|NOT_AVAILABLE)$")


def leggi(testo: str) -> dict[str, str]:
    campi, chiave, buf = {}, None, []
    for riga in testo.splitlines():
        m = CHIAVE.match(riga)
        if m:
            if chiave is not None:
                campi[chiave] = "\n".join(buf).strip("\n")
            chiave, resto = m.group(1), m.group(2)
            buf = [resto] if resto.strip() else []
        elif chiave is not None:
            buf.append(riga)
    if chiave is not None:
        campi[chiave] = "\n".join(buf).strip("\n")
    return campi


def valida(testo: str) -> list[str]:
    g: list[str] = []
    c = leggi(testo)
    if not c:
        return ["nessun campo riconosciuto: il formato non e' quello del gate"]

    tipo = c.get("ARTIFACT_TYPE", "").strip()
    richiesti = list(SEMPRE) + (SOLO_PATCH if tipo == "PATCH" else [])
    for k in richiesti:
        if k not in c:
            g.append(f"campo mancante: {k}")
        elif not c[k].strip():
            g.append(f"campo vuoto: {k}")

    if tipo and tipo not in TIPI:
        g.append(f"ARTIFACT_TYPE '{tipo}' non in {sorted(TIPI)}")

    esito = c.get("PASS/FAIL/SKIP", "").strip().upper()
    if esito and esito not in ESITI:
        g.append(f"PASS/FAIL/SKIP '{esito}' non in {sorted(ESITI)}")

    git_st = c.get("GIT_STATUS", "").strip().upper()
    if git_st and not any(g in git_st for g in GIT_STATI):
        g.append(f"GIT_STATUS '{git_st[:24]}' non contiene clean ne' dirty")

    pg = c.get("REAL_POSTGRES_BACKEND", "").strip().upper()
    if pg and pg not in PG_STATI:
        g.append(f"REAL_POSTGRES_BACKEND '{pg}' non in {sorted(PG_STATI)}")

    for k in ("CLAIMED_BASE_SHA", "LOCAL_HEAD_SHA"):
        v = c.get(k, "").strip()
        if v and not SHA_O_NA.match(v):
            g.append(f"{k} non e' un sha ne' NOT_AVAILABLE: '{v[:24]}'")

    dich = c.get("DESIGN_ONLY_DECLARATION", "")
    if dich and not any(d in dich.upper() for d in DICHIARAZIONI):
        g.append("DESIGN_ONLY_DECLARATION non contiene nessuna fra "
                 f"{sorted(DICHIARAZIONI)}: ogni claim va etichettato")

    if tipo == "PATCH":
        patch = c.get("PATCH", "")
        # il gate dice: testuale, non link
        if re.search(r"https?://", patch) and len(patch) < 400:
            g.append("PATCH sembra un link, non il testo della patch: "
                     "il gate chiede il testo")
        dichiarato = c.get("PATCH_SHA256", "").strip().lower()
        corpo = (patch + "\n").encode()
        reale = hashlib.sha256(patch.encode()).hexdigest()
        reale_nl = hashlib.sha256(corpo).hexdigest()
        if dichiarato and dichiarato not in (reale, reale_nl):
            g.append(f"PATCH_SHA256 non corrisponde al PATCH incluso "
                     f"(calcolato {reale[:16]}...): l'artefatto non e' "
                     "coerente con se stesso")
        byte = c.get("PATCH_BYTES", "").strip()
        if byte.isdigit() and int(byte) not in (len(patch.encode()), len(corpo)):
            g.append(f"PATCH_BYTES dice {byte}, il PATCH incluso ne ha "
                     f"{len(patch.encode())}")
    return g


def self_test() -> int:
    base = ("NODE_ID: prova\nSESSION_DATE: 2026-10-04T00:00:00Z\n"
            "ARTIFACT_TYPE: REVIEW\nCLAIMED_BASE_SHA: NOT_AVAILABLE\n"
            "LOCAL_HEAD_SHA: NOT_AVAILABLE\nBRANCH: NOT_AVAILABLE\n"
            "REPRODUCIBILITY: nessuna\nTEST_COMMANDS: nessuno\n"
            "TEST_OUTPUT_RAW: nessuno\nPASS/FAIL/SKIP: SKIP\n"
            "GIT_STATUS: clean\n"
            "SANDBOX_BACKEND: in-memory\n"
            "REAL_POSTGRES_BACKEND: NOT_APPLICABLE\n"
            "DESIGN_ONLY_DECLARATION: tutto DESIGN_ONLY\n"
            "KNOWN_ISSUES: nessuno\nCLAIM_RETRACTIONS: nessuna\n")
    casi = [
        ("artefatto conforme", base, 0),
        ("campo mancante", base.replace("KNOWN_ISSUES: nessuno\n", ""), 1),
        ("campo vuoto", base.replace("SANDBOX_BACKEND: in-memory",
                                     "SANDBOX_BACKEND:"), 1),
        ("tipo inventato", base.replace("ARTIFACT_TYPE: REVIEW",
                                        "ARTIFACT_TYPE: POESIA"), 1),
        ("esito inventato", base.replace("PASS/FAIL/SKIP: SKIP",
                                         "PASS/FAIL/SKIP: QUASI"), 1),
        ("git status inventato", base.replace("GIT_STATUS: clean",
                                              "GIT_STATUS: forse"), 1),
        ("postgres stato inventato",
         base.replace("REAL_POSTGRES_BACKEND: NOT_APPLICABLE",
                      "REAL_POSTGRES_BACKEND: BOH"), 1),
        ("claim non etichettato",
         base.replace("DESIGN_ONLY_DECLARATION: tutto DESIGN_ONLY",
                      "DESIGN_ONLY_DECLARATION: funziona"), 1),
        ("PATCH con hash sbagliato",
         base.replace("ARTIFACT_TYPE: REVIEW", "ARTIFACT_TYPE: PATCH")
             + "CHANGED_FILES: a.py\nDIFF_STAT: 1 file\n"
               "PATCH: --- a/a.py\nPATCH_SHA256: " + "0" * 64
             + "\nPATCH_BYTES: 11\n", 1),
    ]
    ok = True
    for nome, testo, atteso in casi:
        g = valida(testo)
        rc = 1 if g else 0
        if rc != atteso:
            ok = False
        print(f"  {nome:28s} {'OK' if rc == atteso else f'NO ({g})'}")
    print("  esito:", "OK" if ok else "VALIDATORE INAFFIDABILE")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("artefatto", nargs="?", type=Path)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.artefatto or not a.artefatto.is_file():
        ap.error("serve il percorso di un artefatto")

    g = valida(a.artefatto.read_text(encoding="utf-8"))
    if g:
        print(f"NON CONFORME — {a.artefatto.name}")
        for x in g:
            print(f"  - {x}")
        print("\nPer la regola di ammissione del gate: "
              "NODE_ID -> CANDIDATE / EVIDENCE NOT EXPORTED")
        return 1
    print(f"CONFORME — {a.artefatto.name}")
    print("Il nodo entra nella matrice delle evidenze per questo artefatto.")
    print("\nNota: conformita' di formato e coerenza interna. NON e' un "
          "giudizio\nsulla correttezza del lavoro, che resta da valutare.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
