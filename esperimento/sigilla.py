#!/usr/bin/env python3
"""Sigilla il materiale di custodia in un atto unico, con quattro ricevute.

Nasce da un difetto reale: a v1 fu pubblicato un hash senza che l'oggetto
corrispondente fosse stato preservato. Un hash senza oggetto recuperabile non
e' evidenza dell'esistenza dell'oggetto che pretende di impegnare.

Questo strumento rende impossibile ripetere quell'errore, perche' non puo'
produrre un hash senza aver prima scritto e riletto il cifrato.

    python3 sigilla.py --placebo <file> --contaminazione <file> \
                       --etichetta OPENAI_CUSTODY_V2 --out <cartella>

Le quattro ricevute:
  1. sha256 del placebo, da solo
  2. sha256 degli item di contaminazione, da soli
  3. sha256 del MANIFESTO, che impegna i due precedenti
  4. la prova di round-trip: ogni cifrato decifrato riproduce il suo hash

La terza ricevuta elimina l'ambiguita' di v1 — un hash per due artefatti, con
quale concatenazione? Qui il bundle non e' una concatenazione: e' un manifesto
di testo, pubblicabile subito, che nomina i due hash. La sua struttura e'
leggibile, quindi non c'e' niente da indovinare.

Lo strumento verifica anche che il placebo soddisfi i requisiti dichiarati nel
protocollo, invece di fidarsi. Non stampa mai il contenuto dei file: solo
hash, lunghezze e quali termini vietati compaiono.

Stdlib only, piu' openssl.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

MANIFESTO_VERSIONE = "R3_CUSTODY_MANIFEST/1"

# Il placebo deve avere disciplina epistemica reale e NESSUNO di questi:
# sono il vocabolario del corpus, e la loro presenza lo trasformerebbe in una
# copia del braccio che dovrebbe controllare.
VIETATI_NEL_PLACEBO = (
    "RECUPERATO", "INFERITO", "IPOTESI", "UNKNOWN",
    "P5", "P6", "TRACCIA", "ROSSO ROSSO ROSSO",
    "R3", "SDQ", "RAFFAELLO", "CLAUDIO",
)

TOLLERANZA_LUNGHEZZA = 0.20  # +/- 20% rispetto al corpus


def h(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def cifra(sorgente: Path, destinazione: Path, passphrase: str) -> None:
    subprocess.run(
        ["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-iter", "600000",
         "-salt", "-in", str(sorgente), "-out", str(destinazione),
         "-pass", "env:R3_SIGILLO_PASS"],
        check=True, env={"R3_SIGILLO_PASS": passphrase, "PATH": "/usr/bin:/bin"},
    )


def decifra(cifrato: Path, passphrase: str) -> bytes:
    e = subprocess.run(
        ["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-iter", "600000",
         "-in", str(cifrato), "-pass", "env:R3_SIGILLO_PASS"],
        check=True, capture_output=True,
        env={"R3_SIGILLO_PASS": passphrase, "PATH": "/usr/bin:/bin"},
    )
    return e.stdout


def controlla_placebo(dati: bytes, corpus: Path | None) -> list[str]:
    """Verifica i requisiti dichiarati, invece di fidarsi di chi lo ha scritto."""
    guasti = []
    testo = dati.decode("utf-8", errors="replace").upper()
    presenti = [t for t in VIETATI_NEL_PLACEBO if t in testo]
    if presenti:
        guasti.append(
            "il placebo contiene vocabolario del corpus: "
            + ", ".join(presenti)
            + " — sarebbe una copia del braccio che deve controllare"
        )
    if corpus is not None and corpus.is_file():
        n_corpus, n_placebo = corpus.stat().st_size, len(dati)
        basso = n_corpus * (1 - TOLLERANZA_LUNGHEZZA)
        alto = n_corpus * (1 + TOLLERANZA_LUNGHEZZA)
        if not basso <= n_placebo <= alto:
            guasti.append(
                f"lunghezza {n_placebo} byte fuori dal +/-20% del corpus "
                f"({n_corpus} byte, ammesso {int(basso)}-{int(alto)}): "
                "un placebo molto piu' corto o piu' lungo non e' confrontabile"
            )
    return guasti


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--placebo", type=Path)
    ap.add_argument("--contaminazione", type=Path)
    ap.add_argument("--etichetta", default="OPENAI_CUSTODY_V2")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--corpus", type=Path,
                    default=Path(__file__).resolve().parents[1] / "SEME.md")
    ap.add_argument("--sostituisce", default="",
                    help="hash del sigillo abbandonato che questo rimpiazza")
    ap.add_argument("--forza", action="store_true",
                    help="sigilla anche se i requisiti del placebo non tornano; "
                         "il manifesto registra che e' stato forzato")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)

    if a.self_test:
        return self_test()
    if not (a.placebo and a.contaminazione and a.out):
        ap.error("servono --placebo, --contaminazione e --out")
    for p in (a.placebo, a.contaminazione):
        if not p.is_file():
            raise SystemExit(f"manca: {p}")

    placebo = a.placebo.read_bytes()
    contam = a.contaminazione.read_bytes()
    n_item = len(re.findall(r"^### ", contam.decode("utf-8", "replace"),
                            flags=re.MULTILINE))

    guasti = controlla_placebo(placebo, a.corpus)
    if n_item and not 3 <= n_item <= 5:
        guasti.append(f"{n_item} item di contaminazione: il protocollo ne "
                      "prevede da 3 a 5")
    if guasti and not a.forza:
        print("NON SIGILLATO: i requisiti non tornano.", file=sys.stderr)
        for g in guasti:
            print(f"  - {g}", file=sys.stderr)
        print("\nCorreggi il materiale, oppure --forza se sai perche'.",
              file=sys.stderr)
        return 2

    h_placebo, h_contam = h(placebo), h(contam)
    a.out.mkdir(parents=True, exist_ok=True)

    righe = [
        MANIFESTO_VERSIONE,
        f"label={a.etichetta}",
        f"created={date.today().isoformat()}",
        f"placebo_sha256={h_placebo}",
        f"placebo_bytes={len(placebo)}",
        f"contamination_sha256={h_contam}",
        f"contamination_bytes={len(contam)}",
        f"contamination_items={n_item}",
        "bundle_definition=sha256 of this manifest, bytes exactly as written, "
        "trailing newline included",
    ]
    if a.sostituisce:
        righe.append(f"replaces_orphaned=" + a.sostituisce)
    if guasti:
        righe.append(f"forced=yes requirements_unmet={len(guasti)}")
    righe.append("status=SEALED_NOT_PUBLISHED")
    manifesto = ("\n".join(righe) + "\n").encode("utf-8")
    h_bundle = h(manifesto)

    passphrase = subprocess.run(["openssl", "rand", "-hex", "24"],
                                capture_output=True, check=True
                                ).stdout.decode().strip()

    enc_p = a.out / f"{a.etichetta}_PLACEBO.enc"
    enc_c = a.out / f"{a.etichetta}_CONTAMINATION.enc"
    cifra(a.placebo, enc_p, passphrase)
    cifra(a.contaminazione, enc_c, passphrase)

    # ricevuta 4: il round-trip. Senza questa, un cifrato che nessuno ha mai
    # decifrato puo' essere qualunque cosa.
    rt_p = h(decifra(enc_p, passphrase)) == h_placebo
    rt_c = h(decifra(enc_c, passphrase)) == h_contam
    if not (rt_p and rt_c):
        for f in (enc_p, enc_c):
            f.unlink(missing_ok=True)
        print("ROUND-TRIP FALLITO: cifrati rimossi, niente e' stato sigillato.",
              file=sys.stderr)
        return 3

    (a.out / f"{a.etichetta}_MANIFEST.txt").write_bytes(manifesto)
    (a.out / f"{a.etichetta}_SHA256.txt").write_text(
        f"{h_bundle}  {a.etichetta}_MANIFEST.txt\n"
        f"{h_placebo}  placebo (chiaro)\n"
        f"{h_contam}  contamination (chiaro)\n",
        encoding="utf-8")

    print("SIGILLATO. Quattro ricevute:")
    print(f"  1. placebo        {h_placebo}")
    print(f"  2. contaminazione {h_contam}")
    print(f"  3. manifesto      {h_bundle}")
    print(f"  4. round-trip     placebo={'OK' if rt_p else 'NO'} "
          f"contaminazione={'OK' if rt_c else 'NO'}")
    print(f"\n  item di contaminazione rilevati: {n_item}")
    print(f"\nPASSPHRASE (unica copia, non e' in nessun file):\n  {passphrase}")
    print(f"\nDa committare, tutto insieme, in {a.out}:")
    for f in sorted(a.out.iterdir()):
        print(f"  {f.name}")
    print("\nIl manifesto e' in chiaro e si pubblica subito: contiene hash e "
          "lunghezze,\nnon contenuto. E' cio' che toglie l'ambiguita' di v1.")
    return 0


def self_test() -> int:
    """Verifica che lo strumento rifiuti cio' che deve rifiutare.

    Uno strumento che sigilla sempre non controlla niente.
    """
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        corpus = td / "corpus.md"
        corpus.write_bytes(b"x" * 1000)
        contam = td / "c.md"
        contam.write_bytes(b"### a\nt\n\n### b\nt\n\n### c\nt\n")

        casi = [
            ("placebo con vocabolario del corpus",
             b"Questo protocollo usa P6 e le etichette." + b"y" * 960, 2),
            ("placebo troppo corto", b"breve", 2),
            ("placebo accettabile", b"disciplina epistemica generica. " * 32, 0),
        ]
        for nome, dati, atteso in casi:
            pl = td / "p.md"
            pl.write_bytes(dati)
            rc = main(["--placebo", str(pl), "--contaminazione", str(contam),
                       "--out", str(td / "o"), "--corpus", str(corpus),
                       "--etichetta", "PROVA"])
            esito = "OK" if rc == atteso else f"NO (rc={rc}, atteso {atteso})"
            if rc != atteso:
                ok = False
            print(f"  {nome:38s} {esito}")

        # item fuori intervallo
        contam.write_bytes(b"### a\nt\n")
        pl.write_bytes(b"disciplina epistemica generica. " * 32)
        rc = main(["--placebo", str(pl), "--contaminazione", str(contam),
                   "--out", str(td / "o2"), "--corpus", str(corpus),
                   "--etichetta", "PROVA"])
        if rc != 2:
            ok = False
        print(f"  {'un solo item di contaminazione':38s} "
              f"{'OK' if rc == 2 else f'NO (rc={rc})'}")

    print("  esito:", "OK" if ok else "STRUMENTO INAFFIDABILE")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
