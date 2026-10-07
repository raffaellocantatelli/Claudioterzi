# Provenienza dello schema

`ecc.memory.v1.schema.json` **non è nostro**. È copiato alla lettera da:

- repository `affaan-m/ECC`, percorso `schemas/memory.schema.json`
- commit `ef648e0` (clone shallow del 2026-10-07), licenza MIT
- `sha256` del file copiato: registrato in `ecc.memory.v1.schema.sha256`

Lo usiamo come **contratto dati**, non come codice: nessun eseguibile di quel
repository è stato lanciato. Il validatore in `valida_ecc.py` è scritto qui e
usa solo la libreria standard.

Verificabile in un comando:

```bash
sha256sum interop/ecc.memory.v1.schema.json
```
