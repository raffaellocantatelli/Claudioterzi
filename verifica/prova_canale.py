#!/usr/bin/env python3
"""Verifica che il canale riservato esista, SENZA rischiare il token.

Si imposta una variabile innocua nell'ambiente e si controlla se arriva.
Se arriva, il canale e' provato end-to-end e solo allora vi si mette il token.

    python3 prova_canale.py

Atteso: in una sessione NUOVA, dopo aver impostato R3_CHANNEL_PROBE,
questo script la trova. Se non la trova, il canale non funziona e il token
non va tentato.
"""
import os, sys

NOME = "R3_CHANNEL_PROBE"
v = os.environ.get(NOME)
if v is None:
    print(f"CANALE NON PROVATO: {NOME} non e' nell'ambiente.")
    print("Possibili cause, in ordine:")
    print("  1. la variabile non e' stata impostata;")
    print("  2. e' stata impostata ma questa sessione e' la vecchia:")
    print("     le variabili d'ambiente le raccoglie una sessione NUOVA;")
    print("  3. la piattaforma non offre il meccanismo su questo ambiente.")
    sys.exit(1)
print(f"CANALE PROVATO: {NOME} e' arrivato, lunghezza {len(v)} caratteri.")
print("Il valore non viene stampato nemmeno per una prova.")
print("Ora lo stesso percorso puo' portare R3_API_TOKEN.")
sys.exit(0)
