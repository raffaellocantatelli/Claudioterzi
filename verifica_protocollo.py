#!/usr/bin/env python3
"""Verifica che il Protocollo Rosso Rosso Rosso tenga davvero in questo repo.

Il protocollo non si autocertifica: sarebbe auto-conferma, cioe' P5 violato
dal protocollo che lo enuncia. Questo script e' la contro-forza (P6) resa
eseguibile — fallisce rumorosamente se la disciplina decade.

Uso:
    python3 verifica_protocollo.py          # rapporto leggibile
    python3 verifica_protocollo.py --quiet   # solo exit code

Exit code 0 = invarianti rispettati. Diverso da 0 = numero di violazioni.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parent

ETICHETTE = ("RECUPERATO", "INFERITO", "IPOTESI", "UNKNOWN")

# Documenti canonici: senza questi il protocollo non e' trasportabile.
CANONICI = ("PROTOCOLLO_ROSSO.md", "RICOSTRUZIONE_R3.md", "baseline_r3.json")

# Documenti che affermano fatti sul mondo e devono quindi etichettarli.
ANALISI = ("RICOSTRUZIONE_R3.md", "SOLUZIONE_2055.md")

# Un'ipotesi dichiarata deve avere il proprio criterio di falsificazione
# entro questo numero di righe: P6 non ammette ipotesi non falsificabili.
FINESTRA_FALSIFICAZIONE = 12

# H1, HR1, H2055-A: sigla che inizia per H, contiene cifre, con suffisso
# facoltativo. Una regex piu' stretta lascerebbe fuori le ipotesi con
# suffisso letterale, che sono proprio quelle da controllare.
_RE_IPOTESI = re.compile(r"^\*\*(H[A-Z]*\d+[\w-]*)\*\*", re.MULTILINE)
_RE_FALSIF = re.compile(r"falsificat[ao]\s+se|criterio_falsificazione", re.IGNORECASE)


class Esito:
    def __init__(self) -> None:
        self.violazioni: list[str] = []
        self.controlli: list[tuple[str, bool, str]] = []

    def controlla(self, nome: str, ok: bool, dettaglio: str = "") -> None:
        self.controlli.append((nome, ok, dettaglio))
        if not ok:
            self.violazioni.append(f"{nome}: {dettaglio}" if dettaglio else nome)


def _leggi(nome: str) -> str | None:
    p = RADICE / nome
    try:
        return p.read_text(encoding="utf-8")
    except (FileNotFoundError, IsADirectoryError):
        return None


def verifica_canonici(e: Esito) -> None:
    """I documenti senza cui il protocollo non sopravvive a questo repo."""
    for nome in CANONICI:
        e.controlla(f"documento canonico {nome}",
                    (RADICE / nome).is_file(),
                    "assente")


def verifica_etichette(e: Esito) -> None:
    """Un documento che afferma fatti deve marcarne lo stato epistemico."""
    for nome in ANALISI:
        testo = _leggi(nome)
        if testo is None:
            e.controlla(f"etichette in {nome}", False, "file assente")
            continue
        presenti = [x for x in ETICHETTE if x in testo]
        e.controlla(
            f"etichette in {nome}",
            len(presenti) >= 3,
            f"trovate solo {presenti or 'nessuna'} — servono almeno 3 delle 4",
        )


def verifica_falsificabilita(e: Esito) -> None:
    """P6: ogni ipotesi dichiarata dichiara anche come cadrebbe."""
    for percorso in sorted(RADICE.glob("*.md")):
        testo = percorso.read_text(encoding="utf-8")
        righe = testo.splitlines()
        trovate = list(_RE_IPOTESI.finditer(testo))
        for i, m in enumerate(trovate):
            etichetta = m.group(1)
            n_riga = testo[: m.start()].count("\n")

            # La finestra si ferma all'ipotesi successiva. Senza questo taglio
            # un'ipotesi priva di criterio erediterebbe quello della vicina, e
            # il controllo rassicurerebbe a torto — verificato con un test
            # negativo che prima passava.
            fine = n_riga + FINESTRA_FALSIFICAZIONE
            if i + 1 < len(trovate):
                fine = min(fine, testo[: trovate[i + 1].start()].count("\n"))

            finestra = "\n".join(righe[n_riga:fine])
            e.controlla(
                f"P6 su {etichetta} ({percorso.name})",
                bool(_RE_FALSIF.search(finestra)),
                "nessun criterio di falsificazione entro "
                f"{FINESTRA_FALSIFICAZIONE} righe",
            )


def verifica_blocco_portabile(e: Esito) -> None:
    """Il protocollo deve restare trasportabile fuori da questo repo."""
    testo = _leggi("PROTOCOLLO_ROSSO.md")
    if testo is None:
        e.controlla("blocco portabile", False, "PROTOCOLLO_ROSSO.md assente")
        return
    e.controlla(
        "blocco portabile",
        "PROTOCOLLO ROSSO ROSSO ROSSO — attenzione totale." in testo,
        "il blocco da incollare altrove non e' piu' presente",
    )
    e.controlla(
        "P5 e P6 enunciati",
        "P5" in testo and "P6" in testo,
        "i due principi non sono entrambi enunciati",
    )


def main(argv: list[str]) -> int:
    quiet = "--quiet" in argv
    e = Esito()

    verifica_canonici(e)
    verifica_etichette(e)
    verifica_falsificabilita(e)
    verifica_blocco_portabile(e)

    if not quiet:
        print("PROTOCOLLO ROSSO ROSSO ROSSO — verifica invarianti")
        print("=" * 52)
        for nome, ok, dettaglio in e.controlli:
            segno = "ok  " if ok else "FAIL"
            riga = f"[{segno}] {nome}"
            if not ok and dettaglio:
                riga += f"\n         {dettaglio}"
            print(riga)
        print("=" * 52)
        totale = len(e.controlli)
        passati = totale - len(e.violazioni)
        if e.violazioni:
            print(f"{passati}/{totale} — la disciplina e' decaduta in "
                  f"{len(e.violazioni)} punt{'o' if len(e.violazioni) == 1 else 'i'}.")
        else:
            print(f"{passati}/{totale} — invarianti rispettati.")

    return len(e.violazioni)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
