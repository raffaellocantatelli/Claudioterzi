#!/usr/bin/env python3
"""Verifica unica di tutto cio' che e' stato affermato su R3∞ / SDQ-1.

Un solo file, sola libreria standard, nessuna dipendenza. Copiarlo e'
copiare la verifica.

Controlla tre cose:
  1. PROTOCOLLO — gli invarianti epistemici tengono in questo repository
  2. DIFETTI    — i due bug esistono davvero, e le patch si applicano
  3. REPERTI    — i fatti dichiarati RECUPERATO sono ancora nel codice

I controlli su 2 e 3 leggono il commit 155cb5f del repository sorgente
tramite `git show`, non l'albero di lavoro: cosi' la verifica non dipende
da modifiche locali e non ne introduce.

Cio' che non puo' essere verificato risulta SKIP, mai PASS. Un controllo
non eseguito non e' un controllo superato — sarebbe presentare UNKNOWN
come RECUPERATO, cioe' violare il protocollo che questo file verifica.

Uso:
    python3 test_r3.py                      # rapporto completo
    python3 test_r3.py --quiet              # solo exit code
    python3 test_r3.py --json               # rapporto leggibile da macchina
    python3 test_r3.py --repo /path/Claudio # sorgente altrove
    python3 test_r3.py --self-test          # prova che sa fallire

Exit code 0 = tutto cio' che era verificabile e' verificato.
Diverso da 0 = numero di controlli falliti.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RADICE = Path(__file__).resolve().parent
REPO_DEFAULT = RADICE / ".lavoro" / "Claudio"
COMMIT = "155cb5f"

ETICHETTE = ("RECUPERATO", "INFERITO", "IPOTESI", "UNKNOWN")
CANONICI = ("SEME.md", "PROTOCOLLO_ROSSO.md", "RICOSTRUZIONE_R3.md",
             "baseline_r3.json")
ANALISI = ("RICOSTRUZIONE_R3.md", "SOLUZIONE_2055.md")
FINESTRA_FALSIFICAZIONE = 12

# H1, HR1, H2055-A: sigla che inizia per H, contiene cifre, suffisso
# facoltativo. Una regex piu' stretta lascerebbe fuori proprio le ipotesi
# con suffisso letterale.
_RE_IPOTESI = re.compile(r"^\*\*(H[A-Z]*\d+[\w-]*)\*\*", re.MULTILINE)
_RE_FALSIF = re.compile(r"falsificat[ao]\s+se|criterio_falsificazione", re.I)

PATCHES = ("0001-fix-cli-argomenti-mancanti.patch",
           "0002-fix-registro-ipotesi-perdita-dati.patch",
           "0003-allinea-documentazione-e-config.patch",
           "0004-persistenza-vector-state-store.patch")

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"


class Rapporto:
    def __init__(self) -> None:
        self.righe: list[tuple[str, str, str, str]] = []

    def add(self, gruppo: str, nome: str, esito: str, nota: str = "") -> None:
        self.righe.append((gruppo, nome, esito, nota))

    def controlla(self, gruppo: str, nome: str, ok: bool, nota: str = "") -> bool:
        self.add(gruppo, nome, PASS if ok else FAIL, "" if ok else nota)
        return ok

    @property
    def falliti(self) -> int:
        return sum(1 for *_, e, _n in self.righe if e == FAIL)

    @property
    def saltati(self) -> int:
        return sum(1 for *_, e, _n in self.righe if e == SKIP)

    def come_json(self, repo: Path | None) -> dict:
        """Rapporto leggibile da macchina.

        Deterministico a parita' di stato verificato: nessun timestamp,
        nessun percorso assoluto. Due esecuzioni sullo stesso stato
        producono byte identici, quindi il rapporto si puo' diffare e
        se ne puo' calcolare l'hash — che e' cio' che serve per usarlo
        come prova nel tempo invece che come stampa di un momento.
        """
        return {
            "verifica": "R3∞ / SDQ-1",
            "schema": 1,
            "commit_riferimento": COMMIT,
            "sorgente_disponibile": repo is not None,
            # "ok" solo quando nulla e' rimasto non verificato: con dei SKIP
            # l'esito e' "parziale". E' il primo campo che un consumatore
            # legge, e un "ok" con 13 controlli saltati farebbe passare
            # UNKNOWN per RECUPERATO.
            "esito": ("fallito" if self.falliti
                      else "parziale" if self.saltati
                      else "ok"),
            "exit_code": self.falliti,
            "conteggi": {
                "totale": len(self.righe),
                "superati": len(self.righe) - self.falliti - self.saltati,
                "falliti": self.falliti,
                "saltati": self.saltati,
            },
            "nota_saltati": (
                "I controlli saltati NON sono superati: restano UNKNOWN."
                if self.saltati else None
            ),
            "controlli": [
                {"gruppo": g, "nome": n, "esito": e.lower(),
                 "nota": nota or None}
                for g, n, e, nota in self.righe
            ],
        }


# --------------------------------------------------------------------------- #
# utilita'                                                                     #
# --------------------------------------------------------------------------- #

def leggi_locale(nome: str) -> str | None:
    try:
        return (RADICE / nome).read_text(encoding="utf-8")
    except (FileNotFoundError, IsADirectoryError):
        return None


def git_show(repo: Path, percorso: str) -> str | None:
    """Contenuto di un file al commit di riferimento, non dall'albero di lavoro."""
    try:
        r = subprocess.run(
            ["git", "-C", str(repo), "show", f"{COMMIT}:{percorso}"],
            capture_output=True, text=True, timeout=30,
        )
    except (subprocess.SubprocessError, OSError):
        return None
    return r.stdout if r.returncode == 0 else None


