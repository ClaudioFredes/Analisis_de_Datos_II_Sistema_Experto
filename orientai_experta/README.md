# ORIENTAI · versión por REGLAS (Experta)

Reimplementación del sistema experto vocacional usando un **motor de reglas**
(Experta / forward-chaining) en lugar de la similitud numérica (coseno/Pearson)
de la versión original. Cubre las **90 carreras** de los **6 dominios** (una
carrera puede pertenecer a varios).

> Esta carpeta es **independiente**: no modifica el proyecto original. Lee el
> catálogo original en **solo lectura** (vía `build_kb.py`) para derivar su base
> de conocimiento.

---

## Qué cambia respecto a la versión original

| | Original | Esta versión (reglas) |
|---|---|---|
| Razonamiento | Similitud de coseno + Pearson (vectores) | **Reglas Experta** (hechos + forward-chaining) |
| Resultado | Ranking continuo con % de afinidad | Ranking por **certeza** (suma de reglas) |
| Explicación | Implícita | **Explícita**: cada recomendación lista las reglas que la sostienen |
| Desempate | — | **Afinidad** continua (intensidad del perfil sobre el código de la carrera) |

Las 3 fases y la base de conocimiento (vectores RIASEC de O\*NET) se conservan;
lo que cambia es el **motor**.

**Las 3 fases (interfaz):**
1. **F1 · Dominio** — 18 preguntas Likert (reusadas del original) -> puntaje por dominio -> el usuario elige uno de los 6.
2. **F2 · Perfil RIASEC** — **tríadas** (comparación forzada *1 de 3*, como el sistema
   original), con la fórmula pairwise `score = 1 + (victorias / apariciones) × 4`.
3. **F3 · Valores (pathway)** — se detecta un *pathway* (sub-perfil) por la dimensión dominante
   y sus 5 preguntas bipolares aplican **boosts a carreras específicas** (igual que el original),
   ajustando finamente el ranking. *(El motor también soporta vetos/deal-breakers, opcionales.)*

El perfil que sale de F2 alimenta el motor de reglas (no cambia nada del motor).

---

## Cómo razona (las reglas)

- **R1 · Holland** — Si la carrera está en el dominio elegido y sus letras
  RIASEC dominantes coinciden con los intereses *altos* del usuario, concluye una
  recomendación. Letra dominante = +3, secundaria = +2, terciaria = +1.
- **R2 · Veto** — Si el usuario vetó una etiqueta (deal-breaker, ej.
  `contacto_pacientes`), **retracta** toda recomendación de carreras que la tengan.
- **R3 · Ajuste de Fase 3** — Aplica los *boosts del pathway* (calculados de las
  preguntas bipolares, `boost = boost_carrera × |factor|`) a las carreras concretas que
  cada respuesta favorece. Es lo que da el "acercamiento fino" al resultado, como el original
  (ej. sube *Ciencia de Datos* sobre *Ing. en Sistemas*).

El puntaje (*certeza*) no es una métrica geométrica: es la **acumulación de
certeza de las reglas que dispararon**. Cuando dos carreras empatan en certeza,
se ordenan por **afinidad** — la intensidad real del perfil del usuario sobre las
letras del código de la carrera (ponderada por posición). Así el ranking final
es fino sin dejar de estar dirigido por reglas.

---

## Estructura

```
orientai_experta/
├── compat.py             # shims para correr Experta en Python 3.10+/3.14
├── build_kb.py           # genera data/carreras_reglas.json desde el catálogo original
├── motor_reglas.py       # KnowledgeEngine: hechos + reglas R1/R2/R3
├── app_reglas.py         # UI Streamlit de 3 fases
├── test_motor.py         # tests del motor (4 casos)
├── requirements.txt
└── data/
    ├── carreras_reglas.json    # base de conocimiento (90 carreras, 6 dominios, código Holland)
    ├── f1_reglas.json          # preguntas de F1 (18, reusadas del original)
    ├── triadas_reglas.json     # tríadas de F2 (comparación 1-de-3, reusadas del original)
    └── fase3_reglas.json       # F3: pathways + bipolares con boosts por carrera (reusadas del original)
```

---

## Instalación y uso

```bash
pip install -r requirements.txt

# (opcional) regenerar la base de conocimiento desde el catálogo original
python build_kb.py

# tests del motor
python test_motor.py            # -> 4/4 tests OK

# correr la app
python -m streamlit run app_reglas.py   # -> http://localhost:8501
```

---

## ⚠️ Compatibilidad de Experta

Experta (último release 2018) **no es compatible de fábrica** con Python 3.10+:
- `frozendict==1.2` usa `collections.Mapping` (movido a `collections.abc` en 3.10).
- Experta usa `inspect.getargspec` (removido en 3.11).

`compat.py` aplica ambos *shims* y se importa automáticamente desde
`motor_reglas.py`, así que la app corre tal cual en Python 3.14. Verificado.

---

## Alcance y próximos pasos

- **Catálogo completo:** 90 carreras en 6 dominios (12 carreras pertenecen a más
  de un dominio). Generado por `build_kb.py` desde el catálogo original.
- **Desempate:** la certeza por reglas se afina con la *afinidad* continua.
- Posibles mejoras: usar los niveles (bajo/medio/alto) dentro del match, reglas
  expertas específicas (ej. demover carreras comerciales para perfiles de salud,
  replicando el caso Instrumentadora/Martillero), y portar el estilo visual del
  proyecto original.
