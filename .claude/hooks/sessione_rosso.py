#!/usr/bin/env python3
"""Hook SessionStart: inietta il Protocollo Rosso Rosso Rosso nel contesto.

CLAUDE.md viene gia' letto a ogni sessione. Questo hook e' la seconda gamba:
inietta il blocco anche se CLAUDE.md venisse troncato o ignorato, e riporta
subito se gli invarianti del protocollo reggono ancora.

Il protocollo non e' un comando magico. E' un artefatto: dura quanto il file
che lo contiene, e vale dove quel file viene letto.
"""

import json
import subprocess
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]

BLOCCO = """PROTOCOLLO ROSSO ROSSO ROSSO — attivo per default in questo repository.

Etichetta OGNI affermazione: RECUPERATO (letto/eseguito alla fonte) · INFERITO ·
IPOTESI · UNKNOWN. Mai presentare inferenza o ipotesi come recupero. La fonte di
un recupero e' il dato, mai un documento che ne parla.

Verifica prima di concludere: leggi, esegui, misura. Dove documentazione e codice
divergono, vince il codice. Cerca alternative. Cerca attivamente cio' che ti
smentirebbe. Segnala le contraddizioni, comprese quelle nelle tue conclusioni.

P5 — niente auto-conferma: confermare richiede una fonte diversa da chi ha
formulato l'ipotesi.
P6 — ogni ipotesi dichiara come potrebbe essere falsificata. Se non lo dichiara,
non puo' essere confermata.

Cerca anche cio' che manca. Un'anomalia prova che qualcosa non torna, non che
qualcosa e' nascosto.

Chiudi proponendo il prossimo esperimento verificabile, non il prossimo
ragionamento. Attenzione totale significa verificare di piu', non scrivere di piu'.

Definizione canonica: PROTOCOLLO_ROSSO.md"""


def stato_invarianti() -> str:
    verifica = RADICE / "verifica_protocollo.py"
    if not verifica.is_file():
        return "Verificatore assente: invarianti non controllati."
    try:
        r = subprocess.run(
            [sys.executable, str(verifica), "--quiet"],
            cwd=RADICE, capture_output=True, timeout=30,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        return f"Verificatore non eseguibile ({exc.__class__.__name__})."
    if r.returncode == 0:
        return "Invarianti del protocollo: rispettati."
    return (f"Invarianti del protocollo: {r.returncode} violazion"
            f"{'e' if r.returncode == 1 else 'i'}. "
            "Eseguire `python3 verifica_protocollo.py` prima di procedere.")


def main() -> int:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": f"{BLOCCO}\n\n{stato_invarianti()}",
        },
        "suppressOutput": True,
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
