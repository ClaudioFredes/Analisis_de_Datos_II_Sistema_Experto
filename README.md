# ORIENTAI — Sistema Experto de Orientación Vocacional

**ORIENTAI** recomienda carreras universitarias y terciarias a partir de los intereses del usuario, cruzando el modelo psicométrico **RIASEC (Holland)** con el estándar ocupacional **O\*NET**. Diseñado para jóvenes de 17–20 años en proceso de orientación vocacional. Corre íntegramente en el navegador, sin backend, sin red y sin persistir datos.

---

## Stack técnico

| Capa | Tecnología |
|---|---|
| UI + lógica | **Streamlit** (stateless, en memoria) |
| Cálculo vectorial | **NumPy** — similitud de coseno + correlación de Pearson |
| Visualización | **Plotly** — Radar Chart RIASEC |
| Tests de motor | `tests/test_perfiles.py` (Python estándar) |

---

## Estructura del proyecto

```
.
├── app.py                      # State machine: 7 etapas del flujo
├── build_catalog.py            # Genera data/carreras.json (offline, determinista)
├── requirements.txt
│
├── .streamlit/
│   └── config.toml             # Tema monocromático (paper/ink)
│
├── assets/
│   └── ORIENTAI.SVG.svg
│
├── data/
│   ├── carreras.json           # Catálogo: 90 carreras con vectores RIASEC + universidades
│   ├── dominios.json           # 6 dominios vocacionales y sus carreras
│   └── preguntas.json          # Banco de preguntas F1, tríadas F2, pathways F3
│
├── engine/
│   ├── inference.py            # Vector usuario + scoring híbrido + pairwise + ranking
│
├── ui/
│   ├── header.py               # Navbar: logo + título
│   ├── keyboard.py             # Puente JS para atajos 1–5 + Enter
│   ├── styles.py               # CSS Neo-Brutalismo Gamificado
│   └── visualizations.py       # Radar Chart + tarjetas de recomendación
│
├── scripts/
│   ├── auditoria_onet.py       # Auditoría de fidelidad de vectores vs O*NET
│   ├── montecarlo.py           # Simulación 500×3 escenarios + calibración
│   └── add_universidades.py    # Inyecta datos de universidades en carreras.json
│
└── tests/
    └── test_perfiles.py        # 15 tests del pipeline con perfiles sintéticos
```

---

## Instalación y uso

```bash
pip install -r requirements.txt
python -m streamlit run app.py    # → http://localhost:8501

# Regenerar catálogo desde la tabla O*NET
python build_catalog.py
python build_catalog.py --dry-run

# Tests del motor
python tests/test_perfiles.py
```

---

## Flujo de tres fases (33 preguntas · ~10 minutos)

```
F1 (18q Likert) → TRANSICIÓN → F2 (10 tríadas) → TRANS_F3 → F3 (5q bipolar) → RESULTADOS
```

### Fase 1 · Detección de dominio (18 preguntas)

Preguntas Likert 1–5 sobre actividades generales organizadas en 6 dominios vocacionales:
**Tecnología, Ciencias, Salud, Arte, Negocios, Humanidades.**

El sistema promedia las respuestas por dominio y rankea los 6 según afinidad. El usuario elige el dominio sobre el que quiere profundizar.

### Transición · Selección de dominio y duración

El usuario selecciona el dominio a explorar (con score visual) y su preferencia de duración de carrera (tecnicatura 2–3 años / licenciatura 4–6 años).

### Fase 2 · Construcción del vector RIASEC (10 tríadas)

Comparaciones forzadas: el usuario elige 1 de 3 actividades. Cada opción pertenece a una dimensión RIASEC distinta. El sistema computa el vector del usuario mediante **scoring pairwise**:

```
score_dim = 1 + (wins_dim / appearances_dim) × 4   →   rango [1.0, 5.0]
```

### Transición F3 · Presentación del perfil

Muestra el **radar chart RIASEC** del usuario y el **pathway detectado** dentro del dominio (p. ej. "Analítica & Software" dentro de Tecnología). El pathway se selecciona según la dimensión dominante del vector.

### Fase 3 · Ajuste por valores y contexto (5 preguntas)

