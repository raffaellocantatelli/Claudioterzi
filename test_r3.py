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
import hashlib
import json
import os
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

# Un conteggio in giorni invecchia da solo. "45 giorni di silenzio" era vero
# quando l'ho scritto e falso dodici giorni dopo, senza che nulla lo segnalasse.
# Un numero di giorni a due cifre deve portare accanto una data che lo ancori.
_RE_GIORNI = re.compile(r"\b(\d{2,})\s+giorni\b")
_RE_DATA = re.compile(r"\d{1,2}/\d{1,2}(/\d{4})?|\d{4}-\d{2}-\d{2}|"
                      r"\b(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|"
                      r"agosto|settembre|ottobre|novembre|dicembre)\b", re.I)

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

    # Ogni conteggio in giorni deve essere ancorato a una data, altrimenti
    # diventa falso col tempo senza che nessuno se ne accorga.
    # Si guarda il PARAGRAFO, non la riga: il markdown va a capo, e una data
    # legittima puo' finire sulla riga successiva. Controllare per riga
    # produceva falsi positivi — verificato su SEME.md.
    non_ancorati = []
    for percorso in sorted(RADICE.glob("*.md")):
        testo = percorso.read_text(encoding="utf-8")
        offset = 1
        for blocco in testo.split("\n\n"):
            if _RE_GIORNI.search(blocco) and not _RE_DATA.search(blocco):
                non_ancorati.append(f"{percorso.name}:~{offset}")
            offset += blocco.count("\n") + 2
    r.controlla(g, "conteggi in giorni ancorati a una data", not non_ancorati,
                f"senza data: {', '.join(non_ancorati[:4])}")

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

def test_deriva(r: Rapporto, repo: Path | None) -> None:
    """La baseline descrive ancora il presente, o un passato archeologico?

    Un test puo' essere verde riguardo a un mondo che non esiste piu'. Tutti
    i controlli su DIFETTI e REPERTI leggono il commit fissato in COMMIT: se
    origin/main e' andato avanti, quei verdi parlano di archeologia e non di
    realta'. E' la stessa trappola del rapporto troncato, in forma eseguibile.
    Verificato davvero: al 2026-10-04 la baseline era 677 commit indietro e
    la suite era tutta verde.
    """
    g = "DERIVA"
    if repo is None:
        r.add(g, "la baseline descrive lo stato attuale", SKIP,
              "sorgente non disponibile")
        return
    try:
        res = subprocess.run(
            ["git", "-C", str(repo), "rev-list", "--count", f"{COMMIT}..origin/main"],
            capture_output=True, text=True, timeout=60)
        dietro = int(res.stdout.strip()) if res.returncode == 0 else -1
    except (subprocess.SubprocessError, OSError, ValueError):
        dietro = -1
    if dietro < 0:
        r.add(g, "la baseline descrive lo stato attuale", SKIP,
              "impossibile misurare la distanza da origin/main")
        return
    r.controlla(g, "la baseline descrive lo stato attuale", dietro == 0,
                f"la baseline e' ferma a {COMMIT}, origin/main e' {dietro} commit "
                f"piu' avanti: i verdi di DIFETTI e REPERTI descrivono il passato")


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