def repo_utilizzabile(repo: Path) -> bool:
    if not (repo / ".git").exists():
        return False
    return git_show(repo, "README.md") is not None


# --------------------------------------------------------------------------- #
# 1. PROTOCOLLO                                                                #
# --------------------------------------------------------------------------- #

def test_protocollo(r: Rapporto) -> None:
    g = "PROTOCOLLO"

    for nome in CANONICI:
        r.controlla(g, f"documento canonico {nome}",
                    (RADICE / nome).is_file(), "assente")

    for nome in ANALISI:
        testo = leggi_locale(nome)
        if testo is None:
            r.controlla(g, f"etichette in {nome}", False, "file assente")
            continue
        presenti = [x for x in ETICHETTE if x in testo]
        r.controlla(g, f"etichette in {nome}", len(presenti) >= 3,
                    f"trovate solo {presenti or 'nessuna'}, servono 3 su 4")

    # P6: ogni ipotesi dichiara come cadrebbe.
    for percorso in sorted(RADICE.glob("*.md")):
        testo = percorso.read_text(encoding="utf-8")
        righe = testo.splitlines()
        trovate = list(_RE_IPOTESI.finditer(testo))
        for i, m in enumerate(trovate):
            n_riga = testo[: m.start()].count("\n")
            # La finestra si ferma all'ipotesi successiva: senza questo taglio
            # un'ipotesi priva di criterio erediterebbe quello della vicina.
            fine = n_riga + FINESTRA_FALSIFICAZIONE
            if i + 1 < len(trovate):
                fine = min(fine, testo[: trovate[i + 1].start()].count("\n"))
            r.controlla(g, f"P6 su {m.group(1)} ({percorso.name})",
                        bool(_RE_FALSIF.search("\n".join(righe[n_riga:fine]))),
                        "nessun criterio di falsificazione")

    testo = leggi_locale("PROTOCOLLO_ROSSO.md") or ""
    r.controlla(g, "blocco portabile presente",
                "PROTOCOLLO ROSSO ROSSO ROSSO — attenzione totale." in testo,
                "il blocco da incollare altrove e' sparito")
    r.controlla(g, "P5 e P6 enunciati",
                "P5" in testo and "P6" in testo, "principi incompleti")
    r.controlla(g, "limite dichiarato", "comando magico" in testo,
                "manca la dichiarazione di cio' che il protocollo NON e'")

    seme = leggi_locale("SEME.md") or ""
    r.controlla(g, "SEME.md autosufficiente",
                all(x in seme for x in ETICHETTE) and "P5" in seme
                and "P6" in seme and "TRACCIA" in seme,
                "il seme non trasporta piu' il protocollo completo")
    r.controlla(g, "SEME.md dichiara i propri limiti",
                "non esiste un meccanismo che lo faccia" in seme,
                "il seme non dichiara piu' cosa non puo' fare")

    b = leggi_locale("baseline_r3.json")
    if b is None:
        r.controlla(g, "baseline_r3.json parsabile", False, "assente")
    else:
        try:
            json.loads(b)
            r.controlla(g, "baseline_r3.json parsabile", True)
        except json.JSONDecodeError as exc:
            r.controlla(g, "baseline_r3.json parsabile", False, str(exc))


