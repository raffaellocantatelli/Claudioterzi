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


def serie(letture: list[dict]) -> list[int]:
    """Divergenza osservata a ogni lettura: |A \\ B| + |B \\ A|."""
    return [len(l["confronto"]["solo_in_a"]) + len(l["confronto"]["solo_in_b"])
            for l in letture]


def giudizio(letture: list[dict], attese: list[int]) -> tuple[str, str]:
    """Registra osservazioni. Non nomina cause, nemmeno per negarle.

    Correzione di Claudio, 2026-10-05: non si deduce la causa di una
    divergenza dal fatto che cresca o diminuisca, e con due letture si
    descrive la variazione senza dichiarare convergenza.

    La convergenza si verifica **raggiungendo l'uguaglianza** su almeno tre
    letture, non inferendola da una pendenza. Il perche' sta qui, nella
    docstring: il motivo restituito resta descrittivo, perche' finisce in una
    ricevuta leggibile da macchina e li' una spiegazione causale verrebbe
    riusata come se fosse un reperto.
    """
    segnalati = [
        {"lettura": i + 1,
         "node-a": l["confronto"]["corrotti_a"],
         "node-v2": l["confronto"]["corrotti_b"]}
        for i, l in enumerate(letture)
        if l["confronto"]["corrotti_a"] or l["confronto"]["corrotti_b"]
    ]
    if segnalati:
        return "INTEGRITA_SEGNALATA_DAL_NODO", (
            "il campo documents_missing_or_corrupt non e' vuoto alle letture "
            f"{[x['lettura'] for x in segnalati]}: {segnalati}. "
            "Valore riportato dal nodo, non interpretato.")

    d = serie(letture)
    n = len(d)
    if all(x == 0 for x in d):
        return "INSIEMI_UGUALI", (
            f"divergenza 0 in tutte le {n} letture.")
    if n < 3:
        return "VARIAZIONE_OSSERVATA", (
            f"serie {d} su {n} letture, attese {attese}s. "
            f"variazione fra prima e ultima: {d[-1] - d[0]:+d}. "
            "Con meno di tre letture non dichiaro convergenza.")
    if d[-1] == 0:
        return "UGUAGLIANZA_RAGGIUNTA", (
            f"serie {d}: la divergenza e' 0 alla lettura {n} dopo essere "
            f"stata {d[0]} alla prima. Uguaglianza osservata, non dedotta.")
    passi = [b - a for a, b in zip(d, d[1:])]
    return "DIVERGENZA_NON_RISOLTA", (
        f"serie {d}, variazioni per passo {passi}, attese {attese}s. "
        f"la divergenza non e' 0 all'ultima lettura: {d[-1]} documenti. "
        "nessuna convergenza osservata.")


def _parole_causali(testo: str) -> list[str]:
    """Parole che spiegherebbero il perche'. Non devono stare in un verdetto."""
    return [w for w in ("ritardo", "sincronizzazione", "propagazione",
                        "guasto", "perche", "causa", "compatibile")
            if w in testo.lower()]


