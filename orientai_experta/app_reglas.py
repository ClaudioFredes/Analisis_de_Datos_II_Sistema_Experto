# -*- coding: utf-8 -*-
"""
ORIENTAI — Sistema experto de orientación vocacional. App Streamlit de 3 fases.

  F1  Detección de dominio   (Likert -> puntaje por dominio -> el usuario elige)
  F2  Perfil RIASEC          (tríadas 1-de-3 -> perfil RIASEC del usuario)
  F3  Valores (pathway)      (preguntas bipolares -> boosts por carrera específica)
  -> Resultados              (motor de reglas Experta, con explicación)

Ejecutar:  python -m streamlit run app_reglas.py
"""
import json
from pathlib import Path

import streamlit as st

from motor_reglas import (recomendar, letras_altas, seleccionar_pathway,
                          boosts_de_fase3, NOMBRES)

AQUI = Path(__file__).resolve().parent
DIMS = ("R", "I", "A", "S", "E", "C")
LIKERT = {1: "Nada", 2: "Poco", 3: "Neutro", 4: "Bastante", 5: "Mucho"}



@st.cache_data
def cargar():
    kb = json.loads((AQUI / "data" / "carreras_reglas.json").read_text("utf-8"))
    tri = json.loads((AQUI / "data" / "triadas_reglas.json").read_text("utf-8"))
    f1 = json.loads((AQUI / "data" / "f1_reglas.json").read_text("utf-8"))
    f3 = json.loads((AQUI / "data" / "fase3_reglas.json").read_text("utf-8"))
    return kb, tri, f1, f3


KB, TRI_DATA, F1_DATA, F3_DATA = cargar()
CARRERAS = KB["carreras"]
CARR_DICT = {c["id"]: c for c in CARRERAS}
DOM_INFO = KB["_meta"]["dominios"]
TRI = TRI_DATA["triadas_por_dominio"]
F1 = F1_DATA["fase1_dominio"]
F3 = F3_DATA["fase3_por_dominio"]
BIPOLAR = {1: "Totalmente ←", 2: "Más bien ←", 3: "Neutro", 4: "Más bien →", 5: "Totalmente →"}

st.set_page_config(page_title="ORIENTAI", page_icon="🧩", layout="centered")

_CSS = """
<style>
/* ── Área principal: más ancha y con más padding ── */
.main .block-container {
    max-width: 860px !important;
    padding-top: 2rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
}

/* ── Títulos ── */
h1  { font-size: 2.4rem !important; }
h2  { font-size: 1.9rem !important; }
h3  { font-size: 1.5rem !important; }

/* ── Texto general y listas ── */
p, li, div.stMarkdown p {
    font-size: 1.1rem !important;
    line-height: 1.65 !important;
}

/* ── Caption ── */
.stCaption p { font-size: 1rem !important; }

/* ── Botones ── */
.stButton > button {
    font-size: 1.05rem !important;
    padding: 0.6rem 1rem !important;
    min-height: 3rem !important;
    height: auto !important;
    line-height: 1.4 !important;
    white-space: pre-line !important;
}

/* ── Barra de progreso ── */
.stProgress > div > div {
    height: 10px !important;
    border-radius: 5px !important;
}
.stProgress > div > div > div > div {
    height: 10px !important;
    border-radius: 5px !important;
}

/* ── Contenedor con borde ── */
[data-testid="stVerticalBlockBorderWrapper"] > div:first-child {
    padding: 1.5rem 1.8rem !important;
}

/* ── Alert boxes (info, success, warning) ── */
div[data-testid="stNotification"] p,
.stAlert p { font-size: 1.05rem !important; }

/* ── Métricas (F2 · perfil RIASEC) ── */
[data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.95rem !important;
}

/* ── Radio buttons ── */
.stRadio div[role="radiogroup"] label {
    font-size: 1.05rem !important;
}

/* ── Expander ── */
.streamlit-expanderHeader p {
    font-size: 1.05rem !important;
}
.streamlit-expanderContent p,
.streamlit-expanderContent li {
    font-size: 1.05rem !important;
}

/* ── Success ── */
div[data-testid="stSuccessMessage"] p {
    font-size: 1.05rem !important;
}
</style>
"""


def apply_css():
    st.markdown(_CSS, unsafe_allow_html=True)


def init():
    st.session_state.setdefault("stage", "bienvenida")
    st.session_state.setdefault("resp_f1", {})
    st.session_state.setdefault("f1_q_idx", 0)
    st.session_state.setdefault("resp_triadas", {})
    st.session_state.setdefault("f2_idx", 0)
    st.session_state.setdefault("dominio", None)
    st.session_state.setdefault("perfil", None)
    st.session_state.setdefault("altos", None)
    st.session_state.setdefault("pathway", None)
    st.session_state.setdefault("resp_f3", {})
    st.session_state.setdefault("f3_q_idx", 0)
    st.session_state.setdefault("dur_pref", "ambas")