# --------------------------------------------------------------------------- #
# 2. DIFETTI                                                                   #
# --------------------------------------------------------------------------- #

def test_difetti(r: Rapporto, repo: Path | None) -> None:
    g = "DIFETTI"

    if repo is None:
        r.add(g, "BUG-1 CLI rotta al commit di riferimento", SKIP,
              "sorgente non disponibile")
        r.add(g, "BUG-2 registro cancella ipotesi", SKIP,
              "sorgente non disponibile")
    else:
        main = git_show(repo, "sdq1/__main__.py") or ""
        usati = set(re.findall(r"\bargs\.([a-z0-9_]+)", main))
        dichiarati = {
            m.group(1)[2:].replace("-", "_")
            for m in re.finditer(r'add_argument\(\s*"(--[a-z0-9-]+)"', main)
        }
        dichiarati |= set(re.findall(r'add_argument\(\s*"([a-z0-9_]+)"', main))
        mancanti = sorted(usati - dichiarati)
        r.controlla(g, "BUG-1 CLI rotta al commit di riferimento",
                    {"chat_telegram", "briefing_operativo"} <= set(mancanti),
                    f"attesi chat_telegram e briefing_operativo, trovati {mancanti}")

        reg = git_show(repo, "registro_ipotesi.py") or ""
        blocco = reg.split("if __name__", 1)[-1]
        r.controlla(g, "BUG-2 registro cancella ipotesi",
                    "salva()" in blocco and "carica()" not in blocco,
                    "il blocco __main__ non mostra piu' salva() senza carica()")

    # Le patch devono restare applicabili IN SEQUENCE su albero pulito: e' il
    # modo in cui verranno usate davvero. Verificarle una per una su alberi
    # separati nasconderebbe i conflitti fra patch.
    for nome in PATCHES:
        if not (RADICE / "patches" / nome).is_file():
            r.controlla(g, f"patch {nome[:4]} presente", False, "assente")

    if repo is None:
        for nome in PATCHES:
            r.add(g, f"patch {nome[:4]} applicabile in sequenza", SKIP,
                  "sorgente non disponibile")
    else:
        with tempfile.TemporaryDirectory() as td:
            ok_ck = subprocess.run(
                ["git", "-C", str(repo), "--work-tree", td, "checkout", COMMIT, "--", "."],
                capture_output=True, text=True,
            ).returncode == 0
            for nome in PATCHES:
                p = RADICE / "patches" / nome
                if not ok_ck or not p.is_file():
                    r.add(g, f"patch {nome[:4]} applicabile in sequenza", SKIP,
                          "albero pulito non disponibile")
                    continue
                res = subprocess.run(["git", "apply", str(p)],
                                     cwd=td, capture_output=True, text=True)
                r.controlla(g, f"patch {nome[:4]} applicabile in sequenza",
                            res.returncode == 0, res.stderr.strip()[:120])


# --------------------------------------------------------------------------- #
# 3. REPERTI                                                                   #
# --------------------------------------------------------------------------- #

AGENTI_AUTONOMI = ("CoerenzaKeeper", "IntelligenceDeveloper", "SistemaGuardian",
                   "MemoryManager", "MultiSystemCoordinator", "FuturePreparer",
                   "MilestoneLogger")


