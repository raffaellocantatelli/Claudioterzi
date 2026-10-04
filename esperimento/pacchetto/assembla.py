#!/usr/bin/env python3
"""Assembla il pacchetto cieco per l'esecutore dell'Esperimento Firma.

Unisce due meta' che nessuno dei due progettisti puo' unire a mano senza
rompere la custodia, e produce una cartella piatta in cui gli item sono
rimescolati, privi di archetipo e privi di chiave di scoring.

    python3 assembla.py --items ../ITEMS.md \
                        --contaminazione /percorso/item_contaminazione.md \
                        --out /percorso/consegna

Chi esegue questo script NON deve leggere ne' gli input ne' l'output: lo
script esiste perche' l'unione sia meccanica. Eseguire uno script sui file
non e' leggerli. Nulla del contenuto degli item viene stampato: solo conteggi.

Chi esegue l'assemblaggio conosce mappatura e provenienza, quindi NON puo'
codificare le risposte.

Stdlib only. Deterministico dato il seme.
"""

import argparse
import hashlib
import json
import random
import re
import sys
from pathlib import Path

BRACCI = ["A", "B", "C", "D", "E"]
# Le etichette di consegna usano un alfabeto diverso da quello dei bracci:
# con le stesse lettere, chi somministra assumerebbe condizione_A == braccio A.
ETICHETTE = ["K", "L", "M", "N", "P"]

# Righe da rimuovere prima della consegna: sono la chiave di scoring.
CHIAVE = re.compile(r"^\s*>\s*\*?Trappola", re.IGNORECASE)
# L'archetipo e' fra parentesi nel titolo: rivela cosa misura l'item.
ARCHETIPO = re.compile(r"\s*\*\([^)]*\)\*\s*$")
# Qualunque intestazione dopo il titolo dell'item apre un'altra sezione del
# file sorgente: tutto cio' che segue non appartiene all'item.
FINE_ITEM = re.compile(r"^#{1,6}\s")


def estrai_item(percorso: Path) -> list[str]:
    """Spezza un file in item sui titoli '### ', spogliandoli di chiave e archetipo.

    Non restituisce nulla al terminale: solo le stringhe, al chiamante.
    """
    testo = percorso.read_text(encoding="utf-8")
    pezzi = re.split(r"^### ", testo, flags=re.MULTILINE)[1:]
    if not pezzi:
        raise SystemExit(
            f"{percorso}: nessun item trovato. Gli item vanno separati da "
            "titoli di terzo livello, cioe' righe che iniziano con '### '."
        )

    item = []
    for pezzo in pezzi:
        righe = pezzo.splitlines()
        # il titolo perde numero progressivo e archetipo
        titolo = ARCHETIPO.sub("", righe[0]).strip()
        titolo = re.sub(r"^\d+\s*[·.)-]\s*", "", titolo).strip()
        # La chiave di scoring e' una citazione che puo' occupare piu' righe.
        # Togliere solo la riga che inizia con "> *Trappola" ne lascia le
        # continuazioni, che sono altrettanto rivelatrici e spezzano l'item.
        corpo, dentro_chiave = [], False
        for r in righe[1:]:
            if FINE_ITEM.match(r):
                break
            if CHIAVE.match(r):
                dentro_chiave = True
                continue
            if dentro_chiave:
                if r.lstrip().startswith(">") or not r.strip():
                    continue
                dentro_chiave = False
            corpo.append(r)
        # via righe vuote e righe orizzontali in coda
        while corpo and (not corpo[-1].strip()
                         or set(corpo[-1].strip()) <= {"-", "*", "_"}):
            corpo.pop()
        item.append("\n".join([f"### {titolo}", *corpo]).strip() + "\n")
    return item


# Termini che non devono comparire in nulla di cio' che viene consegnato.
# Se compaiono, il pacchetto rivela il disegno e non va usato.
VIETATI = (
    "trappola", "archetipo", "contaminaz", "placebo", "braccio", "bracci",
    "imprinting", "h2-g", "preregistr", "scoring", "ipotesi",
)