def ir(stage):
    st.session_state["stage"] = stage
    st.rerun()


# ─────────────────────────────────────────────────────────────
def pantalla_bienvenida():
    st.title("🧩 ORIENTAI")
    st.caption("Sistema experto de orientación vocacional — 90 carreras, 6 dominios")
    st.markdown(
        """
Este sistema recomienda carreras con un **motor de reglas** (forward-chaining),
no con similitud numérica. El razonamiento es **simbólico y explicable**: cada
recomendación se justifica con las reglas que la dispararon.

**Tres fases:**
1. **Dominio** — detectamos cuál de los 6 mundos vocacionales te atrae más.
2. **Perfil RIASEC** — comparaciones *1 de 3* que construyen tus intereses dominantes.
3. **Valores y contexto** — preguntas del *pathway* detectado que refuerzan carreras concretas (ajuste fino).
        """
    )
    st.info(f"Base de conocimiento: **{len(CARRERAS)} carreras** · "
            f"motor: **Experta** (reglas R1 Holland · R3 Valor · E1–E4 expertas)")
    if st.button("Comenzar →", type="primary", use_container_width=True):
        ir("f1")


# ─────────────────────────────────────────────────────────────
def pantalla_f1():
    total = len(F1)
    idx = st.session_state["f1_q_idx"]
    if idx >= total:
        ir("f1_elegir")
        return

    q = F1[idx]
    st.subheader(f"Fase 1 · Pregunta {idx + 1} de {total}")
    st.caption("¿Cuánto te gustaría hacer esta actividad?")
    st.progress(idx / total)
    st.markdown("&nbsp;", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f"**{q['texto']}**")
        st.markdown("")
        cols = st.columns(5, gap="small")
        for v, label in LIKERT.items():
            if cols[v - 1].button(f"{v} · {label}", key=f"f1_{q['id']}_{v}",
                                  use_container_width=True):
                st.session_state["resp_f1"][q["id"]] = v
                if idx >= total - 1:
                    ir("f1_elegir")
                else:
                    st.session_state["f1_q_idx"] = idx + 1
                    st.rerun()

    if idx > 0:
        st.markdown("---")
        if st.button("← Anterior", key="f1_prev"):
            st.session_state["f1_q_idx"] = idx - 1
            st.rerun()


def pantalla_f1_elegir():
    resp = st.session_state["resp_f1"]
    # Puntaje por dominio = promedio de sus actividades
    puntajes = {}
    for dom in DOM_INFO:
        vals = [resp[q["id"]] for q in F1 if q["dominio"] == dom]
        puntajes[dom] = round(sum(vals) / len(vals), 2) if vals else 0
    ranking = sorted(puntajes.items(), key=lambda kv: -kv[1])

    st.subheader("Fase 1 · Tu afinidad por dominio")
    for dom, p in ranking:
        info = DOM_INFO[dom]
        st.markdown(f"**{info['icono']} {info['nombre']}** — {p}/5")
        st.progress(p / 5)

    recomendado = ranking[0][0]
    st.markdown("#### ¿Sobre qué dominio querés profundizar?")
    opciones = list(DOM_INFO.keys())
    dom = st.radio(
        "dominio", opciones,
        index=opciones.index(recomendado),
        format_func=lambda d: f"{DOM_INFO[d]['icono']} {DOM_INFO[d]['nombre']}"
        + ("  ⭐ recomendado" if d == recomendado else ""),
        label_visibility="collapsed",
    )

    st.markdown("**¿Qué duración preferís?**")
    dur_pref = st.radio(
        "dur", ["ambas", "tecnicatura", "grado"],
        format_func=lambda v: {"ambas": "↔ Indiferente",
                               "tecnicatura": "⚡ Tecnicatura (2-3 años)",
                               "grado": "🎓 Licenciatura / Ingeniería (4-6 años)"}[v],
        horizontal=True, label_visibility="collapsed",
    )

    c1, c2 = st.columns(2)
    if c1.button("← Volver", use_container_width=True):
        st.session_state["f1_q_idx"] = 0
        st.session_state["resp_f1"] = {}
        ir("f1")
    if c2.button("Continuar a Fase 2 →", type="primary", use_container_width=True):
        st.session_state["dominio"] = dom
        st.session_state["dur_pref"] = dur_pref
        ir("f2")