def test_reperti(r: Rapporto, repo: Path | None) -> None:
    g = "REPERTI"
    if repo is None:
        for nome in ("7 agenti autonomi", "pipeline SDQ-1 esplicita",
                     "SAR V3 e 10 livelli coesistono", "SAR livello 5 assente",
                     "VSS a n-grammi, non embedding", "VSS non persiste",
                     "eternal_backup simula IPFS",
                     "eternal_backup non importato da moduli",
                     "agente_orario ha continue-on-error sul passo Telegram",
                     "caccia-voli usa un entry point separato",
                     "sdq1_daily dipende interamente dal modulo rotto",
                     "r3/node.py usa Ed25519 reale"):
            r.add(g, nome, SKIP, "sorgente non disponibile")
        return

    ag = git_show(repo, "sdq1/sar/agenti_autonomi.py") or ""
    assenti = [a for a in AGENTI_AUTONOMI if f"class {a}" not in ag]
    r.controlla(g, "7 agenti autonomi", not assenti, f"classi assenti: {assenti}")

    yaml = git_show(repo, "sdq1/config/sdq1.yaml") or ""
    r.controlla(g, "pipeline SDQ-1 esplicita",
                re.search(r"pipeline:\s*(\n\s*-\s*\d+\s*(#[^\n]*)?){6}", yaml)
                is not None,
                "la pipeline a 6 caselle non e' piu' dichiarata in config")

    sar = git_show(repo, "sdq1/sar/sar.py") or ""
    sq = git_show(repo, "sdq1/sar/scacchiera_quantica.py") or ""
    r.controlla(g, "SAR V3 e 10 livelli coesistono",
                "ScacchieraAutoRiflessiva" in sar and "AutoriflessoreV3" in sq,
                "uno dei due sistemi non esiste piu'")

    livelli = set(re.findall(r"^\s+(\d+)\s+\w", sar, re.M))
    r.controlla(g, "SAR livello 5 assente",
                "5" not in livelli and "10" in livelli,
                f"livelli elencati nel docstring: {sorted(livelli)}")

    store = git_show(repo, "sdq1/memory/store.py") or ""
    r.controlla(g, "VSS a n-grammi, non embedding",
                "_shingle" in store and "sentence_transformers" not in store,
                "lo store non usa piu' n-grammi di caratteri")

    vss = git_show(repo, "sdq1/memory/vss.py") or ""
    r.controlla(g, "VSS non persiste",
                "self._idx: dict[str, str] = {}" in vss,
                "l'indice non e' piu' un dict in-process")

    eb = git_show(repo, "sdq1/agents/eternal_backup_agent.py") or ""
    r.controlla(g, "eternal_backup simula IPFS",
                '"Qm" + hashlib.sha256' in eb,
                "il generatore di CID falsi non c'e' piu'")

    try:
        grep = subprocess.run(
            ["git", "-C", str(repo), "grep", "-l", "eternal_backup", COMMIT,
             "--", "*.py"],
            capture_output=True, text=True, timeout=30,
        )
        riferimenti = [l for l in grep.stdout.splitlines()
                       if "eternal_backup_agent.py" not in l]
        r.controlla(g, "eternal_backup non importato da moduli", not riferimenti,
                    f"ora e' importato da: {riferimenti}")
    except (subprocess.SubprocessError, OSError) as exc:
        r.add(g, "eternal_backup non importato da moduli", SKIP,
              exc.__class__.__name__)

    # Portata reale di BUG-1: non tutti i workflow ne sono colpiti.
    wf_orario = git_show(repo, ".github/workflows/agente_orario.yml") or ""
    r.controlla(g, "agente_orario ha continue-on-error sul passo Telegram",
                "continue-on-error: true" in wf_orario and "--chat-telegram" in wf_orario,
                "il passo Telegram non e' piu' tollerante agli errori: BUG-1 ucciderebbe l'intero workflow")

    wf_voli = git_show(repo, ".github/workflows/caccia-voli.yml") or ""
    r.controlla(g, "caccia-voli usa un entry point separato",
                "sdq1.voli" in wf_voli and "git add" not in wf_voli,
                "caccia-voli ora passa dal __main__ o committa: la portata di BUG-1 e' cambiata")

    daily = git_show(repo, ".github/workflows/sdq1_daily.yml") or ""
    r.controlla(g, "sdq1_daily dipende interamente dal modulo rotto",
                daily.count("python3 -m sdq1 ") >= 3,
                "sdq1_daily non usa piu' tre comandi sdq1: rivedere l'analisi causale")

    node = git_show(repo, "r3/node.py") or ""
    r.controlla(g, "r3/node.py usa Ed25519 reale",
                "nacl.signing" in node and "hashlib.sha256" in node,
                "la firma reale non c'e' piu'")


