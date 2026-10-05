#!/usr/bin/env python3
"""Confronto autenticato dei fingerprint dei due nodi R3 su Railway.

Legge il Bearer da R3_API_TOKEN nell'ambiente. **Non lo stampa mai**, non lo
scrive in nessun file e non lo mette nella ricevuta.

    R3_API_TOKEN=<dall'ambiente>  python3 fingerprint_nodi.py --out ricevuta.json

Senza token esce 2 e dice cosa manca: non finge un risultato.

Distingue il ritardo di sincronizzazione da un errore facendo DUE letture
distanziate e guardando se la divergenza converge. Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

NODI = {
    "node-a": "https://r3-external-node-a-production.up.railway.app",
    "node-v2": "https://r3-external-node-v2-production.up.railway.app",
}
PERCORSO = "/state/fingerprint"


def ora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def leggi(base: str, token: str, timeout: int = 45) -> tuple[int, dict | str]:
    req = urllib.request.Request(
        base + PERCORSO,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # il corpo di un errore non contiene il token: e' sicuro riportarlo
        return e.code, e.read().decode("utf-8", "replace")[:300]
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
        return 0, f"{type(e).__name__}: {e}"


def estrai(d: dict) -> dict:
    """Solo i campi che servono. Nessun segreto: verify_key e' pubblica."""
    return {
        "node_id": d.get("node_id"),
        "storage_id": d.get("storage_id"),
        "storage_id_created_this_boot": d.get("storage_id_created_this_boot"),
        "durable_state_detected": d.get("durable_state_detected"),
        "verify_key": d.get("verify_key"),
        "document_count": d.get("document_count"),
        "document_set_sha256": d.get("document_set_sha256"),
        "document_hashes": sorted(d.get("document_hashes") or []),
        "documents_missing_or_corrupt": sorted(
            d.get("documents_missing_or_corrupt") or []),
        "protocol_event_count": d.get("protocol_event_count"),
        "rrr_event_id": d.get("rrr_event_id"),
        "rrr_counter": d.get("rrr_counter"),
        "rrr_action": d.get("rrr_action"),
        "process_boot_id": d.get("process_boot_id"),
        "ts": d.get("ts"),
    }


def confronta(a: dict, b: dict) -> dict:
    sa, sb = set(a["document_hashes"]), set(b["document_hashes"])
    return {
        "insieme_identico": sa == sb,
        "solo_in_a": sorted(sa - sb),
        "solo_in_b": sorted(sb - sa),
        "comuni": len(sa & sb),
        "document_set_sha256_identico":
            a["document_set_sha256"] == b["document_set_sha256"],
        "storage_id_distinti": a["storage_id"] != b["storage_id"],
        "verify_key_distinte": a["verify_key"] != b["verify_key"],
        "corrotti_a": a["documents_missing_or_corrupt"],
        "corrotti_b": b["documents_missing_or_corrupt"],
    }


def giudizio(c1: dict, c2: dict, attesa: int) -> tuple[str, str]:
    """Ritardo di sincronizzazione o errore? Regola scritta prima di guardare."""
    corrotti = (c1["corrotti_a"] or c1["corrotti_b"]
                or c2["corrotti_a"] or c2["corrotti_b"])
    if corrotti:
        return "ERRORE", ("documents_missing_or_corrupt non vuoto: un digest "
                          "esiste senza il suo oggetto, o l'oggetto non "
                          "corrisponde. Non e' ritardo.")
    if c1["insieme_identico"] and c2["insieme_identico"]:
        return "COERENTE", "insiemi identici in entrambe le letture."
    d1 = len(c1["solo_in_a"]) + len(c1["solo_in_b"])
    d2 = len(c2["solo_in_a"]) + len(c2["solo_in_b"])
    if d2 < d1:
        return "RITARDO_DI_SINCRONIZZAZIONE", (
            f"divergenza scesa da {d1} a {d2} documenti in {attesa}s: "
            "converge, quindi e' propagazione in corso.")
    if d2 == d1:
        return "DIVERGENZA_PERSISTENTE", (
            f"divergenza ferma a {d1} documenti dopo {attesa}s: non converge. "
            "Serve una terza lettura piu' distante prima di chiamarlo errore.")
    return "DIVERGENZA_IN_AUMENTO", (
        f"divergenza salita da {d1} a {d2}: uno dei due nodi sta ricevendo "
        "scritture che l'altro non vede.")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="ricevuta_fingerprint.json")
    ap.add_argument("--attesa", type=int, default=45,
                    help="secondi fra le due letture (default 45)")
    a = ap.parse_args(argv)

    token = os.environ.get("R3_API_TOKEN", "")
    if not token:
        print("BLOCCATO: R3_API_TOKEN non e' nell'ambiente.", file=sys.stderr)
        print("Serve come variabile d'ambiente della sessione; non va "
              "incollato in chat.", file=sys.stderr)
        return 2

    letture = []
    for giro in (1, 2):
        if giro == 2:
            time.sleep(a.attesa)
        snap = {"giro": giro, "ora": ora(), "nodi": {}}
        for nome, base in NODI.items():
            codice, corpo = leggi(base, token)
            if codice != 200:
                print(f"BLOCCATO: {nome} ha risposto {codice}: {corpo}",
                      file=sys.stderr)
                return 3
            snap["nodi"][nome] = estrai(corpo)
        snap["confronto"] = confronta(snap["nodi"]["node-a"],
                                      snap["nodi"]["node-v2"])
        letture.append(snap)

    verdetto, motivo = giudizio(letture[0]["confronto"],
                               letture[1]["confronto"], a.attesa)
    ricevuta = {
        "schema": "R3-FINGERPRINT-COMPARE/1",
        "generato": ora(),
        "attesa_fra_letture_s": a.attesa,
        "percorso": PERCORSO,
        "nodi": {k: v for k, v in NODI.items()},
        "letture": letture,
        "verdetto": verdetto,
        "motivo": motivo,
        "nota_credenziali": "nessuna credenziale in questa ricevuta; "
                            "verify_key e storage_id sono pubblici",
    }
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(ricevuta, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")

    c = letture[-1]["confronto"]
    print(f"verdetto: {verdetto}")
    print(f"  {motivo}")
    print(f"  insieme documenti identico : {c['insieme_identico']}")
    print(f"  document_set_sha256 uguale : {c['document_set_sha256_identico']}")
    print(f"  documenti comuni           : {c['comuni']}")
    print(f"  solo su node-a / node-v2   : {len(c['solo_in_a'])} / {len(c['solo_in_b'])}")
    print(f"  storage_id distinti        : {c['storage_id_distinti']}")
    print(f"  corrotti o mancanti        : a={c['corrotti_a']} v2={c['corrotti_b']}")
    print(f"\nricevuta: {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
