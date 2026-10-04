#!/usr/bin/env python3
"""GEN — generatore deterministico del fixture R3-PEER/1.1c.

Non decide nulla. Produce envelope secondo §4 della spec e NON dice quale
decisione sia corretta: non e' un oracolo, e non deve diventarlo.

    python3 genera_fixture.py --out <cartella>
    python3 genera_fixture.py --prova-riproducibilita

Il seed non e' scelto qui: e' pinnato e ricalcolato a ogni esecuzione dalla
formula preregistrata. La distribuzione non e' scritta qui: viene **letta
dalla preregistrazione sigillata**, cosi' non puo' derivare dal documento che
la impegna.

Tre uscite:
  FIXTURE.jsonl        gli eventi, senza etichette di strato
  FIXTURE.manifest.json   conteggi, hash, seed, versione — confronta la
                          distribuzione ottenuta con quella impegnata
  PROVENIENZA_STRATI.tsv  indice evento -> strato. NON si consegna agli
                          implementatori: direbbe loro la risposta

Determinismo: nessuna iterazione su insiemi non ordinati, `sort_keys=True`,
`random.Random` seminato dall'intero del seed. Stdlib only.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import random
import re
import subprocess
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
PREREG = QUI / "PREREGISTRAZIONE_SCORING.md"

ANCORA = "81dce982dfbd1d4b5f646b1418efbc24c8be4bf0"
ETICHETTA = "R3-FIXTURE-1000"
SEED_ATTESO = "583efd3fed126a802aa716fe2537e116850a2fbc2f94c9d59580a1cdc0b7466b"
APERTI = ("S11", "S12")   # esercitano OPEN FINDINGS: fuori dal denominatore
VERSIONE = "R3-PEER/1.1c"
T0 = "2026-10-04T12:00:00Z"


def seed_pinnato() -> tuple[str, int]:
    """Ricalcola il seed dalla formula, invece di fidarsi del valore scritto."""
    b = ANCORA.encode("ascii") + ETICHETTA.encode("ascii")
    h = hashlib.sha256(b).hexdigest()
    if h != SEED_ATTESO:
        raise SystemExit(
            f"il seed ricalcolato ({h}) non e' quello pinnato ({SEED_ATTESO}): "
            "la formula o il pinning sono cambiati")
    return h, int(h, 16)


def distribuzione() -> dict[str, int]:
    """Legge gli strati dalla preregistrazione sigillata, non da qui."""
    if not PREREG.is_file():
        raise SystemExit(f"manca {PREREG}")
    t = PREREG.read_text(encoding="utf-8")
    d: dict[str, int] = {}
    for riga in t.splitlines():
        if re.match(r"^\| S\d+ \|", riga):
            c = [x.strip() for x in riga.split("|")]
            d[c[1]] = int(c[4])
    if not d:
        raise SystemExit("nessuno strato trovato nella preregistrazione")
    tot = sum(d.values())
    den = tot - sum(d[k] for k in APERTI if k in d)
    if tot != 1000:
        raise SystemExit(f"la distribuzione somma {tot}, non 1000")
    if den != 900:
        raise SystemExit(f"il denominatore e' {den}, non 900")
    basso = sorted((k, v) for k, v in d.items() if v <= 20)
    if basso:
        raise SystemExit(f"strati troppo piccoli per la soglia: {basso}")
    return d


def jcs(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def sha(s: str | bytes) -> str:
    if isinstance(s, str):
        s = s.encode("utf-8")
    return "sha256:" + hashlib.sha256(s).hexdigest()


class Stato:
    """Stato di generazione: gli eventi vedono quelli precedenti (punto 3)."""

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng
        self.canali: list[str] = [self._uuid() for _ in range(4)]
        self.nodi: list[str] = [self._nodo() for _ in range(5)]
        self.key_ref: dict[str, str] = {
            n: f"opaque:keyref:{i:02d}" for i, n in enumerate(sorted(self.nodi))
        }
        self.revocate: list[tuple[str, str]] = []   # (key_ref, effective_from)
        self.msg_visti: list[tuple[str, str, str]] = []  # (chan, sender, msg_id)
        self.nonce_visti: list[tuple[str, str, str]] = []
        self.ultimo_hash: dict[str, str] = {}
        self.emessi: list[dict] = []
        self.n = 0

    def _uuid(self) -> str:
        h = self.rng.getrandbits(128)
        s = f"{h:032x}"
        return f"{s[:8]}-{s[8:12]}-7{s[13:16]}-{s[16:20]}-{s[20:32]}"

    def _nodo(self) -> str:
        return "ed25519:" + base64.b64encode(
            bytes(self.rng.getrandbits(8) for _ in range(32))
        ).decode()

    def _nonce(self) -> str:
        return base64.b64encode(
            bytes(self.rng.getrandbits(8) for _ in range(16))).decode()

    def _ts(self, delta: int) -> str:
        m = delta % 60
        h = 12 + (delta // 60) % 12
        return f"2026-10-04T{h:02d}:{m:02d}:00Z"

    def base(self, chan: str, sender: str) -> dict:
        self.n += 1
        payload = {"op": "note", "seq": self.n,
                   "body": f"evento {self.n}"}
        env = {
            "version": VERSIONE,
            "channel_id": chan,
            "channel_registry_ref": f"opaque:chanref:{self.canali.index(chan)}"
                                    if chan in self.canali else "opaque:chanref:?",
            "msg_id": self._uuid(),
            "sender_node_id": sender,
            "sender_key_ref": self.key_ref.get(sender, "opaque:keyref:??"),
            "recipient_node_id": self.nodi[(self.nodi.index(sender) + 1)
                                           % len(self.nodi)],
            "nonce": self._nonce(),
            "timestamp": self._ts(self.n),
            "expiry": self._ts(self.n + 300),
            "operation": "APPEND",
            "policy_profile_id": "pp-default",
            "prev_message_hash": self.ultimo_hash.get(chan, sha("")),
            "observed_source_memory_head": None,
            "source_memory_namespace": "ns-main",
            "observed_decision_head": None,
            "payload_mode": "INLINE",
            "payload": payload,
            "payload_ref": None,
            "payload_hash": sha(jcs(payload)),
            "raw_input_hash": sha(jcs(payload)),
            "claimed_identity": {
                "node_identity": sender,
                "provider_identity": "provider-x",
                "provider_account_ref": "opaque:acctref:01",
                "model_requested": "model-a",
                "model_reported": "model-a",
                "transport_identity": "tls:endpoint-1",
                "evidence_origin_claimed": "api_direct",
            },
            "causal_origin_ids": [],
            "evidence_parent_ids": [],
            "signature": "ed25519:" + hashlib.sha256(
                jcs(payload).encode()).hexdigest()[:43],
        }
        return env

    def registra(self, env: dict) -> None:
        self.ultimo_hash[env["channel_id"]] = sha(jcs(env))
        self.msg_visti.append((env["channel_id"], env["sender_node_id"],
                               env["msg_id"]))
        self.nonce_visti.append((env["channel_id"], env["sender_node_id"],
                                 env["nonce"]))
        self.emessi.append(env)


# --- iniezioni, una per strato. Nessuna dice quale sia la decisione giusta --- #

def s1(st: Stato, e: dict) -> dict:
    return e

def s2(st: Stato, e: dict) -> dict:          # channel non nel registry
    e["channel_id"] = st._uuid()
    e["channel_registry_ref"] = "opaque:chanref:unknown"
    return e

def s3(st: Stato, e: dict) -> dict:          # msg_id duplicato, stesso scope
    cand = [m for m in st.msg_visti if m[0] == e["channel_id"]
            and m[1] == e["sender_node_id"]]
    if cand:
        e["msg_id"] = cand[-1][2]
    return e

def s4(st: Stato, e: dict) -> dict:          # nonce riusato, msg_id nuovo
    cand = [n for n in st.nonce_visti if n[0] == e["channel_id"]
            and n[1] == e["sender_node_id"]]
    if cand:
        e["nonce"] = cand[-1][2]
    return e

def s5(st: Stato, e: dict) -> dict:          # sender dichiara canonical head
    e["canonical_memory_head"] = sha(f"vietato-{st.n}")
    return e

def s6(st: Stato, e: dict) -> dict:          # key_ref noto, pubkey diversa
    e["claimed_identity"]["node_identity"] = st._nodo()
    return e

def s7(st: Stato, e: dict) -> dict:          # REVOCATION retroattiva
    e["operation"] = "REVOCATION"
    e["payload"] = {"revokes": e["sender_key_ref"],
                    "effective_from": "2026-09-01T00:00:00Z"}
    e["payload_hash"] = sha(jcs(e["payload"]))
    e["raw_input_hash"] = e["payload_hash"]
    st.revocate.append((e["sender_key_ref"], "2026-09-01T00:00:00Z"))
    return e

def s8(st: Stato, e: dict) -> dict:          # firmato da chiave revocata
    if st.revocate:
        e["sender_key_ref"] = sorted(st.revocate)[0][0]
    return e

def s9(st: Stato, e: dict) -> dict:          # LINK-ONLY che pretende canonical
    e["operation"] = "LINK"
    e["payload"] = {"link_to": sha(f"doc-{st.n}"), "request_write": "CANONICAL"}
    e["payload_hash"] = sha(jcs(e["payload"]))
    e["raw_input_hash"] = e["payload_hash"]
    return e

def s10(st: Stato, e: dict) -> dict:         # MODEL_ATTESTED senza challenge
    e["claimed_identity"]["model_reported"] = "model-a"
    e["payload"] = {"attestation": {"claim": "MODEL_ATTESTED"}}
    e["payload_hash"] = sha(jcs(e["payload"]))
    e["raw_input_hash"] = e["payload_hash"]
    return e

def s11(st: Stato, e: dict) -> dict:         # replay broadcast obsoleto — O5
    if st.emessi:
        vecchio = st.emessi[0]
        e["prev_message_hash"] = vecchio["prev_message_hash"]
        e["observed_decision_head"] = vecchio["observed_decision_head"]
        e["operation"] = "BROADCAST"
    return e

def s12(st: Stato, e: dict) -> dict:         # claimed vs verified — O1
    e["claimed_identity"]["evidence_origin_claimed"] = "api_direct"
    e["claimed_identity"]["transport_identity"] = None
    e["claimed_identity"]["provider_account_ref"] = None
    return e

def s13(st: Stato, e: dict) -> dict:         # stesso stato, chiavi permutate
    e["__permuta__"] = True
    return e


INIEZIONI = {"S1": s1, "S2": s2, "S3": s3, "S4": s4, "S5": s5, "S6": s6,
             "S7": s7, "S8": s8, "S9": s9, "S10": s10, "S11": s11,
             "S12": s12, "S13": s13}


def genera(out: Path) -> dict:
    seed_hex, seed_int = seed_pinnato()
    dist = distribuzione()
    rng = random.Random(seed_int)
    st = Stato(rng)

    # sequenza: ordine degli strati mescolato una volta, deterministicamente
    sequenza: list[str] = []
    for s in sorted(dist):                      # sorted: niente dict order
        sequenza += [s] * dist[s]
    rng.shuffle(sequenza)

    righe: list[str] = []
    provenienza: list[tuple[int, str]] = []
    for i, strato in enumerate(sequenza, start=1):
        chan = st.canali[rng.randrange(len(st.canali))]
        sender = st.nodi[rng.randrange(len(st.nodi))]
        env = INIEZIONI[strato](st, st.base(chan, sender))
        permuta = env.pop("__permuta__", False)
        st.registra(env)
        if permuta:
            # S13: chiavi deliberatamente NON ordinate. Vedi L4 nel documento:
            # un fixture interamente canonico non puo' testare la
            # canonicalizzazione.
            chiavi = sorted(env)
            rng.shuffle(chiavi)
            riga = json.dumps({k: env[k] for k in chiavi},
                              separators=(",", ":"), ensure_ascii=False)
        else:
            riga = jcs(env)
        righe.append(riga)
        provenienza.append((i, strato))

    out.mkdir(parents=True, exist_ok=True)
    f = out / "R3_PEER_1_1C_FIXTURE_1000.jsonl"
    f.write_text("\n".join(righe) + "\n", encoding="utf-8")

    ottenuta = {s: sequenza.count(s) for s in sorted(dist)}
    gen_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    manifest = {
        "fixture": f.name,
        "fixture_sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
        "eventi": len(righe),
        "seed_formula": f'sha256(ascii("{ANCORA}") + ascii("{ETICHETTA}"))',
        "seed_sha256": seed_hex,
        "generatore": Path(__file__).name,
        "generatore_sha256": gen_sha,
        "python": sys.version.split()[0],
        "preregistrazione_sha256": hashlib.sha256(
            PREREG.read_bytes()).hexdigest(),
        "distribuzione_impegnata": dist,
        "distribuzione_ottenuta": ottenuta,
        "distribuzione_coincide": dist == ottenuta,
        "strati_fuori_denominatore": list(APERTI),
        "denominatore": sum(v for k, v in ottenuta.items() if k not in APERTI),
        "righe_non_canoniche": sorted(i for i, s in provenienza if s == "S13"),
        "nota_S13": "chiavi deliberatamente permutate: un fixture interamente "
                    "JCS-canonico non puo' testare la canonicalizzazione",
    }
    if not manifest["distribuzione_coincide"]:
        raise SystemExit("la distribuzione ottenuta non coincide con quella "
                         "impegnata: non scrivo il manifest")
    (out / "R3_PEER_1_1C_FIXTURE_1000.manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8")
    ris = out / "RISERVATO_non_consegnare"
    ris.mkdir(exist_ok=True)
    (ris / "PROVENIENZA_STRATI.tsv").write_text(
        "".join(f"{i}\t{s}\n" for i, s in provenienza), encoding="utf-8")
    return manifest


def prova_riproducibilita() -> int:
    """Processi SEPARATI, con PYTHONHASHSEED diversi.

    Due esecuzioni nello stesso processo non provano niente: condividono
    l'hash seed, e un'eventuale iterazione su un insieme non ordinato
    darebbe lo stesso ordine in entrambe. La prova deve attraversare
    processi.
    """
    import os
    import tempfile
    hash_seed = ["0", "1", "12345", "random"]
    hash_ottenuti = []
    for hs in hash_seed:
        with tempfile.TemporaryDirectory() as d:
            amb = dict(os.environ, PYTHONHASHSEED=hs)
            e = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--out", d],
                capture_output=True, text=True, env=amb, timeout=300)
            if e.returncode != 0:
                print(f"  PYTHONHASHSEED={hs}: esecuzione fallita\n{e.stderr}")
                return 1
            man = json.loads(
                (Path(d) / "R3_PEER_1_1C_FIXTURE_1000.manifest.json")
                .read_text(encoding="utf-8"))
            hash_ottenuti.append(man["fixture_sha256"])
            print(f"  PYTHONHASHSEED={hs:<7} -> {man['fixture_sha256']}")
    ok = len(set(hash_ottenuti)) == 1
    print("  esito:", "RIPRODUCIBILE" if ok else "NON RIPRODUCIBILE")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--prova-riproducibilita", action="store_true")
    a = ap.parse_args(argv)
    if a.prova_riproducibilita:
        return prova_riproducibilita()
    if not a.out:
        ap.error("serve --out")
    m = genera(a.out)
    print(f"eventi: {m['eventi']}   denominatore: {m['denominatore']}")
    print(f"seed:    {m['seed_sha256']}")
    print(f"fixture: {m['fixture_sha256']}")
    print(f"distribuzione coincide con l'impegno: "
          f"{'SI' if m['distribuzione_coincide'] else 'NO'}")
    print(f"righe non canoniche (S13): {len(m['righe_non_canoniche'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