# --------------------------------------------------------------------------- #
# self-test: il verificatore deve saper fallire                                #
# --------------------------------------------------------------------------- #

def self_test() -> int:
    """P5: un controllo che passa sempre non e' un controllo.

    Costruisce un documento con un'ipotesi priva di criterio di
    falsificazione, seguita da una che ce l'ha, e pretende che la prima
    venga segnalata. E' il caso che una finestra mal tagliata lascerebbe
    passare.
    """
    doc = (
        "**HX1** — ipotesi senza criterio.\n\n"
        "Testo di riempimento.\n\n"
        "**HX2** — ipotesi con criterio.\n"
        "*Falsificata se:* accade qualcosa di verificabile.\n"
    )
    righe = doc.splitlines()
    trovate = list(_RE_IPOTESI.finditer(doc))
    esiti = {}
    for i, m in enumerate(trovate):
        n = doc[: m.start()].count("\n")
        fine = n + FINESTRA_FALSIFICAZIONE
        if i + 1 < len(trovate):
            fine = min(fine, doc[: trovate[i + 1].start()].count("\n"))
        esiti[m.group(1)] = bool(_RE_FALSIF.search("\n".join(righe[n:fine])))

    ok = esiti.get("HX1") is False and esiti.get("HX2") is True
    print("SELF-TEST — il verificatore sa fallire?")
    print(f"  HX1 (senza criterio) segnalata : {'si' if not esiti.get('HX1') else 'NO'}")
    print(f"  HX2 (con criterio)   accettata : {'si' if esiti.get('HX2') else 'NO'}")
    print("  esito:", "OK" if ok else "IL VERIFICATORE E' CIECO")
    return 0 if ok else 1


# --------------------------------------------------------------------------- #

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, default=REPO_DEFAULT,
                    help="copia di claudioterzi/Claudio (default: .lavoro/Claudio)")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--json", action="store_true",
                    help="rapporto su stdout in JSON, leggibile da macchina")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    repo = args.repo if repo_utilizzabile(args.repo) else None

    r = Rapporto()
    test_protocollo(r)
    test_difetti(r, repo)
    test_reperti(r, repo)

    if args.json:
        print(json.dumps(r.come_json(repo), ensure_ascii=False, indent=2))
        return r.falliti

    if not args.quiet:
        print("VERIFICA UNICA — R3∞ / SDQ-1")
        print(f"sorgente: {repo if repo else 'NON DISPONIBILE (controlli saltati)'}")
        print("=" * 62)
        gruppo_corr = None
        for gruppo, nome, esito, nota in r.righe:
            if gruppo != gruppo_corr:
                print(f"\n── {gruppo} " + "─" * (58 - len(gruppo)))
                gruppo_corr = gruppo
            print(f"[{esito}] {nome}")
            if nota:
                print(f"       {nota}")
        print("\n" + "=" * 62)
        tot = len(r.righe)
        passati = tot - r.falliti - r.saltati
        print(f"{passati} superati · {r.falliti} falliti · {r.saltati} saltati "
              f"su {tot}")
        if r.saltati:
            print("I controlli saltati NON sono superati: restano UNKNOWN.")
        if r.falliti:
            print("Qualcosa che era stato verificato non lo e' piu'.")

    return r.falliti


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
