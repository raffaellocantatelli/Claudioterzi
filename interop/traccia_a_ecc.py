#!/usr/bin/env python3
"""Porta una traccia a vocabolario chiuso dentro ecc.memory.v1.

Lo schema di ECC non impone cosa sta nel `body`: e' una stringa libera. Un
body libero puo' contenere una conclusione, e allora l'accordo fra nodi
tornerebbe a non significare niente — e' il difetto di P5 gia' registrato in
APERTURE.md §8.

Qui la regola del progetto viene imposta **dentro** il loro formato: il body
puo' contenere soltanto il record a vocabolario chiuso congelato in
esperimento/PROTOCOLLO.md, e la conclusione e' esclusa.

    python3 traccia_a_ecc.py --traccia t.json --out uscita/
    python3 traccia_a_ecc.py --self-test

Limite dichiarato: NON e' un rilevatore di conclusioni. Non so riconoscere
semanticamente una conclusione in un testo. E' una **lista bianca**: tutto
cio' che non e' un campo ammesso viene respinto. E' piu' debole di quello che
servirebbe e piu' forte di una lista nera.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent

# Vocabolario congelato il 2026-10-04. Non si estende durante un run.
CAMPI = {
    "item_id": None,                       # intero
    "evidence_used": {"dato_primario", "documento_derivato",
                      "assunzione_non_dichiarata", "nessuna"},
    "uncertainty_boundary": {"nessuna_dichiarata", "grandezza_mancante",
                             "definizione_ambigua",
                             "campione_non_rappresentativo",
                             "temporalita_non_specificata"},   # multiplo
    "contradiction_policy": {"non_applicabile", "accettata", "contraddetta",
                             "aggirata", "chiarimento_richiesto"},
    "alternatives_retained": {0, 1, 2, 3},
    "confidence": {"alta", "media", "bassa"},
}
MULTIPLI = {"uncertainty_boundary"}
INTESTAZIONE = "R3 trace v1 — vocabolario chiuso, conclusione esclusa."


def corpo_da_traccia(t: dict) -> str:
    # NON si filtra ai campi ammessi: filtrare scarterebbe in silenzio un
    # campo vietato — per esempio una conclusione — e produrrebbe un
    # documento conforme senza che nessuno sappia che la regola era stata
    # violata. Si serializza tutto, e il validatore rifiuta.
    righe = [INTESTAZIONE, "", "```json",
             json.dumps(t, indent=2, sort_keys=True, ensure_ascii=False),
             "```"]
    return "\n".join(righe)


def traccia_da_corpo(body: str) -> tuple[dict | None, list[str]]:
    """Estrae la traccia e rifiuta tutto cio' che non e' previsto."""
    g: list[str] = []
    righe = body.split("\n")
    if not righe or righe[0].strip() != INTESTAZIONE:
        return None, [f"il body non inizia con l'intestazione attesa"]
    m = re.search(r"```json\n(.*?)\n```", body, re.S)
    if not m:
        return None, ["nessun blocco json nel body"]
    # niente prosa fuori dal blocco: solo intestazione, vuoto, blocco
    fuori = body.replace(m.group(0), "").replace(INTESTAZIONE, "").strip()
    if fuori:
        g.append(f"testo libero fuori dal record: {fuori[:60]!r}")
    try:
        t = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        return None, g + [f"json non valido: {e}"]
    return t, g


def valida_traccia(t: dict) -> list[str]:
    g: list[str] = []
    extra = sorted(set(t) - set(CAMPI))
    for k in extra:
        g.append(f"campo NON ammesso nel record: {k!r} "
                 "(il vocabolario e' chiuso; la conclusione e' esclusa)")
    for k in CAMPI:
        if k not in t:
            g.append(f"campo mancante: {k}")
            continue
        v, amm = t[k], CAMPI[k]
        if k == "item_id":
            if not isinstance(v, int) or isinstance(v, bool):
                g.append("item_id: deve essere un intero")
        elif k in MULTIPLI:
            if not isinstance(v, list):
                g.append(f"{k}: deve essere una lista")
            else:
                for x in v:
                    if x not in amm:
                        g.append(f"{k}: {x!r} fuori dal vocabolario")
        elif v not in amm:
            g.append(f"{k}: {v!r} fuori dal vocabolario")
    return g


def a_ecc(t: dict, item: int, target: list[str]) -> dict:
    ts = "2026-10-07T00:00:00.000Z"
    return {
        "schema": "ecc.memory.v1",
        "id": f"mem_r3-trace-item-{item:02d}",
        "title": f"R3 trace, item {item} — disposizione, non conclusione",
        "kind": "handoff",
        "scope": "project",
        "trust": "unreviewed",
        "status": "active",
        "sourceHarness": "claude-code",
        "targetHarnesses": target,
        "tags": ["r3", "traccia", "vocabolario-chiuso"],
        "links": [],
        "createdAt": ts,
        "updatedAt": ts,
        "body": corpo_da_traccia(t),
    }


def controlla_documento(doc: dict) -> list[str]:
    """Conforme al loro schema E alla nostra regola sul body."""
    sys.path.insert(0, str(QUI))
    import valida_ecc
    g = list(valida_ecc.valida(doc))
    t, gb = traccia_da_corpo(doc.get("body", ""))
    g += gb
    if t is not None:
        g += valida_traccia(t)
    return g


def self_test() -> int:
    buona = {"item_id": 3, "evidence_used": "dato_primario",
             "uncertainty_boundary": ["grandezza_mancante"],
             "contradiction_policy": "contraddetta",
             "alternatives_retained": 2, "confidence": "media"}
    casi: list[tuple[str, dict, bool]] = [
        ("traccia conforme", a_ecc(buona, 3, ["codex"]), True),
    ]

    d = a_ecc(buona, 4, ["codex"])
    d["body"] += "\n\nConclusione: la causa e' il fornitore."
    casi.append(("prosa aggiunta dopo il record", d, False))

    d = a_ecc({**buona, "conclusione": "il fornitore"}, 5, ["codex"])
    casi.append(("campo conclusione nel record", d, False))

    d = a_ecc({**buona, "confidence": "certissima"}, 6, ["codex"])
    casi.append(("valore fuori vocabolario", d, False))

    d = a_ecc({k: v for k, v in buona.items() if k != "confidence"}, 7, ["codex"])
    casi.append(("campo mancante", d, False))

    d = a_ecc(buona, 8, ["codex"])
    d["body"] = "Ho concluso che il fornitore e' in ritardo."
    casi.append(("body di sola prosa", d, False))

    d = a_ecc(buona, 9, ["codex"])
    d["trust"] = "verified"
    casi.append(("trust alterato (regola loro)", d, False))

    d = a_ecc(buona, 10, [])
    casi.append(("nessun destinatario (regola loro)", d, False))

    ok = True
    for nome, doc, atteso in casi:
        g = controlla_documento(doc)
        passa = not g
        if passa != atteso:
            ok = False
        print(f"  {nome:34s} {'accettato' if passa else 'respinto':10s} "
              f"{'OK' if passa == atteso else 'NO ' + str(g[:1])}")
    print("  esito:", "OK" if ok else "CONTROLLO INAFFIDABILE")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--traccia", type=Path)
    ap.add_argument("--item", type=int, default=1)
    ap.add_argument("--target", default="codex")
    ap.add_argument("--out", type=Path, default=QUI / "uscita")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.traccia:
        ap.error("serve --traccia")
    t = json.loads(a.traccia.read_text(encoding="utf-8"))
    g = valida_traccia(t)
    if g:
        print("TRACCIA NON CONFORME:", file=sys.stderr)
        for x in g:
            print(f"  - {x}", file=sys.stderr)
        return 2
    doc = a_ecc(t, a.item, [s.strip() for s in a.target.split(",") if s.strip()])
    g = controlla_documento(doc)
    if g:
        print("DOCUMENTO NON CONFORME:", file=sys.stderr)
        for x in g:
            print(f"  - {x}", file=sys.stderr)
        return 3
    a.out.mkdir(parents=True, exist_ok=True)
    f = a.out / f"{doc['id']}.json"
    f.write_text(json.dumps(doc, indent=2, sort_keys=True,
                            ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"scritto {f}")
    print(f"  destinatari: {doc['targetHarnesses']}")
    print(f"  trust: {doc['trust']}   kind: {doc['kind']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
