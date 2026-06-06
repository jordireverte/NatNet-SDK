# NatNet-SDK — Pipeline de Neuronavegació Òptica

Python scripts per adquirir dades de posició 6-DOF des de **OptiTrack Motive** via el protocol NatNet i retransmetre-les en temps real cap a **3D Slicer** mitjançant OpenIGTLink.

Desenvolupat com a part d'un Treball de Fi de Grau sobre neuronavegació de fus ultrasònic.

---

## Contingut del repositori

```
NatNet-SDK/
└── PythonClient/
    ├── NatNetClient.py          # Llibreria de comunicació NatNet (OptiTrack)
    ├── PythonRead3Ddata.py      # Monitorització local de cossos rígids
    └── PythonSendData3DSlicer.py # Pipeline complet cap a 3D Slicer
```

---

## Scripts

### `PythonRead3Ddata.py`
Monitoritza en temps real la posició i rotació de tots els cossos rígids detectats per Motive. Calcula la posició relativa de cada cos respecte a la referència (ID 1) i la mostra per terminal a 120 Hz.

**Útil per:** verificar la connexió amb Motive i validar les dades abans d'activar el pipeline complet.

### `PythonSendData3DSlicer.py`
Pipeline principal del sistema. Rep les dades de Motive, aplica la transformació homogènia 6-DOF al sistema de coordenades RAS de 3D Slicer i emet les matrius 4×4 via OpenIGTLink (TCP, port 18944).

**Útil per:** neuronavegació en temps real amb visualització sobre model 3D al Slicer.

---

## Requisits

```
Python >= 3.8
numpy
pyigtl
```

Instal·lació de dependències:

```bash
pip install numpy pyigtl
```

> `NatNetClient.py` és la llibreria oficial d'OptiTrack i no requereix instal·lació addicional.

---

## Configuració prèvia

1. Obrir **Motive** i activar el streaming de dades (Data Streaming).
2. Definir els cossos rígids i assignar-los ID correlatius (ID 1 = referència del pacient).
3. Anotar la IP de la màquina on corre Motive (servidor) i la IP del PC local (client).
4. Per a `PythonSendData3DSlicer.py`: obrir **3D Slicer** i activar el mòdul OpenIGTLink al port 18944.

---

## Ús

### Monitorització local

```bash
python PythonRead3Ddata.py
```

El programa demanarà interactivament:
- Tipus de xarxa: `0` per Multicast, `1` per Unicast
- IP del client (per defecte `127.0.0.1`)
- IP del servidor Motive (per defecte `127.0.0.1`)

### Pipeline cap a 3D Slicer

```bash
python PythonSendData3DSlicer.py
```

Mateixos paràmetres interactius. Un cop connectat, emet automàticament les transformacions de tots els cossos configurats a `COSSOS_CONFIG`.

Per aturar qualsevol dels dos scripts: `Ctrl+C`.

---

## Configuració dels cossos rígids

A `PythonSendData3DSlicer.py`, el diccionari `COSSOS_CONFIG` mapeja cada ID de Motive amb el nom del dispositiu a 3D Slicer:

```python
COSSOS_CONFIG = {
    1: "PacientReferencia",
    2: "TransductorSimulat",
    3: "EinaAuxiliar"
}
```

Modifica aquest diccionari per afegir o canviar els cossos rígids del teu setup.

---

## Arquitectura del sistema

```
Motive (OptiTrack)
      │  UDP · port 1511 · NatNet
      ▼
PythonSendData3DSlicer.py
  ├── Fil 1 (segon pla): recepció NatNet → rigid_bodies_data{}
  └── Fil 2 (principal): transformació 6-DOF → OpenIGTLink
                                                      │  TCP · port 18944
                                                      ▼
                                              3D Slicer
```

---

## Sistema de coordenades

Motive treballa en un sistema Y-up (mètres). Els scripts apliquen el re-mapeig següent per convertir al sistema RAS de 3D Slicer (mil·límetres):

| Eix Motive | Eix RAS Slicer |
|------------|----------------|
| −X         | R              |
| Z          | A              |
| Y          | S              |

La rotació s'adapta mitjançant una transformació de semblança algebraica sobre la matriu de rotació 3×3.

---

## Llicència

MIT License — lliure per a ús acadèmic i de recerca.