def self_test(giudice=None) -> int:
    """Casi controllati sulla funzione di giudizio.

    `giudice` serve al controllo negativo: passando l'implementazione
    precedente, questi stessi casi DEVONO fallire. Un test che passa su
    entrambe le versioni non distingue niente.
    """
    g = giudice or giudizio

    def finta(div: int, corrotti_a=(), corrotti_b=()) -> dict:
        return {"confronto": {
            "solo_in_a": [f"h{i}" for i in range(div)],
            "solo_in_b": [],
            "corrotti_a": list(corrotti_a),
            "corrotti_b": list(corrotti_b),
        }}

    casi = [
        ("insiemi uguali",            [finta(0), finta(0), finta(0)], "INSIEMI_UGUALI"),
        ("mancanti o corrotti",       [finta(0, corrotti_b=["y"]), finta(0), finta(0)],
                                      "INTEGRITA_SEGNALATA_DAL_NODO"),
        ("corrotti pur arrivando a 0", [finta(3), finta(1), finta(0, corrotti_a=["x"])],
                                      "INTEGRITA_SEGNALATA_DAL_NODO"),
        ("divergenza decrescente a 0", [finta(5), finta(2), finta(0)], "UGUAGLIANZA_RAGGIUNTA"),
        ("decrescente, non a 0",      [finta(9), finta(5), finta(3)], "DIVERGENZA_NON_RISOLTA"),
        ("divergenza crescente",      [finta(1), finta(3), finta(7)], "DIVERGENZA_NON_RISOLTA"),
        ("ferma sopra zero",          [finta(4), finta(4), finta(4)], "DIVERGENZA_NON_RISOLTA"),
        ("due letture, in discesa",   [finta(6), finta(2)],           "VARIAZIONE_OSSERVATA"),
        ("due letture, in salita",    [finta(2), finta(6)],           "VARIAZIONE_OSSERVATA"),
        ("due letture, arriva a 0",   [finta(4), finta(0)],           "VARIAZIONE_OSSERVATA"),
    ]
    ok = True
    for nome, letture, atteso in casi:
        try:
            v, motivo = g(letture, [45] * (len(letture) - 1))
        except Exception as e:                      # noqa: BLE001
            v, motivo = f"ECCEZIONE:{type(e).__name__}", ""
        buono = v == atteso
        if not buono:
            ok = False
        print(f"  {nome:28s} -> {v:30s} {'OK' if buono else f'NO (atteso {atteso})'}")

    # proprieta' 1: nessun verdetto sulla divergenza nomina una causa
    for nome, letture in (("discesa", [finta(9), finta(5), finta(3)]),
                          ("salita",  [finta(1), finta(3), finta(7)]),
                          ("due letture", [finta(6), finta(2)])):
        try:
            _, motivo = g(letture, [45] * (len(letture) - 1))
        except Exception:                           # noqa: BLE001
            motivo = ""
        trovate = _parole_causali(motivo)
        if trovate:
            ok = False
        print(f"  {'nessuna causa: ' + nome:28s} -> "
              f"{'OK' if not trovate else 'NO: ' + str(trovate)}")

    # proprieta' 2: con due letture non si dichiara convergenza
    try:
        v, motivo = g([finta(4), finta(0)], [45])
    except Exception:                               # noqa: BLE001
        v, motivo = "ECCEZIONE", ""
    senza = "converg" not in (v + motivo).lower() or "non dichiaro" in motivo.lower()
    if not senza:
        ok = False
    print(f"  {'due letture: nessuna converg.':28s} -> {'OK' if senza else 'NO'}")

    print("  esito:", "OK" if ok else "GIUDIZIO INAFFIDABILE")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="ricevuta_fingerprint.json")
    ap.add_argument("--self-test", action="store_true",
                    help="esegue la funzione di giudizio su serie sintetiche")
    ap.add_argument("--letture", type=int, default=3,
                    help="quante letture (default 3: due non bastano a "
                         "osservare una convergenza)")
    ap.add_argument("--attesa", type=int, default=45,
                    help="secondi fra una lettura e la successiva (default 45)")
    a = ap.parse_args(argv)

    if a.self_test:
        return self_test()

    token = os.environ.get("R3_API_TOKEN", "")
    if not token:
        print("BLOCCATO: R3_API_TOKEN non e' nell'ambiente.", file=sys.stderr)
        print("Serve come variabile d'ambiente della sessione; non va "
              "incollato in chat.", file=sys.stderr)
        return 2

    if a.letture < 2:
        print("Servono almeno 2 letture.", file=sys.stderr)
        return 4

    letture, attese = [], []
    for giro in range(1, a.letture + 1):
        if giro > 1:
            time.sleep(a.attesa)
            attese.append(a.attesa)
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

    verdetto, motivo = giudizio(letture, attese)
    ricevuta = {
        "schema": "R3-FINGERPRINT-COMPARE/1",
        "generato": ora(),
        "letture_richieste": a.letture,
        "attesa_fra_letture_s": a.attesa,
        "serie_divergenza": serie(letture),
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