# ─────────────────────────────────────────────────────────────
def _perfil_de_triadas(elecciones, triadas):
    """Fórmula pairwise: score_dim = 1 + (victorias_dim / apariciones_dim) * 4  (3.0 si no aparece)."""
    wins = {d: 0 for d in DIMS}
    apps = {d: 0 for d in DIMS}
    tmap = {t["id"]: t for t in triadas}
    for tid, op_id in elecciones.items():
        t = tmap.get(tid)
        if not t:
            continue
        for op in t["opciones"]:
            if op["dimension"] in apps:
                apps[op["dimension"]] += 1
        for op in t["opciones"]:
            if op["id"] == op_id:
                wins[op["dimension"]] += 1
                break
    return {d: round(1 + (wins[d] / apps[d]) * 4, 2) if apps[d] else 3.0 for d in DIMS}


def pantalla_f2():
    dom = st.session_state["dominio"]
    triadas = TRI.get(dom, [])
    total = len(triadas)
    if total == 0:
        ir("f2_perfil")
        return
    idx = min(st.session_state["f2_idx"], total - 1)
    t = triadas[idx]

    st.subheader(f"Fase 2 · Comparación {idx + 1} de {total}")
    st.caption("Elegí la actividad que **más te atraería** (comparación forzada, 1 de 3).")
    st.progress(idx / total)
    st.markdown("&nbsp;", unsafe_allow_html=True)

    cols = st.columns(3, gap="medium")
    for i, op in enumerate(t["opciones"]):
        if cols[i].button(op["texto"], key=f"tri_{t['id']}_{i}", use_container_width=True):
            st.session_state["resp_triadas"][t["id"]] = op["id"]
            if idx >= total - 1:
                ir("f2_perfil")
            else:
                st.session_state["f2_idx"] = idx + 1
                st.rerun()

    if idx > 0:
        st.markdown("---")
        if st.button("← Anterior", key="tri_prev"):
            st.session_state["f2_idx"] = idx - 1
            st.rerun()


def pantalla_f2_perfil():
    dom = st.session_state["dominio"]
    triadas = TRI.get(dom, [])
    perfil = _perfil_de_triadas(st.session_state["resp_triadas"], triadas)
    st.session_state["perfil"] = perfil
    altos = letras_altas(perfil)
    st.session_state["altos"] = altos

    st.subheader("Fase 2 · Tu perfil detectado")
    cols = st.columns(6)
    for i, d in enumerate(DIMS):
        marca = "🔶" if d in altos else "▫️"
        cols[i].metric(f"{marca} {d}", perfil[d])
    st.success("Tus intereses **altos**: " +
               " · ".join(f"{d} ({NOMBRES[d]})" for d in altos))
    st.caption("Salen de tus elecciones en las comparaciones (fórmula "
               "victorias / apariciones). Son las letras que el motor usará para "
               "emparejar con el código Holland de cada carrera.")

    c1, c2 = st.columns(2)
    if c1.button("↻ Rehacer comparaciones", use_container_width=True):
        st.session_state["resp_triadas"] = {}
        st.session_state["f2_idx"] = 0
        ir("f2")
    if c2.button("Continuar a Fase 3 →", type="primary", use_container_width=True):
        ir("f3")


# ─────────────────────────────────────────────────────────────
def pantalla_f3():
    dom = st.session_state["dominio"]
    perfil = st.session_state["perfil"]
    pathway = seleccionar_pathway(F3.get(dom, []), perfil)
    st.session_state["pathway"] = pathway

    if not pathway:
        st.session_state["resp_f3"] = {}
        ir("resultados")
        return

    preguntas = pathway.get("preguntas", [])
    total = len(preguntas)
    idx = st.session_state["f3_q_idx"]
    if idx >= total:
        ir("resultados")
        return

    q = preguntas[idx]
    st.subheader(f"Fase 3 · Pregunta {idx + 1} de {total}")
    st.info(f"**{pathway['nombre']}** — {pathway.get('descripcion', '')}")
    st.progress(idx / total)
    st.markdown("&nbsp;", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f"**{q['pregunta']}**")
        st.markdown("")
        ca, cb = st.columns(2)
        ca.caption(f"← {q['polo_a']}")
        cb.markdown(f"<div style='text-align:right;color:#888;font-size:.875rem'>"
                    f"{q['polo_b']} →</div>", unsafe_allow_html=True)
        st.markdown("")
        cols = st.columns(5, gap="small")
        for v, label in BIPOLAR.items():
            if cols[v - 1].button(label, key=f"f3_{q['id']}_{v}",
                                  use_container_width=True):
                st.session_state["resp_f3"][q["id"]] = v
                if idx >= total - 1:
                    ir("resultados")
                else:
                    st.session_state["f3_q_idx"] = idx + 1
                    st.rerun()

    if idx > 0:
        st.markdown("---")
        if st.button("← Anterior", key="f3_prev"):
            st.session_state["f3_q_idx"] = idx - 1
            st.rerun()


