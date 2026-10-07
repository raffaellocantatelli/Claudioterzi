#!/usr/bin/env python3
"""Traduce le voci di AUTOBIOGRAFIA.md in documenti ecc.memory.v1.

Lo scopo non e' l'esportazione: e' **misurare cosa va perso**. Lo schema di
ECC ha `additionalProperties: false`, quindi ogni nostro campo che non trova
un campo loro non puo' essere aggiunto: o degrada a prosa dentro `body`, o
sparisce. La misura e' l'elenco di quali.

    python3 autobiografia_a_ecc.py --out uscita/

Stdlib only. Non esegue nulla del repository ECC.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
FONTE = QUI.parent / "AUTOBIOGRAFIA.md"
SCHEMA = json.loads((QUI / "ecc.memory.v1.schema.json").read_text(encoding="utf-8"))

# I campi del NOSTRO schema, nell'ordine in cui li abbiamo definiti.
NOSTRI = ["voce_id", "data", "evento", "percezioni", "disaccordi", "decisione",
          "conseguenza", "errore_scoperto", "autocorrezione", "modifica_stato"]

# Mappatura verso un campo STRUTTURATO loro. None = nessun campo: degrada a prosa.
MAPPA = {
    "voce_id":         "id",
    "data":            "createdAt / updatedAt",
    "evento":          "title (troncato) + body",
    "percezioni":      None,
    "disaccordi":      None,
    "decisione":       None,
    "conseguenza":     None,
    "errore_scoperto": None,
    "autocorrezione":  None,
    "modifica_stato":  None,
}

TARGET = ["codex", "cursor", "opencode", "gemini", "hermes"]


def estrai_voci(testo: str) -> list[dict]:
    """Ogni voce e' un blocco ```yaml ... ``` che contiene voce_id."""
    voci = []
    for blocco in re.findall(r"```yaml\n(.*?)```", testo, re.S):
        if "voce_id:" not in blocco:
            continue
        # il blocco della sezione 1 e' il MODELLO: ha segnaposto, non valori.
        # Si riconosce da una data che non e' una data.
        m_data = re.search(r"^data:\s*(.+)$", blocco, re.M)
        if not m_data or not re.match(r"^\d{4}-\d{2}-\d{2}$", m_data.group(1).strip()):
            continue
        campi, chiave = {}, None
        for riga in blocco.splitlines():
            m = re.match(r"^([a-z_]+):\s*(.*)$", riga)
            if m:
                chiave = m.group(1)
                campi[chiave] = m.group(2).strip()
            elif chiave:
                campi[chiave] += "\n" + riga
        campi["_grezzo"] = blocco
        voci.append(campi)
    return voci


def a_ecc(voce: dict, precedente: str | None) -> dict:
    vid = voce["voce_id"].strip().lower()
    mem_id = "mem_" + re.sub(r"[^a-z0-9_-]", "-", vid)
    data = voce["data"].strip()
    ts = f"{data}T00:00:00.000Z"
    evento = " ".join(voce.get("evento", "").split())
    titolo = (evento[:150] + "…") if len(evento) > 150 else (evento or vid)
    # tutto cio' che non ha un campo loro finisce qui, come prosa
    corpo = [f"# {vid}", "", "Voce di autobiografia computazionale R3.",
             "Formato originale conservato per intero: lo schema ecc.memory.v1",
             "non ha campi per percezioni, disaccordi, errori e autocorrezioni.",
             "", "```yaml", voce["_grezzo"].rstrip(), "```"]
    return {
        "schema": "ecc.memory.v1",
        "id": mem_id,
        "title": titolo,
        "kind": "lesson",
        "scope": "project",
        "trust": "unreviewed",
        "status": "active",
        "sourceHarness": "claude-code",
        "targetHarnesses": TARGET,
        "tags": ["r3", "autobiografia", "protocollo-rosso"],
        "links": [precedente] if precedente else [],
        "createdAt": ts,
        "updatedAt": ts,
        "body": "\n".join(corpo),
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=QUI / "uscita")
    a = ap.parse_args(argv)
    if not FONTE.is_file():
        raise SystemExit(f"manca {FONTE}")

    voci = estrai_voci(FONTE.read_text(encoding="utf-8"))
    if not voci:
        raise SystemExit("nessuna voce trovata in AUTOBIOGRAFIA.md")
    a.out.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(QUI))
    import valida_ecc

    prec, scritti = None, []
    for v in voci:
        doc = a_ecc(v, prec)
        guasti = valida_ecc.valida(doc)
        if guasti:
            print(f"NON CONFORME: {doc['id']}", file=sys.stderr)
            for g in guasti:
                print(f"  - {g}", file=sys.stderr)
            return 1
        f = a.out / f"{doc['id']}.json"
        f.write_text(json.dumps(doc, indent=2, ensure_ascii=False,
                                sort_keys=True) + "\n", encoding="utf-8")
        scritti.append(f.name)
        prec = doc["id"]

    # --- la misura ---
    strutturati = [k for k in NOSTRI if MAPPA[k]]
    prosa = [k for k in NOSTRI if not MAPPA[k]]
    loro = sorted(SCHEMA["properties"])
    nostri_senza_casa = len(prosa)

    print(f"voci tradotte e validate: {len(scritti)} -> {a.out}")
    for n in scritti:
        print(f"  {n}")
    print()
    print(f"campi nostri: {len(NOSTRI)}   campi loro: {len(loro)}")
    print(f"con un campo strutturato corrispondente: {len(strutturati)}")
    for k in strutturati:
        print(f"   {k:16s} -> {MAPPA[k]}")
    print(f"\nSENZA casa strutturata, degradati a prosa dentro body: "
          f"{nostri_senza_casa} su {len(NOSTRI)}")
    for k in prosa:
        print(f"   {k}")
    print("\nMotivo: additionalProperties = "
          f"{SCHEMA.get('additionalProperties')}. Nessun campo in piu' e' ammesso.")
    print("Conseguenza: per una macchina quei campi non esistono. Restano")
    print("leggibili da un umano, e invisibili a una query.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
