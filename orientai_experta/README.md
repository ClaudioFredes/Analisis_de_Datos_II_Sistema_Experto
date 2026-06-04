# ORIENTAI · Sistema Experto de Orientación Vocacional

Sistema experto vocacional basado en un **motor de reglas** (Experta /
forward-chaining). Cubre **90 carreras** en **6 dominios vocacionales**
(una carrera puede pertenecer a más de un dominio).

---

## Cómo funciona

El razonamiento es 100 % simbólico: **hechos + reglas**. No hay similitud
numérica ni vectores de distancia. Cada recomendación se justifica con las
reglas concretas que la generaron.

### Las tres fases de elicitación

1. **F1 · Dominio** — 18 preguntas Likert evalúan la afinidad del usuario con
   cada uno de los 6 dominios. El sistema rankea los dominios y el usuario elige
   uno (puede elegir uno distinto al recomendado). También elige preferencia de
   duración (tecnicatura / grado / indiferente). Esto reduce el espacio de búsqueda
   de 90 a ~15 carreras.

2. **F2 · Perfil RIASEC** — 10 tríadas de comparación forzada (1 de 3) construyen
   el vector RIASEC del usuario. Cada elección suma una victoria a la dimensión
   elegida. Fórmula: `score[dim] = 1 + (victorias / apariciones) × 4` → perfil 1–5.

3. **F3 · Valores (pathway)** — Según la dimensión dominante del perfil, el sistema
   detecta un *pathway* (sub-perfil) y presenta 5 preguntas bipolares calibradas
   para ese sub-perfil. Las respuestas generan **boosts a carreras específicas**
   (`factor = (respuesta − 3) / 2 → [−1, +1]`), ajustando finamente el ranking.
   Hay 18 pathways × 5 preguntas = 90 ajustes posibles.

### Las reglas del motor

**Reglas principales:**

- **R1 · Holland** — Si la carrera está en el dominio elegido y sus letras RIASEC
  dominantes coinciden con los intereses *altos* del usuario, genera una
  recomendación. Puntaje de certeza: letra dominante = +3, secundaria = +2,
  terciaria = +1.
- **R3 · Boost F3** — Aplica los boosts del pathway (calculados en F3) a las
  carreras concretas que cada respuesta bipolar favorece.

**Reglas expertas** — conocimiento humano que el matching genérico no captura.
Acumulan en el campo `boost` y son completamente explicables:

- **E1 · anti-confound** — penaliza (−0.8) si la letra que *define* la carrera no
  está entre los intereses altos del usuario. Evita que una coincidencia en letra
  secundaria posicione mal una carrera.
- **E2 · rechazo del rasgo dominante** — penaliza (−1.2) si el usuario puntúa muy
  bajo la letra dominante de la carrera (la rechaza activamente).
- **E3 · alineación principal** — refuerza (+0.5) si el interés #1 del usuario
  coincide exactamente con la letra dominante de la carrera. Ejemplo: Psicología
  (S-I-A) y Biología (I-S-R) pueden empatar en certeza 5; E3 detecta que Biología
  es I-dominante y que I es el interés #1 del usuario → +0.5 que rompe el empate.
- **E4 · preferencia de duración** — refuerza (+0.4) las carreras cuya duración
  coincide con la preferencia elegida en F1.

### Ordenamiento final

`certeza (R1) + ajustes (R3 + E1–E4)` como criterio primario.
Ante empates, **afinidad** continua (intensidad del perfil sobre el código Holland
de la carrera). Todo dirigido por reglas y completamente explicable.

---

## Estructura del proyecto

```
orientai_experta/
├── compat.py               # shims para correr Experta en Python 3.10+/3.14
├── build_kb.py             # genera data/carreras_reglas.json
├── motor_reglas.py         # KnowledgeEngine: hechos + reglas R1/R3 + E1–E4
├── app_reglas.py           # UI Streamlit de 3 fases
├── test_motor.py           # tests del motor
├── requirements.txt
└── data/
    ├── carreras_reglas.json    # base de conocimiento (90 carreras, 6 dominios, código Holland)
    ├── f1_reglas.json          # 18 preguntas Likert de F1 (3 por dominio)
    ├── triadas_reglas.json     # tríadas de F2 (comparación 1-de-3, por dominio)
    └── fase3_reglas.json       # F3: 18 pathways con 5 preguntas bipolares cada uno
```

---

## Instalación y uso

```bash
pip install -r requirements.txt

# (opcional) regenerar la base de conocimiento
python build_kb.py

# tests del motor
python test_motor.py

# correr la app
python -m streamlit run app_reglas.py   # -> http://localhost:8501
```

---

## Compatibilidad con Python 3.10+

Experta (último release 2018) no es compatible de fábrica con Python 3.10+:

- `frozendict==1.2` usa `collections.Mapping` (movido a `collections.abc` en 3.10).
- Experta usa `inspect.getargspec` (removido en 3.11).

`compat.py` aplica ambos *shims* antes de importar Experta. Se importa
automáticamente desde `motor_reglas.py`, por lo que la app funciona sin
modificaciones en Python 3.14. Verificado.
