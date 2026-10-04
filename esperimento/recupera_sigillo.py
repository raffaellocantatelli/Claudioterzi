#!/usr/bin/env python3
"""Cerca la ricetta di byte che riproduce un hash sigillato.

Ritrovare il testo non basta: il sigillo copre dei *byte*. Un testo copiato da
un'interfaccia di chat perde o aggiunge quasi sempre qualcosa — il newline
finale, i ritorni a capo CRLF, uno spazio in coda, un BOM — e un solo byte di
differenza produce un hash completamente diverso.

Questo strumento prova sistematicamente lo spazio delle varianti plausibili e
dice quale ricetta, se esiste, riproduce l'hash. Non stampa mai il contenuto
dei file: solo hash e nome della ricetta.

    python3 recupera_sigillo.py --atteso <sha256> file1 [file2 ...]
    python3 recupera_sigillo.py --self-test

Chiude BLOCKER-CUSTODY-02 solo un esito POSITIVO. Un esito negativo significa
che quei byte non sono stati ricostruiti, non che il testo e' sbagliato.

Stdlib only.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import sys
from pathlib import Path

# Normalizzazioni applicate a ciascun file, da sole e combinate.
NORMALIZZAZIONI = {
    "esatto":            lambda b: b,
    "crlf_a_lf":         lambda b: b.replace(b"\r\n", b"\n"),
    "lf_a_crlf":         lambda b: b.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"),
    "senza_bom":         lambda b: b[3:] if b.startswith(b"\xef\xbb\xbf") else b,
    "con_bom":           lambda b: b if b.startswith(b"\xef\xbb\xbf") else b"\xef\xbb\xbf" + b,
    "spazi_in_coda_via": lambda b: b"\n".join(l.rstrip() for l in b.split(b"\n")),
    "senza_nl_finale":   lambda b: b.rstrip(b"\n").rstrip(b"\r\n"),
    "con_nl_finale":     lambda b: b if b.endswith(b"\n") else b + b"\n",
}

# Separatori provati fra due o piu' file concatenati.
SEPARATORI = {
    "niente":      b"",
    "nl":          b"\n",
    "nl_doppio":   b"\n\n",
    "regola":      b"\n---\n\n",
    "regola_nl":   b"\n\n---\n\n",
}


def varianti(b: bytes):
    """Genera (nome_ricetta, byte) per ogni normalizzazione, sola e in coppia."""
    visti = set()
    nomi = list(NORMALIZZAZIONI)
    for n in range(1, 3):
        for combo in itertools.permutations(nomi, n):
            out = b
            for nome in combo:
                out = NORMALIZZAZIONI[nome](out)
            if out in visti:
                continue
            visti.add(out)
            yield "+".join(combo), out


def cerca(atteso: str, percorsi: list[Path]) -> tuple[str, str] | None:
    grezzi = [p.read_bytes() for p in percorsi]
    tentativi = 0

    if len(grezzi) == 1:
        for nome, b in varianti(grezzi[0]):
            tentativi += 1
            if hashlib.sha256(b).hexdigest() == atteso:
                return nome, f"{tentativi} tentativi"
        return None

    # piu' file: ogni ordine, ogni separatore, ogni normalizzazione per file,
    # piu' una normalizzazione finale sul concatenato
    indici = range(len(grezzi))
    for ordine in itertools.permutations(indici):
        for sep_nome, sep in SEPARATORI.items():
            pezzi_varianti = [list(varianti(grezzi[i])) for i in ordine]
            for scelte in itertools.product(*pezzi_varianti):
                unito = sep.join(b for _, b in scelte)
                for finale, b in varianti(unito):
                    tentativi += 1
                    if hashlib.sha256(b).hexdigest() == atteso:
                        ricetta = (
                            f"ordine={[percorsi[i].name for i in ordine]} "
                            f"separatore={sep_nome} "
                            f"per_file={[n for n, _ in scelte]} "
                            f"finale={finale}"
                        )
                        return ricetta, f"{tentativi} tentativi"
    return None


def self_test() -> int:
    """Costruisce un caso con ricetta nota e verifica che venga ritrovata.

    Senza questo, uno strumento che non trova mai niente e' indistinguibile da
    uno rotto.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        a, b = td / "a.txt", td / "b.txt"
        a.write_bytes(b"placebo finto\r\nriga due\r\n")
        b.write_bytes(b"item finti\n")
        # ricetta nota: b prima di a, separatore doppio newline, CRLF -> LF
        atteso_byte = b"item finti\n" + b"\n\n" + b"placebo finto\nriga due\n"
        atteso = hashlib.sha256(atteso_byte).hexdigest()

        trovato = cerca(atteso, [a, b])
        ok_pos = trovato is not None
        print(f"  ricetta nota ritrovata : {'si' if ok_pos else 'NO'}")
        if ok_pos:
            print(f"    -> {trovato[0]}")

        # controprova: un hash inventato non deve mai risultare trovato
        falso = "0" * 64
        ok_neg = cerca(falso, [a, b]) is None
        print(f"  hash inesistente respinto: {'si' if ok_neg else 'NO'}")

    ok = ok_pos and ok_neg
    print("  esito:", "OK" if ok else "STRUMENTO INAFFIDABILE")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--atteso", help="sha256 da riprodurre")
    ap.add_argument("file", nargs="*", type=Path)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)

    if a.self_test:
        return self_test()
    if not a.atteso or not a.file:
        ap.error("servono --atteso e almeno un file")
    for p in a.file:
        if not p.is_file():
            raise SystemExit(f"manca: {p}")
    if len(a.file) > 3:
        raise SystemExit("piu' di tre file: lo spazio delle ricette esplode. "
                         "Concatenali prima come ricordi di averli avuti.")

    esito = cerca(a.atteso.strip().lower(), a.file)
    if esito is None:
        print("NESSUNA RICETTA riproduce l'hash atteso.")
        print("Non significa che il testo sia sbagliato: significa che questi "
              "byte,\nin nessuna delle varianti provate, non sono quelli "
              "sigillati.")
        print("BLOCKER-CUSTODY-02 resta APERTO.")
        return 1

    ricetta, quanti = esito
    print("TROVATA.")
    print(f"  ricetta  : {ricetta}")
    print(f"  provati  : {quanti}")
    print(f"  sha256   : {a.atteso.strip().lower()}")
    print("\nRicostruisci i byte con quella ricetta, cifrali, committali e "
          "verifica\nil round-trip. Solo allora BLOCKER-CUSTODY-02 e' chiuso.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