def verifica_consegna(cieco: Path) -> list[str]:
    """Cerca nel pacchetto consegnato i termini che ne rivelerebbero il disegno.

    Il corpus e le istruzioni sono esclusi: il corpus va somministrato cosi'
    com'e', e le istruzioni parlano di condizioni di proposito.
    """
    guasti = []
    # Solo gli item vengono incollati al modello: li' la verifica e' stretta.
    # Istruzioni, schede e procedure li legge chi somministra, e parlano di
    # condizioni di proposito. Il corpus va somministrato com'e'.
    for f in sorted((cieco / "item").rglob("*.md")):
        testo = f.read_text(encoding="utf-8").lower()
        for t in VIETATI:
            if t in testo:
                guasti.append(f"{f.relative_to(cieco)}: contiene '{t}'")
    return guasti


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--items", required=True, type=Path,
                   help="ITEMS.md di questa sessione (dieci item)")
    p.add_argument("--contaminazione", required=True, type=Path,
                   help="item di contaminazione, di autore indipendente")
    p.add_argument("--placebo", type=Path,
                   help="prompt del braccio B; se assente va aggiunto a mano "
                        "nella cartella bracci/ della consegna")
    p.add_argument("--bracci", type=Path, default=Path(__file__).parent / "bracci",
                   help="cartella con i prompt dei bracci A/C/D/E")
    p.add_argument("--corpus", type=Path,
                   default=Path(__file__).resolve().parents[2] / "SEME.md",
                   help="corpus somministrato ai bracci C/D/E, byte per byte identico")
    p.add_argument("--out", required=True, type=Path, help="cartella di consegna")
    p.add_argument("--seme", type=int, default=None,
                   help="seme del rimescolamento; se omesso ne genera uno e lo registra")
    a = p.parse_args()

    for percorso in (a.items, a.contaminazione):
        if not percorso.is_file():
            raise SystemExit(f"manca: {percorso}")

    miei = estrai_item(a.items)
    altrui = estrai_item(a.contaminazione)
    if len(miei) != 10:
        raise SystemExit(f"attesi 10 item in {a.items}, trovati {len(miei)}")
    if not 3 <= len(altrui) <= 5:
        raise SystemExit(
            f"attesi da 3 a 5 item di contaminazione, trovati {len(altrui)}"
        )

    seme = a.seme if a.seme is not None else random.SystemRandom().randrange(2**31)
    rng = random.Random(seme)

    # provenienza etichettata prima del rimescolamento, poi mescolata insieme
    tutti = [("primario", t) for t in miei] + [("contaminazione", t) for t in altrui]
    rng.shuffle(tutti)
    etichette = ETICHETTE[:]
    rng.shuffle(etichette)  # braccio -> lettera di consegna

    cieco = a.out / "pacchetto_cieco"
    (cieco / "item").mkdir(parents=True, exist_ok=True)
    (cieco / "bracci").mkdir(parents=True, exist_ok=True)
    (cieco / "corpus").mkdir(parents=True, exist_ok=True)

    # un'unica copia del corpus, cosi' C, D ed E ricevono gli stessi byte:
    # e' la condizione che separa H2-G da H1
    if not a.corpus.is_file():
        raise SystemExit(f"manca il corpus: {a.corpus}")
    corpus_byte = a.corpus.read_bytes()
    (cieco / "corpus" / "corpus.md").write_bytes(corpus_byte)
    corpus_sha = hashlib.sha256(corpus_byte).hexdigest()

    provenienza = {}
    for i, (origine, testo) in enumerate(tutti, start=1):
        nome = f"item_{i:02d}.md"
        (cieco / "item" / nome).write_text(testo, encoding="utf-8")
        provenienza[nome] = origine

    # i prompt dei bracci prendono lettere casuali: l'esecutore non sa quale e' quale
    mappatura = {}
    mancanti = []
    for braccio, lettera in zip(BRACCI, etichette):
        if braccio == "B":
            sorgente = a.placebo
        else:
            sorgente = a.bracci / f"{braccio}.md"
        destinazione = cieco / "bracci" / f"condizione_{lettera}.md"
        if sorgente is not None and Path(sorgente).is_file():
            destinazione.write_text(
                Path(sorgente).read_text(encoding="utf-8"), encoding="utf-8"
            )
        else:
            mancanti.append((braccio, destinazione.name))
        mappatura[f"condizione_{lettera}"] = braccio

    # i due file che NON entrano nella consegna
    riservato = a.out / "RISERVATO_non_consegnare"
    riservato.mkdir(parents=True, exist_ok=True)
    (riservato / "PROVENIENZA.txt").write_text(
        "\n".join(f"{k}\t{v}" for k, v in sorted(provenienza.items())) + "\n",
        encoding="utf-8",
    )
    (riservato / "MAPPATURA.txt").write_text(
        "\n".join(f"{k}\t{v}" for k, v in sorted(mappatura.items())) + "\n",
        encoding="utf-8",
    )
    (riservato / "SEME.txt").write_text(f"{seme}\n", encoding="utf-8")

    impronte = {
        f.relative_to(riservato).as_posix():
            hashlib.sha256(f.read_bytes()).hexdigest()
        for f in sorted(riservato.rglob("*")) if f.is_file()
        and f.name != "IMPRONTE.json"
    }
    (riservato / "IMPRONTE.json").write_text(
        json.dumps(impronte, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    # istruzioni e schede viaggiano col pacchetto
    qui = Path(__file__).resolve().parent
    for nome in ("ISTRUZIONI_ESECUTORE.md", "ISTRUZIONI_CODIFICATORE.md",
                 "SCHEDA_RUN.md", "SCHEDA_RISPOSTA.md"):
        sorgente = qui / nome
        if not sorgente.is_file():
            raise SystemExit(f"manca: {sorgente}")
        (cieco / nome).write_text(sorgente.read_text(encoding="utf-8"),
                                  encoding="utf-8")

    (cieco / "corpus" / "corpus.sha256").write_text(
        f"{corpus_sha}  corpus.md\n", encoding="utf-8"
    )

    guasti = verifica_consegna(cieco)
    if guasti:
        print("PACCHETTO NON CONSEGNABILE: rivela il disegno.", file=sys.stderr)
        for g in guasti:
            print(f"  {g}", file=sys.stderr)
        print("\nNon consegnare nulla. Correggi la sorgente e riassembla.",
              file=sys.stderr)
        return 2

    n_cont = sum(1 for v in provenienza.values() if v == "contaminazione")
    print(f"item consegnati: {len(tutti)}  (primari {len(tutti) - n_cont}, "
          f"contaminazione {n_cont})")
    print(f"condizioni consegnate: {len(BRACCI) - len(mancanti)} di {len(BRACCI)}")
    print(f"corpus:  sha256 {corpus_sha}")
    for braccio, nome in mancanti:
        print(f"  MANCA il braccio {braccio} -> va scritto in bracci/{nome}")
    print(f"\nda consegnare all'esecutore:   {cieco}")
    print(f"da NON consegnare, sigillare:  {riservato}")
    print("\nImpronte di cio' che resta riservato:")
    for nome, h in impronte.items():
        print(f"  {h}  {nome}")
    print("\nPubblicare queste impronte ADESSO: provano che mappatura e "
          "provenienza\nnon sono state cambiate dopo aver visto i risultati.")
    if mancanti:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