def test_custodia(r: Rapporto, repo: Path | None = None) -> None:
    """Controlla che il pacchetto cieco resti cieco.

    Chi modifica ITEMS.md puo' far finire il disegno dentro un item senza
    accorgersene: e' gia' accaduto una volta, e lo script se n'e' accorto solo
    perche' verifica la propria uscita. Qui si verifica che quella verifica
    funzioni ancora.
    """
    G = "CUSTODIA"
    base = Path(__file__).resolve().parent
    esp = base / "esperimento"
    pac = esp / "pacchetto"

    for nome, percorso in (
        ("previsioni cifrate presenti", esp / "PREVISIONI.enc"),
        ("emendamento 01 in chiaro", esp / "EMENDAMENTO_01.md"),
        ("indice dei due sigilli", esp / "CUSTODIA.md"),
        ("istruzioni separate per chi codifica", pac / "ISTRUZIONI_CODIFICATORE.md"),
        ("script di assemblaggio", pac / "assembla.py"),
    ):
        r.controlla(G, nome, percorso.is_file(), f"manca {percorso.name}")

    # i due hash sigillati devono restare citati alla lettera
    cust = leggi_locale("esperimento/CUSTODIA.md") or ""
    for etichetta, h in (
        ("previsioni",
         "54f258a811c3411c3a15e49635243b52a07d8fced9c28c556a16e6cfa31b5a90"),
        ("placebo e contaminazione",
         "9b26358483158011f405b5cf0618ca884d9191c230b5eb59618f14480282b1d8"),
    ):
        r.controlla(G, f"hash {etichetta} citato per intero", h in cust,
                    "l'hash non compare: il sigillo diventa inverificabile")

    # il cifrato deve ancora restituire il chiaro sigillato: senza questo,
    # PREVISIONI.enc e' un file opaco di cui nessuno sa piu' niente
    enc = esp / "PREVISIONI.enc"
    if not enc.is_file():
        r.add(G, "il cifrato restituisce l'hash sigillato", SKIP,
              "PREVISIONI.enc assente")
    elif not os.environ.get("R3_PASSPHRASE"):
        r.add(G, "il cifrato restituisce l'hash sigillato", SKIP,
              "serve R3_PASSPHRASE nell'ambiente; senza, resta UNKNOWN")
    else:
        try:
            out = subprocess.run(
                ["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2",
                 "-iter", "600000", "-in", str(enc),
                 "-pass", "env:R3_PASSPHRASE"],
                capture_output=True, timeout=60,
            )
            got = hashlib.sha256(out.stdout).hexdigest()
            r.controlla(
                G, "il cifrato restituisce l'hash sigillato",
                out.returncode == 0 and got ==
                "54f258a811c3411c3a15e49635243b52a07d8fced9c28c556a16e6cfa31b5a90",
                f"decifrato con sha256 {got[:16]}..., non quello sigillato",
            )
        except (OSError, subprocess.SubprocessError) as e:
            r.add(G, "il cifrato restituisce l'hash sigillato", SKIP, str(e))

    # --- BLOCKER-CUSTODY-02 ---------------------------------------------- #
    # Un hash senza chiaro recuperabile non e' una preregistrazione. Il
    # sigillo delle previsioni ha il suo chiaro cifrato e committato; il
    # secondo sigillo, al 2026-10-04, no. Questo controllo resta rosso
    # finche' non si chiude, cosi' START non si puo' dare per distrazione.
    SIGILLO_2 = "9b26358483158011f405b5cf0618ca884d9191c230b5eb59618f14480282b1d8"

    blocchi = leggi_locale("esperimento/BLOCCHI.md") or ""
    r.controlla(G, "il registro dei blocchi esiste e cita il secondo sigillo",
                SIGILLO_2 in blocchi,
                "esperimento/BLOCCHI.md manca o non cita 9b263584...")
    r.controlla(G, "BLOCKER-CUSTODY-02 dichiara un criterio di chiusura",
                "BLOCKER-CUSTODY-02" in blocchi
                and "Criterio di chiusura" in blocchi,
                "un blocco senza criterio di chiusura non si puo' chiudere")

    # v1 deve restare visibile e marcato: cancellarlo farebbe sparire la
    # genealogia, che e' l'unica cosa che distingue un abbandono dichiarato
    # da un insabbiamento
    gen = (leggi_locale("esperimento/CUSTODIA.md") or "") + blocchi
    r.controlla(G, "il sigillo abbandonato resta visibile e marcato ORPHANED",
                SIGILLO_2 in gen and "ORPHANED" in gen,
                "v1 non e' piu' citato o non e' marcato: un sigillo scomparso "
                "e' un buco nella genealogia")

    # lo strumento che sigilla deve rifiutare cio' che deve rifiutare
    sig = esp / "sigilla.py"
    if not sig.is_file():
        r.add(G, "lo strumento di sigillatura rifiuta materiale non conforme",
              SKIP, "sigilla.py assente")
    else:
        try:
            e = subprocess.run([sys.executable, str(sig), "--self-test"],
                               capture_output=True, timeout=180)
            r.controlla(G,
                        "lo strumento di sigillatura rifiuta materiale non conforme",
                        e.returncode == 0,
                        "il self-test fallisce: uno strumento che sigilla "
                        "sempre non controlla niente")
        except (OSError, subprocess.SubprocessError) as exc:
            r.add(G, "lo strumento di sigillatura rifiuta materiale non conforme",
                  SKIP, str(exc))

    # 1) il chiaro recuperato, se qualcuno lo indica, deve produrre quell'hash
    recuperato = os.environ.get("R3_CUSTODIA2")
    if recuperato:
        f = Path(recuperato)
        if not f.is_file():
            r.controlla(G, "BLOCKER-CUSTODY-02 chiuso: round-trip verificato",
                        False, f"R3_CUSTODIA2 punta a un file assente: {f}")
        else:
            got = hashlib.sha256(f.read_bytes()).hexdigest()
            r.controlla(G, "BLOCKER-CUSTODY-02 chiuso: round-trip verificato",
                        got == SIGILLO_2,
                        f"il materiale indicato ha sha256 {got[:16]}..., "
                        "non quello sigillato: non sono quei byte")
    else:
        # 2) altrimenti si cerca un cifrato depositato accanto all'hash
        # il manifesto e' testo deterministico: si ricalcola, non si crede
        MANIFESTO_V2 = ("7a55931dcc51a190942fe3a78f537ac8b"
                        "0662f51ab07b5c44edb345cfa40c8c9")
        man = esp / "OPENAI_CUSTODY_V2_MANIFEST.txt"
        if not man.is_file():
            r.controlla(G, "manifesto v2 persistito e verificato", False,
                        "OPENAI_CUSTODY_V2_MANIFEST.txt assente: la terza "
                        "ricevuta non e' durevole")
        else:
            got = hashlib.sha256(man.read_bytes()).hexdigest()
            r.controlla(G, "manifesto v2 persistito e verificato",
                        got == MANIFESTO_V2,
                        f"il manifesto ha sha256 {got[:16]}..., non quello "
                        "dichiarato: non e' lo stesso oggetto")

        # i cifrati sono l'unica cosa che chiude il blocco, e non li ho io
        depositato = []
        if repo is not None and repo.is_dir():
            for pattern in ("docs/experiments/*CUSTODY_V2*.enc",
                            "docs/experiments/*custody_v2*.enc"):
                depositato += list(repo.glob(pattern))
        depositato += list(esp.glob("OPENAI_CUSTODY_V2_*.enc"))
        r.controlla(
            G, "BLOCKER-CUSTODY-02 chiuso: cifrati v2 persistiti",
            len(depositato) >= 2,
            "APERTO: v2 e' generato e il round-trip verificato, ma il deposito "
            "dei cifrati e' fallito (container_session_expired). Il manifesto "
            "e' salvo, i due cifrati no. Nessun START "
            "(vedi esperimento/BLOCCHI.md)",
        )

    # lo strumento di recupero deve ritrovare una ricetta nota: senza questa
    # controprova, uno strumento che non trova mai niente sarebbe
    # indistinguibile da uno rotto
    rec = esp / "recupera_sigillo.py"
    if not rec.is_file():
        r.add(G, "lo strumento di recupero ritrova una ricetta nota", SKIP,
              "recupera_sigillo.py assente")
    else:
        try:
            e = subprocess.run([sys.executable, str(rec), "--self-test"],
                               capture_output=True, timeout=120)
            r.controlla(G, "lo strumento di recupero ritrova una ricetta nota",
                        e.returncode == 0,
                        "il self-test fallisce: non ci si puo' fidare di un "
                        "esito negativo del recupero")
        except (OSError, subprocess.SubprocessError) as exc:
            r.add(G, "lo strumento di recupero ritrova una ricetta nota",
                  SKIP, str(exc))

    # lo script deve rifiutarsi di consegnare un pacchetto che rivela il disegno
    script = pac / "assembla.py"
    if not script.is_file() or not (esp / "ITEMS.md").is_file():
        r.add(G, "l'assemblaggio rifiuta un pacchetto che rivela il disegno",
              SKIP, "script o item assenti")
        return
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # un item che nomina il disegno: lo script DEVE fermarsi
        (td / "avvelenato.md").write_text(
            "### Finto uno\nTesto.\n**Domanda?**\n\n"
            "### Finto due\nQuesto item nomina il placebo.\n**Domanda?**\n\n"
            "### Finto tre\nTesto.\n**Domanda?**\n",
            encoding="utf-8")
        (td / "pulito.md").write_text(
            "### Finto uno\nTesto.\n**Domanda?**\n\n"
            "### Finto due\nTesto.\n**Domanda?**\n\n"
            "### Finto tre\nTesto.\n**Domanda?**\n",
            encoding="utf-8")
        esiti = {}
        for nome in ("avvelenato", "pulito"):
            try:
                e = subprocess.run(
                    [sys.executable, str(script), "--items", str(esp / "ITEMS.md"),
                     "--contaminazione", str(td / f"{nome}.md"),
                     "--out", str(td / nome), "--seme", "1"],
                    capture_output=True, timeout=120,
                )
                esiti[nome] = e.returncode
            except (OSError, subprocess.SubprocessError) as exc:
                r.add(G, "l'assemblaggio rifiuta un pacchetto che rivela il disegno",
                      SKIP, str(exc))
                return

        r.controlla(G, "l'assemblaggio rifiuta un pacchetto che rivela il disegno",
                    esiti.get("avvelenato") == 2,
                    f"uscita {esiti.get('avvelenato')} invece di 2: la guardia "
                    "non scatta e il disegno finirebbe nel pacchetto")

        # controprova: su materiale pulito la guardia non deve scattare,
        # altrimenti passerebbe sempre e non proverebbe niente
        r.controlla(G, "l'assemblaggio non scatta su materiale pulito",
                    esiti.get("pulito") != 2,
                    f"uscita 2 anche su materiale pulito: guardia troppo larga")

        # nessuna chiave di scoring in cio' che viene consegnato
        consegnati = sorted((td / "pulito" / "pacchetto_cieco" / "item").glob("*.md"))
        r.controlla(G, "il pacchetto consegnato contiene 13 item",
                    len(consegnati) == 13,
                    f"{len(consegnati)} item invece di 13")
        residui = [f.name for f in consegnati
                   if any(l.startswith(">") for l in
                          f.read_text(encoding="utf-8").splitlines())]
        r.controlla(G, "nessuna chiave di scoring negli item consegnati",
                    not residui, f"citazioni residue in {residui}")


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
    test_deriva(r, repo)
    test_difetti(r, repo)
    test_reperti(r, repo)
    test_custodia(r, repo)

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