# ─────────────────────────────────────────────────────────────
def pantalla_resultados():
    dom = st.session_state["dominio"]
    perfil = st.session_state["perfil"]
    altos = st.session_state["altos"]
    pathway = st.session_state.get("pathway")
    resp_f3 = st.session_state.get("resp_f3", {})

    boosts = boosts_de_fase3(pathway, resp_f3) if pathway else {}
    dur_pref = st.session_state.get("dur_pref", "ambas")
    recos = recomendar(CARRERAS, dom, perfil, boosts_f3=boosts, dur_pref=dur_pref)

    info = DOM_INFO[dom]
    st.subheader(f"Resultados · {info['icono']} {info['nombre']}")
    cap = f"Perfil alto en: {' · '.join(altos)}"
    if pathway:
        cap += f"  ·  pathway: {pathway['nombre']}"
    st.caption(cap)

    if not recos:
        st.warning("No hay carreras que recomendar para este perfil.")
        if st.button("🔄 Empezar de nuevo"):
            reiniciar()
        return

    st.markdown("#### Top 5 recomendadas")
    for i, r in enumerate(recos[:5], 1):
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            adj = r["boost"]
            marca = " ▲" if adj > 0 else (" ▼" if adj < 0 else "")
            extra = f" · ajuste {adj:+.2f}" if adj else ""
            c1.markdown(f"**{i}. {r['nombre']}{marca}**  \n"
                        f"<span style='color:#888'>código Holland: {'-'.join(r['code'])} · "
                        f"afinidad {r['afinidad']}{extra}</span>", unsafe_allow_html=True)
            c2.metric("certeza", r["score"])
            with st.expander("¿Por qué? (reglas que la sostienen)"):
                for m in r["motivos"]:
                    st.markdown(f"- {m}")
                univs = CARR_DICT.get(r["id"], {}).get("universidades", [])
                if univs:
                    st.markdown("**🏛 Dónde estudiarla:**")
                    for u in univs:
                        st.markdown(f"- **{u['nombre']}** — {u['ciudad']}")
    if any(r["boost"] for r in recos[:5]):
        st.caption("▲ / ▼ = la **Fase 3** y las **reglas expertas** ajustaron la posición de la carrera.")

    with st.expander("🧠 Cómo razonó el sistema (reglas aplicadas)"):
        n_f3 = sum(1 for r in recos if r.get("f3"))
        exp_desc = {"E1": "E1 anti-confound", "E2": "E2 rechazo del rasgo dominante",
                    "E3": "E3 alineación principal", "E4": "E4 preferencia de duración"}
        reglas_exp = sorted({rg for r in recos for rg in r["reglas"]})
        st.markdown(
            f"""
- **R1 · Holland**: emparejó tu perfil (**{', '.join(altos)}**) con el código de
  cada carrera del dominio *{info['nombre']}*. Dominante = +3, secundaria = +2, terciaria = +1.
- **R3 · Fase 3**: { f'el pathway *{pathway["nombre"]}* reforzó {n_f3} carreras concretas según tus respuestas bipolares.' if pathway and n_f3 else 'el pathway no movió el ranking (respuestas neutrales).' }
- **Reglas expertas**: { ', '.join(exp_desc[e] for e in reglas_exp) if reglas_exp else 'no se activaron' }.

El orden final es **certeza + ajustes** (Fase 3 + reglas expertas); ante empates,
**afinidad** (intensidad del perfil sobre el código). Todo es explicable y
dirigido por reglas.
            """
        )

    if st.button("🔄 Empezar de nuevo", use_container_width=True):
        reiniciar()


def reiniciar():
    for k in ("stage", "resp_f1", "f1_q_idx", "resp_triadas", "f2_idx",
              "dominio", "perfil", "altos", "pathway", "resp_f3", "f3_q_idx", "dur_pref"):
        st.session_state.pop(k, None)
    init()
    st.rerun()


# ─────────────────────────────────────────────────────────────
def main():
    apply_css()
    init()
    router = {
        "bienvenida": pantalla_bienvenida,
        "f1": pantalla_f1,
        "f1_elegir": pantalla_f1_elegir,
        "f2": pantalla_f2,
        "f2_perfil": pantalla_f2_perfil,
        "f3": pantalla_f3,
        "resultados": pantalla_resultados,
    }
    router.get(st.session_state["stage"], pantalla_bienvenida)()


main()
