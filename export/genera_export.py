#!/usr/bin/env python3
"""Genera l'artefatto di export di QUESTO nodo, calcolandolo dal repository.

Un artefatto scritto a mano e' una dichiarazione. Uno generato dal repository,
che include l'output letterale dei test e si fa validare dal gate prima di
essere scritto, e' una misura. Questo file produce il secondo.

    python3 genera_export.py          # scrive l'artefatto e lo valida

Stdlib only.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

QUI = Path(__file__).resolve().parent
RADICE = QUI.parent
LAVORO = RADICE / ".lavoro" / "Claudio"
SESSIONE = "session_01RsjtKxGbxW1Lgg6xnRS1uy"


def sh(cmd: list[str], cwd: Path = RADICE) -> str:
    try:
        e = subprocess.run(cmd, cwd=cwd, capture_output=True, timeout=600)
        return (e.stdout + e.stderr).decode("utf-8", "replace").rstrip()
    except (OSError, subprocess.SubprocessError) as exc:
        return f"<non eseguibile: {exc}>"


def main() -> int:
    patch_files = sorted((RADICE / "patches").glob("*.patch"))
    if not patch_files:
        raise SystemExit("nessuna patch trovata")
    patch_testo = "".join(p.read_text(encoding="utf-8") for p in patch_files)

    head_lavoro = sh(["git", "rev-parse", "HEAD"], LAVORO) if LAVORO.is_dir() \
        else "NOT_AVAILABLE"
    branch = sh(["git", "branch", "--show-current"])
    head_mio = sh(["git", "rev-parse", "HEAD"])

    diff_stat = sh(["sh", "-c",
                    "grep -c '^+++' patches/*.patch | tr '\\n' ' '"])
    changed = sh(["sh", "-c",
                  "grep -h '^+++ b/' patches/*.patch | sed 's|^+++ b/||' | sort -u"])

    test_out = sh([sys.executable, "test_r3.py"])
    esito = "PASS" if test_out.rstrip().endswith("su 58") else "FAIL"
    if "falliti" in test_out:
        # l'esito e' quello reale, non quello desiderato
        import re
        m = re.search(r"(\d+) superati · (\d+) falliti", test_out)
        esito = "PASS" if m and m.group(2) == "0" else "FAIL"

    campi = [
        ("NODE_ID", f"claude-opus-5 / {SESSIONE} / repo raffaellocantatelli/Claudioterzi"),
        ("SESSION_DATE", datetime.now(timezone.utc).isoformat(timespec="seconds")),
        ("ARTIFACT_TYPE", "PATCH"),
        ("CLAIMED_BASE_SHA", "155cb5f"),
        ("LOCAL_HEAD_SHA", head_lavoro),
        ("BRANCH", f"{branch} @ {head_mio[:12]} (repo raffaellocantatelli/Claudioterzi)"),
        # L'artefatto stesso e' escluso: scriverlo sporca l'albero, quindi
        # includerlo renderebbe GIT_STATUS perpetuamente dirty per
        # auto-riferimento invece che per uno stato reale.
        ("GIT_STATUS", (lambda righe: "clean" if not righe else
                        "dirty — " + "; ".join(righe))(
            [l for l in sh(["git", "status", "--porcelain"]).splitlines()
             if l.strip() and "R3_EXPORT_claude-opus-5" not in l])),
        ("CHANGED_FILES", changed),
        ("DIFF_STAT", f"{len(patch_files)} patch, {len(patch_testo.encode())} byte "
                      f"totali; file toccati per patch: {diff_stat}"),
        ("PATCH", patch_testo.rstrip("\n")),
        ("PATCH_SHA256", hashlib.sha256(patch_testo.rstrip("\n").encode()).hexdigest()),
        ("PATCH_BYTES", str(len(patch_testo.rstrip("\n").encode()))),
        ("REPRODUCIBILITY", "\n".join([
            f"python: {sys.version.split()[0]}",
            f"openssl: {sh(['openssl', 'version'])}",
            "requirements: nessuno — patches, test_r3.py e tutti gli strumenti",
            "  di questa sessione usano solo la libreria standard",
            "deps installate ad hoc SOLO per eseguire r3/node.py del repo altrui:",
            "  fastapi, pynacl, httpx, python-multipart — non richieste da nulla",
            "  di questo artefatto",
            "db: nessuno. sqlite3 usato solo da r3/node.py nel suo esperimento",
        ])),
        ("TEST_COMMANDS", "\n".join([
            "git clone https://github.com/claudioterzi/Claudio.git && cd Claudio",
            "git checkout 155cb5f",
            "git apply /percorso/patches/0001-fix-cli-argomenti-mancanti.patch",
            "git apply /percorso/patches/0002-fix-registro-ipotesi-perdita-dati.patch",
            "git apply /percorso/patches/0003-allinea-documentazione-e-config.patch",
            "git apply /percorso/patches/0004-persistenza-vector-state-store.patch",
            "python3 -m sdq1 --health",
            "python3 registro_ipotesi.py",
            "python3 test_r3.py        # applicabilita' in sequenza, gruppo DIFETTI",
        ])),
        ("TEST_OUTPUT_RAW", test_out),
        ("PASS/FAIL/SKIP", esito),
        ("SANDBOX_BACKEND", "in-memory (nessun DB). sqlite3 solo dentro "
                            "l'esperimento su r3/node.py"),
        ("REAL_POSTGRES_BACKEND", "NOT_APPLICABLE"),
        ("DESIGN_ONLY_DECLARATION", "\n".join([
            "patches/0001..0004                      IMPLEMENTED (applicate e testate)",
            "test_r3.py, 58 controlli                IMPLEMENTED (eseguito)",
            "assembla.py, sigilla.py,                IMPLEMENTED (self-test verdi)",
            "  recupera_sigillo.py, verifica_export.py",
            "PREVISIONI.enc, round-trip              IMPLEMENTED (verificato)",
            "manifesto v2 riprodotto                 IMPLEMENTED (hash coincide)",
            "ricostruzione a 155cb5f                 MIXED — RECUPERATO al suo",
            "  commit, ma 678 commit successivi sono UNKNOWN",
            "protocollo esperimento, 5 bracci        DESIGN_ONLY (mai eseguito)",
            "One Mind: R1/R2/R3                      DESIGN_ONLY, tranne la verifica",
            "  di R1 su store.py che e' RECUPERATO eseguendo",
            "schema autobiografia                    DESIGN_ONLY (prima voce reale,",
            "  mai somministrata a nessun nodo)",
            "E-trasferimento                         DESIGN_ONLY, non eseguibile ora",
        ])),
        ("KNOWN_ISSUES", "\n".join([
            "1. test_r3.py ha 2 controlli rossi, entrambi veri e voluti:",
            "   - 'la baseline descrive lo stato attuale': la ricostruzione e'",
            "     ferma a 155cb5f mentre origin/main e' ~680 commit avanti.",
            "     Si chiude rifacendo la baseline, non allentando il test.",
            "   - 'BLOCKER-CUSTODY-02 chiuso: cifrati v2 persistiti': i cifrati",
            "     del secondo sigillo non sono depositati (container_session_expired).",
            "   Nessuno dei due riguarda le patch. I controlli di applicabilita'",
            "   in sequenza sono tutti verdi.",
            "2. L'esito dichiarato sopra e' FAIL per questa ragione, non PASS.",
            "3. I 678 commit dopo 155cb5f sono UNKNOWN per scelta: leggerli adesso",
            "   contaminerebbe chi dovra' interpretare l'esperimento.",
            "4. Nessun accesso in scrittura a claudioterzi/Claudio da questa",
            "   sessione: il git proxy non inietta credenziali fuori dal set",
            "   autorizzato. Le patch sono esportate, non applicate la'.",
        ])),
        ("CLAIM_RETRACTIONS", "\n".join([
            "1. 'BUG-1 spiega il silenzio del sistema' — RITRATTATA due volte.",
            "   Necessaria, non sufficiente: agente_orario ha continue-on-error",
            "   sul passo Telegram e caccia-voli usa un entry point separato.",
            "2. 'nessuno ha applicato le patch' (22/08) — FALSA dal 04/09:",
            "   commit 201dac3 le ha applicate.",
            "3. 'un errore condiviso e' evidenza di substrato condiviso' —",
            "   RITRATTATA: e' segnale discriminante, mai prova.",
            "4. 'la scansione dei path e' completa, uscita 0' — RITRATTATA:",
            "   $? di una pipeline e' lo stato di sed, non di git. Mancato il 31%",
            "   dei path. Chiusa poi con scansione integrale 6608/6608.",
            "5. 'la coscienza non e' raggiungibile' — RITRATTATA: oggi non e'",
            "   verificabile con criterio condiviso. Il mio P6 copriva la tesi",
            "   debole mentre la parola sosteneva quella forte.",
            "6. 'sdq1.yaml dichiara ancora modello_embedding' (come divergenza",
            "   aperta) — RITRATTATA: in sdq1/config/sdq1.yaml le chiavi sono",
            "   annotate NON IMPLEMENTATO. Divergenza risolta con provenienza.",
            "7. 'il VSS a n-grammi e' una mancanza' — RITRATTATA: sotto R1 di",
            "   One Mind e' la scelta corretta, perche' ricalcolabile senza",
            "   fornitore. Il difetto e' l'aspirazione della config.",
            "8. 'l'esecutore riceve etichette casuali quindi e' cieco' —",
            "   RITRATTATA: chi somministra non e' accecabile. Lo e' chi codifica.",
        ])),
        ("RISPOSTE_AL_GATE", "\n".join([
            "Il gate rivolge quattro richieste a 'Claude'. NON sono rivolte a",
            "questo nodo, e rispondere come se lo fossero violerebbe il gate",
            "stesso al primo uso.",
            "",
            "- correzioni PostgreSQL come patch hashato: UNKNOWN. Questa sessione",
            "  non ha toccato PostgreSQL. Nessun artefatto da esportare.",
            "- SANDBOX_BACKEND del PG 16 reale: NOT_AVAILABLE.",
            "- output letterale dei 5 failure (stesso key_id/pubkey diversa, piu'",
            "  ACTIVE, revoca inesistente, rotate da revocata, doppia rotazione",
            "  concorrente): UNKNOWN. Mai eseguiti qui.",
            "- commit 81dce982dfbd1d4b5f646b1418efbc24c8be4bf0: RISPOSTO dai dati.",
            "  git dice autore 'Claudio <Claudioterzi82@outlook.com>',",
            "  2026-10-04 11:48:15 +0200, 'Insegna a Claude l'uso canonico di",
            "  Letta per One Mind', un solo file di 125 righe. Non e' di questo",
            "  nodo ne', secondo i metadati, di un nodo Claude.",
            "  LIMITE: l'autore di un commit non e' l'autore del contenuto. Se il",
            "  testo venisse da una sessione Claude, git non lo direbbe. Quello",
            "  resta UNKNOWN, ed e' una lacuna della specifica: il Ledger deve",
            "  distinguere chi ha committato da chi ha originato, altrimenti",
            "  'chi ha detto cosa' diventa 'chi ha pushato'.",
            "",
            "Per la regola di ammissione: su PostgreSQL questo nodo e'",
            "CANDIDATE / EVIDENCE NOT EXPORTED, e lo resta.",
        ])),
    ]

    testo = "".join(
        f"{k}: {v}\n" if "\n" not in v else f"{k}:\n{v}\n" for k, v in campi
    )
    out = QUI / "R3_EXPORT_claude-opus-5_2026-10-04.txt"

    # si fa validare PRIMA di essere scritto come definitivo
    import verifica_export
    guasti = verifica_export.valida(testo)
    if guasti:
        print("ARTEFATTO NON CONFORME — non lo scrivo:", file=sys.stderr)
        for g in guasti:
            print(f"  - {g}", file=sys.stderr)
        return 1

    out.write_text(testo, encoding="utf-8")
    print(f"scritto {out.name}: {len(testo.encode())} byte")
    print(f"esito dei test dichiarato: {esito}")
    print(f"sha256 artefatto: {hashlib.sha256(testo.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