Escala bipolar 1–5: cada pregunta enfrenta dos polos de valores o contexto laboral (ej. *Autonomía* ↔ *Trabajo en equipo*). Las respuestas aplican **boosts continuos** al score de las carreras:

```
factor = (respuesta − 3) / 2   →   rango [−1, +1]
boost_carrera += boosts_polo_x[carrera] × |factor|
```

---

## Motor lógico: RIASEC + O\*NET

### Vectores de carrera

Cada carrera mapea a un código SOC de O\*NET. Los valores (escala 1–7) se reescalan a 1–5 **sin redondear** (float):

```
riasec[d] = 1 + (onet_valor[d] − 1) / 6 × 4
```

El paso a float fue crítico: la versión con redondeo a enteros colapsaba 16 carreras en 7 vectores idénticos, generando "carreras imán" por artefacto de orden de lista.

### Scoring híbrido (Coseno + Pearson)

```python
score = 0.3 × coseno + 0.7 × pearson
afinidad_pct = round(100 × max(0, score))
```

- **Coseno** (sobre vectores 1–5 sin centrar): alineación direccional, sensible a la intensidad del interés.
- **Pearson** (coseno sobre vectores centrados): similitud de *forma* del perfil, invariante al sesgo de quien responde alto o bajo en todo.

El peso **0.3/0.7** fue calibrado mediante simulación Monte Carlo: el coseno sobre el ortante positivo 1–5 está comprimido (~0.99) y aporta poca discriminación; el óptimo es Pearson-dominante.

**Desempate neutral:** a igual score, por Pearson descendente y luego `id` alfabético.

**Guardia de varianza nula:** si el usuario responde todo igual, `afinidad_pct = 0` para todas y la app avisa.

### Pathways y boosts F3

Cada dominio tiene 3 pathways (perfiles dentro del dominio), cada uno con 5 preguntas de valores calibradas para discriminar entre las carreras del subconjunto. Los boosts se acumulan sobre el score RIASEC antes del ranking final.

---

## Catálogo

| Ítem | Valor |
|---|---|
| Carreras | 90 |
| Dominios | 6 |
| Pathways | 18 (3 por dominio) |
| Universidades mapeadas | ~90 carreras con datos de instituciones argentinas |
| Fuente RIASEC | O\*NET Interests v28.x |

---

## Arquitectura de UI: Neo-Brutalismo Gamificado

### Paleta ORIENTAI

```css
--ink:    #111111   /* bordes, sombras, texto */
--paper:  #f6f1e7   /* fondo principal */
--card:   #fffdf8   /* fondo de tarjetas */
--violet: #c4b5fd   /* acento primario (botones de avance, selección) */
--lime:   #c6ff4d   /* acento secundario (hover, selección activa) */
```

### Principios visuales

- **Neo-Brutalismo:** bordes 2px sólidos `#111111`, sombra `4px 4px 0px #111111`, sin gradientes. Los elementos se "presionan" al interactuar.
- **Gamificación:** teclas físicas como badges (atajos 1–5 + Enter en quiz).
- **Fondo papel técnico:** patrón de puntos con `radial-gradient` (1px cada 22px).

### Navegación por teclado (quiz)

`ui/keyboard.py` inyecta un puente JavaScript que conecta teclas físicas con la UI de Streamlit:

- **1–5** seleccionan la opción de la escala (Likert en F1, bipolar en F3).
- **Enter** hace click en el botón primario (avanzar).

---

## Tests

```bash
python tests/test_perfiles.py   # → 15/15 OK
```

15 casos con perfiles sintéticos que verifican:
- Propiedades del pipeline RIASEC (social, artístico, realista, vector nulo, extremo, multipotencial).
- Corrección del motor híbrido (coseno ≠ pearson, sin colisiones de vectores, desempate neutral, sin castigo al cubo).
- Corrección de `calcular_vector_pairwise` (dimensión dominante, dimensión ausente, rango válido).
- Edge cases históricos (perfil Instrumentadora R+C, perfil plano).

---

## Créditos

- Banco de preguntas F1 adaptado del **O\*NET Interest Profiler** (dominio público, U.S. Department of Labor).
- Puntajes RIASEC por ocupación: **O\*NET Interests v28.x** (onetonline.org).
- Proyecto académico — Análisis de Datos II.
