"""
=================================================================
SISTEMA EXPERTO VOCACIONAL v5 — Tres fases
=================================================================
  F1 (18q Likert)  →  TRANSICIÓN  →  F2 (tríadas 1-de-3)
  →  TRANS_F3  →  F3 (5q pathway)  →  RESULTADOS
=================================================================
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import streamlit as st

from engine.inference import (
    DIMENSIONES_RIASEC,
    calcular_vector_pairwise,
    get_peso_coseno,
    ranking_carreras,
    seleccionar_pathway,
    aplicar_boosts_f3,
)
from ui.header import render_header
from ui.keyboard import inyectar_navegacion_teclado
from ui.styles import inject_css
from ui.visualizations import (
    ETIQUETAS_RIASEC,
    radar_chart_riasec,
    tarjeta_recomendacion,
)

DATA_DIR       = Path(__file__).parent / "data"
PATH_CARRERAS  = DATA_DIR / "carreras.json"
PATH_PREGUNTAS = DATA_DIR / "preguntas.json"
PATH_DOMINIOS  = DATA_DIR / "dominios.json"

ETAPA_BIENVENIDA  = "bienvenida"
ETAPA_F1          = "f1"
ETAPA_TRANSICION  = "transicion"
ETAPA_F2          = "f2"
ETAPA_TRANS_F3    = "trans_f3"
ETAPA_F3          = "f3"
ETAPA_RESULTADOS  = "resultados"
ETAPA_EDITOR      = "editor"

CLAVES_SESION = (
    "etapa",
    "resp_f1", "resp_pairwise", "resp_f3",
    "dominio_activo", "dominios_explorados", "pref_duracion",
    "pathway_activo",
    "vector_usuario", "idx", "orden",
    "_err_idx", "_trans_dom", "_trans_dur",
)

LIKERT = {1: "Lo detestaría", 2: "No me gustaría", 3: "Me da igual",
          4: "Me gustaría", 5: "Me encantaría"}

st.set_page_config(
    page_title="ORIENTAI", page_icon="◼",
    layout="wide", initial_sidebar_state="collapsed",
)
inject_css()


# =================================================================
# CARGA DE DATOS
# =================================================================
@st.cache_data(show_spinner=False)
def cargar_catalogo():
    return json.loads(PATH_CARRERAS.read_text(encoding="utf-8"))["carreras"]

@st.cache_data(show_spinner=False)
def cargar_dominios():
    return json.loads(PATH_DOMINIOS.read_text(encoding="utf-8"))["dominios"]

@st.cache_data(show_spinner=False)
def cargar_f1():
    return json.loads(PATH_PREGUNTAS.read_text(encoding="utf-8"))["preguntas_fase1"]

@st.cache_data(show_spinner=False)
def cargar_pathways(dominio_id: str) -> list[dict]:
    d = json.loads(PATH_PREGUNTAS.read_text(encoding="utf-8"))
    return d.get("fase3_por_dominio", {}).get(dominio_id, [])

@st.cache_data(show_spinner=False)
def cargar_triadas(dominio_id: str):
    d = json.loads(PATH_PREGUNTAS.read_text(encoding="utf-8"))
    return d["triadas_por_dominio"].get(dominio_id, [])

def catalogo_dominio(dominio_id: str):
    doms = cargar_dominios()
    ids = next((set(d["carreras"]) for d in doms if d["id"] == dominio_id), set())
    return [c for c in cargar_catalogo() if c["id"] in ids]


# =================================================================
# ESTADO
# =================================================================
def init_session():
    st.session_state.setdefault("etapa", ETAPA_BIENVENIDA)
    st.session_state.setdefault("resp_f1", {})
    st.session_state.setdefault("resp_pairwise", {})
    st.session_state.setdefault("resp_f3", {})
    st.session_state.setdefault("dominio_activo", None)
    st.session_state.setdefault("dominios_explorados", [])
    st.session_state.setdefault("pref_duracion", "ambas")
    st.session_state.setdefault("pathway_activo", None)
    st.session_state.setdefault("vector_usuario", None)
    st.session_state.setdefault("idx", 0)
    st.session_state.setdefault("orden", None)

def ir_a(etapa):
    st.session_state["etapa"] = etapa
    st.rerun()

def reiniciar():
    for k in CLAVES_SESION:
        st.session_state.pop(k, None)
    init_session()
    st.rerun()

def calcular_scores():
    pf1  = cargar_f1()
    doms = cargar_dominios()
    resp = st.session_state.get("resp_f1", {})
    acum = {d["id"]: [] for d in doms}
    for p in pf1:
        v = resp.get(p["id"])
        if v is not None:
            acum[p["dominio"]].append(float(v) * p.get("ponderacion", 1.0))
    prom = {did: round(sum(vs)/len(vs), 2) if vs else 0.0 for did, vs in acum.items()}
    return sorted(prom.items(), key=lambda x: -x[1])


# =================================================================
# PANTALLAS
# =================================================================

# ── BIENVENIDA ──────────────────────────────────────────────────
def pantalla_bienvenida():
    render_header()
    st.markdown("##### Descubrí qué carreras se ajustan mejor a tus intereses.")
    st.markdown("---")
    st.markdown("""
Este sistema analiza tus intereses y los cruza con el perfil de cada carrera
usando el estándar **O\\*NET** y el modelo **RIASEC** de Holland.

**Tres fases:**
1. **Fase 1 · 18 preguntas** — respondés actividades generales (escala 1-5).
   El sistema detecta qué dominio te atrae más.
2. **Fase 2 · 10 comparaciones** — elegís entre tres actividades dentro de tu
   dominio para construir tu perfil RIASEC detallado.
3. **Fase 3 · 5 preguntas** — preguntas de valores y contexto laboral
   específicas para tu perfil que afinan el ranking final.

**Total: 33 preguntas · ~10 minutos · Privacidad total.**
    """)
    st.markdown("&nbsp;")
    if st.button("Comenzar →", type="primary", use_container_width=True):
        pf1 = cargar_f1()[:]
        random.shuffle(pf1)
        st.session_state["orden"] = [{"tipo": "f1", "item": p} for p in pf1]
        st.session_state["idx"]   = 0
        st.session_state["resp_f1"] = {}
        ir_a(ETAPA_F1)

    st.markdown("&nbsp;")
    st.markdown(
        "<div style='text-align:center'>",
        unsafe_allow_html=True,
    )
    if st.button("⚙ Panel de administración", type="secondary", use_container_width=False):
        ir_a(ETAPA_EDITOR)
    st.markdown("</div>", unsafe_allow_html=True)


# ── FASE 1 ───────────────────────────────────────────────────────
def pantalla_f1():
    render_header(is_quiz=True)
    orden = st.session_state["orden"]
    total = len(orden)
    idx   = st.session_state["idx"]
    item  = orden[idx]["item"]

    st.markdown("##### Fase 1 — Descubriendo tus intereses")
    with st.container(key="quiz_question"):
        st.markdown(f"### ¿Cuánto te gustaría {item['pregunta'].lower()}?")

    resp = st.session_state["resp_f1"]
    prev = resp.get(item["id"])
    opts = list(LIKERT.keys())
    sel = st.radio("r", opts, format_func=lambda v: LIKERT[v],
                   index=opts.index(prev) if prev is not None else None,
                   horizontal=True, label_visibility="collapsed",
                   key=f"rf1_{item['id']}")

    nueva = sel is not None and sel != prev
    if sel is not None:
        resp[item["id"]] = int(sel)

    if st.session_state.get("_err_idx") == idx:
        st.error("Seleccioná una opción para continuar.")

    st.markdown('<div class="keyboard-hint">Teclas <strong>1–5</strong> · <strong>Enter</strong> para avanzar</div>',
                unsafe_allow_html=True)

    if nueva:
        st.session_state.pop("_err_idx", None)
        if idx == total - 1:
            ir_a(ETAPA_TRANSICION)
        else:
            st.session_state["idx"] = idx + 1
            st.rerun()

    _botonera(idx, resp.get(item["id"]) is not None,
              es_ultima=(idx == total - 1),
              label_next="Ver mis dominios →" if idx == total - 1 else "Siguiente →",
              on_next=lambda: ir_a(ETAPA_TRANSICION) if idx == total - 1
                              else _set_idx(idx + 1))

    _barra(idx + 1, total, "Fase 1", fase=1)
    inyectar_navegacion_teclado(num_opciones=len(LIKERT))


# ── TRANSICIÓN ───────────────────────────────────────────────────
def pantalla_transicion():
    render_header()
    scores     = calcular_scores()
    doms       = cargar_dominios()
    dom_map    = {d["id"]: d for d in doms}
    explorados = st.session_state.get("dominios_explorados", [])

    # Dominio pre-seleccionado: el mejor no explorado
    recomendado = next((did for did, _ in scores if did not in explorados), scores[0][0])
    if "_trans_dom" not in st.session_state:
        st.session_state["_trans_dom"] = recomendado

    st.markdown("##### ¿Sobre qué mundo querés profundizar?")
    st.markdown("---")

    col_doms, col_gap, col_accion = st.columns([3, 0.15, 1.6])

    # CSS: cards partido en dos botones (nombre | barra) que parecen uno
    st.markdown("""
    <style>
    /* Gap entre filas de tarjetas */
    .st-key-dom_cards [data-testid="stVerticalBlock"] { gap: 0.3rem !important; }

    /* Sin gap entre las dos mitades de cada tarjeta */
    .st-key-dom_cards [data-testid="stHorizontalBlock"] { gap: 0 !important; }

    /* Estilos base de ambas mitades */
    .st-key-dom_cards .stButton > button {
        height: 2.6rem !important;
        white-space: nowrap !important;
        padding: 0.4rem 0.8rem !important;
        font-size: 0.88rem !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        border-bottom-width: 2px !important;
        border-top-width: 2px !important;
    }
    /* Mitad izquierda: borde izquierdo + radio izquierdo */
    .st-key-dom_cards [data-testid="stHorizontalBlock"] > div:first-child .stButton > button {
        border-left-width: 2px !important;
        border-right-width: 1px !important;
        border-radius: 8px 0 0 8px !important;
        text-align: left !important;
    }
    /* Mitad derecha: borde derecho + radio derecho + sombra al conjunto */
    .st-key-dom_cards [data-testid="stHorizontalBlock"] > div:last-child .stButton > button {
        border-left-width: 1px !important;
        border-right-width: 2px !important;
        border-radius: 0 8px 8px 0 !important;
        text-align: right !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
        box-shadow: 3px 3px 0px var(--ink) !important;
    }
    /* Seleccionado: lime en ambas mitades */
    .st-key-dom_cards .stButton > button[kind="primary"] {
        background-color: var(--lime) !important;
        color: var(--ink) !important;
    }

    /* Duración: botones sin margen extra */
    .st-key-dur_buttons [data-testid="stVerticalBlock"] { gap: 0.3rem !important; }
    .st-key-dur_buttons .stButton > button {
        font-size: 0.84rem !important;
        white-space: nowrap !important;
        height: 2.6rem !important;
    }
    .st-key-dur_buttons .stButton > button[kind="primary"] {
        background-color: var(--lime) !important;
        color: var(--ink) !important;
    }

    /* Botón avanzar: hereda el primario global (violeta). */
    </style>
    """, unsafe_allow_html=True)

    with col_doms:
        with st.container(key="dom_cards"):
            for did, score in scores:
                d      = dom_map.get(did, {})
                sel    = st.session_state["_trans_dom"] == did
                es_rec = did == recomendado and did not in explorados
                es_exp = did in explorados
                tag    = " ★" if es_rec else (" ✓" if es_exp else "")
                filled = int(score / 5.0 * 10)
                bar    = "█" * filled + "░" * (10 - filled)
                btn_type = "primary" if sel else "secondary"
                c1, c2 = st.columns([2.6, 1.4])
                with c1:
                    if st.button(f"{d.get('icono','')} {d.get('nombre','')}{tag}",
                                 key=f"btn_name_{did}", type=btn_type,
                                 use_container_width=True):
                        st.session_state["_trans_dom"] = did
                        st.rerun()
                with c2:
                    if st.button(f"{bar}  {score:.1f}/5",
                                 key=f"btn_bar_{did}", type=btn_type,
                                 use_container_width=True):
                        st.session_state["_trans_dom"] = did
                        st.rerun()

    with col_accion:
        dom_sel = st.session_state["_trans_dom"]
        d_info  = dom_map.get(dom_sel, {})
        st.markdown(
            f"""<div style="padding:0.5rem 0.9rem;border:2px solid var(--ink);
                border-radius:10px;background:var(--violet);box-shadow:3px 3px 0 var(--ink);
                margin-bottom:0.8rem;display:flex;align-items:center;gap:0.5rem;">
                <span style="font-size:1.3rem;">{d_info.get('icono','')}</span>
                <span style="font-weight:700;font-size:0.95rem;">{d_info.get('nombre','')}</span>
            </div>""",
            unsafe_allow_html=True,
        )

        st.markdown("**Duración preferida:**")
        if "_trans_dur" not in st.session_state:
            st.session_state["_trans_dur"] = "ambas"
        dur_opts = [
            ("tecnicatura", "⚡ Tecnicatura  (2-3 años)"),
            ("ambas",       "↔ Indiferente"),
            ("grado",       "🎓 Licenciatura  (4-6 años)"),
        ]
        with st.container(key="dur_buttons"):
            for val, label in dur_opts:
                sel_dur = st.session_state["_trans_dur"] == val
                if st.button(label, key=f"dur_{val}",
                             type="primary" if sel_dur else "secondary",
                             use_container_width=True):
                    st.session_state["_trans_dur"] = val
                    st.rerun()
        dur = st.session_state["_trans_dur"]

        st.markdown("&nbsp;")
        if st.button("Comenzar Fase 2 →", type="primary", use_container_width=True):
            st.session_state["dominio_activo"] = dom_sel
            st.session_state["pref_duracion"]  = dur
            st.session_state.pop("_trans_dom", None)
            st.session_state.pop("_trans_dur", None)
            _init_f2(dom_sel)


# ── FASE 2 — TRÍADAS (1 de 3) ────────────────────────────────────
def _init_f2(dominio_id):
    triadas = cargar_triadas(dominio_id)[:]
    random.shuffle(triadas)
    st.session_state["orden"]         = [{"tipo": "triada", "item": t} for t in triadas]
    st.session_state["idx"]           = 0
    st.session_state["resp_pairwise"] = {}
    st.session_state.pop("_err_idx", None)
    ir_a(ETAPA_F2)

def pantalla_f2():
    render_header(is_quiz=True)
    orden     = st.session_state["orden"]
    total     = len(orden)
    idx       = st.session_state["idx"]
    item      = orden[idx]["item"]
    resp      = st.session_state["resp_pairwise"]
    es_ultima = idx == total - 1

    st.markdown(f"##### Fase 2 — Comparación {idx + 1} de {total}")
    st.markdown("### ¿Cuál de estas actividades te atraería más?")
    st.markdown("&nbsp;")

    elegida_id = resp.get(item["id"])
    clicked_id = None

    with st.container(key="pairwise_row"):
        cols = st.columns(3, gap="large")
        for i, opcion in enumerate(item["opciones"]):
            with cols[i]:
                es_sel = elegida_id == opcion["id"]
                if st.button(
                    opcion["texto"],
                    key=f"pw2_{opcion['id']}",
                    type="primary" if es_sel else "secondary",
                    use_container_width=True,
                ):
                    clicked_id = opcion["id"]

    if clicked_id:
        resp[item["id"]] = clicked_id
        es_nueva = elegida_id is None
        if es_nueva:
            st.session_state.pop("_err_idx", None)
            if es_ultima:
                _finalizar_f2()
            else:
                st.session_state["idx"] = idx + 1
        st.rerun()

    if st.session_state.get("_err_idx") == idx:
        st.error("Elegí una opción para continuar.")

    _botonera(idx, elegida_id is not None, es_ultima,
              label_next="Ver mi perfil →" if es_ultima else "Siguiente →",
              on_next=lambda: _finalizar_f2() if es_ultima else _set_idx(idx + 1))

    _barra(idx + 1, total, "Fase 2 · Comparaciones", fase=2)


def _finalizar_f2():
    """Fin de tríadas F2 → calcula vector RIASEC → selecciona pathway → TRANS_F3."""
    triads = [e["item"] for e in st.session_state["orden"]]
    vector = calcular_vector_pairwise(st.session_state["resp_pairwise"], triads)
    st.session_state["vector_usuario"] = vector
    dom      = st.session_state.get("dominio_activo", "")
    pathways = cargar_pathways(dom)
    if pathways:
        st.session_state["pathway_activo"] = seleccionar_pathway(pathways, vector)
    ir_a(ETAPA_TRANS_F3)


# ── TRANSICIÓN F3 — muestra perfil detectado ─────────────────────
def pantalla_trans_f3():
    render_header()
    pathway = st.session_state.get("pathway_activo")
    if not pathway:
        _init_f3()
        return

    vector = st.session_state.get("vector_usuario")

    # Indicador de etapas
    st.markdown(
        """<div style="display:flex;gap:0.5rem;align-items:center;
            font-size:0.82rem;margin-bottom:1.1rem;flex-wrap:wrap;">
            <span style="padding:3px 10px;background:var(--ink);color:var(--card);
                border-radius:20px;font-weight:700;">✓ Fase 1</span>
            <span style="color:#888;">──</span>
            <span style="padding:3px 10px;background:var(--ink);color:var(--card);
                border-radius:20px;font-weight:700;">✓ Fase 2</span>
            <span style="color:#888;">──</span>
            <span style="padding:3px 10px;background:var(--violet);color:var(--ink);
                border:2px solid var(--ink);border-radius:20px;font-weight:700;">
                → Fase 3 · 5 preguntas</span>
        </div>""",
        unsafe_allow_html=True,
    )

    with st.container(key="trans_f3_layout"):
        col_riasec, col_pathway = st.columns([1.4, 1], gap="large")

        with col_riasec:
            st.markdown("##### Tu perfil RIASEC")
            if vector:
                fig = radar_chart_riasec(vector, titulo="")
                st.plotly_chart(fig, use_container_width=True,
                                config={"scrollZoom": False, "displayModeBar": False,
                                        "doubleClick": False})

        with col_pathway:
            st.markdown("##### Tu perfil detectado")
            st.markdown(
                f"""<div style="padding:1.2rem 1.4rem;border:3px solid var(--ink);
                    border-radius:12px;background:var(--violet);
                    box-shadow:5px 5px 0px var(--ink);margin-bottom:1rem;">
                    <div style="font-size:1.1rem;font-weight:800;margin-bottom:0.35rem;">
                        ✦ {pathway['nombre']}
                    </div>
                    <div style="font-size:0.9rem;line-height:1.5;">
                        {pathway['descripcion']}
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )
            st.markdown(
                "Las **5 preguntas** de la Fase 3 están diseñadas "
                "específicamente para este perfil y afinarán el ranking final."
            )
            st.markdown("&nbsp;")
            if st.button("Comenzar Fase 3 →", type="primary", use_container_width=True):
                _init_f3()


def _init_f3():
    pathway = st.session_state.get("pathway_activo")
    if not pathway:
        _finalizar_completo()
        return
    preguntas = pathway["preguntas"]
    st.session_state["orden"]   = preguntas
    st.session_state["idx"]     = 0
    st.session_state["resp_f3"] = {}
    st.session_state.pop("_err_idx", None)
    ir_a(ETAPA_F3)


# ── FASE 3 — valores y contexto (escala bipolar) ─────────────────
_BIPOLAR_LABELS = {
    1: "Totalmente ←",
    2: "Más bien ←",
    3: "Me da igual",
    4: "Más bien →",
    5: "Totalmente →",
}

def pantalla_f3():
    render_header(is_quiz=True)
    preguntas = st.session_state["orden"]
    total     = len(preguntas)
    idx       = st.session_state["idx"]
    q         = preguntas[idx]
    resp_f3   = st.session_state["resp_f3"]
    es_ultima = idx == total - 1

    st.markdown(f"##### Fase 3 — Pregunta {idx + 1} de {total}")
    with st.container(key="quiz_question"):
        st.markdown(f"### {q['pregunta']}")
    st.markdown("&nbsp;")

    # Polos en columnas para contexto visual
    col_a, col_mid, col_b = st.columns([5, 1, 5])
    with col_a:
        st.markdown(
            f"<div style='padding:0.6rem 0.9rem;border:2px solid var(--ink);"
            f"border-radius:8px;background:var(--card);font-size:0.92rem;"
            f"text-align:center;'>← {q['polo_a']}</div>",
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(
            f"<div style='padding:0.6rem 0.9rem;border:2px solid var(--ink);"
            f"border-radius:8px;background:var(--card);font-size:0.92rem;"
            f"text-align:center;'>{q['polo_b']} →</div>",
            unsafe_allow_html=True,
        )
    st.markdown("&nbsp;")

    prev = resp_f3.get(q["id"])
    opts = [1, 2, 3, 4, 5]
    sel = st.radio(
        "f3r", opts,
        format_func=lambda v: _BIPOLAR_LABELS[v],
        index=opts.index(prev) if prev is not None else None,
        horizontal=True,
        label_visibility="collapsed",
        key=f"rf3_{q['id']}",
    )

    nueva = sel is not None and sel != prev
    if sel is not None:
        resp_f3[q["id"]] = int(sel)

    if st.session_state.get("_err_idx") == idx:
        st.error("Seleccioná una opción para continuar.")

    st.markdown('<div class="keyboard-hint">Teclas <strong>1–5</strong> · <strong>Enter</strong> para avanzar</div>',
                unsafe_allow_html=True)

    if nueva:
        st.session_state.pop("_err_idx", None)
        if es_ultima:
            _finalizar_completo()
        else:
            st.session_state["idx"] = idx + 1
            st.rerun()

    _botonera(idx, resp_f3.get(q["id"]) is not None, es_ultima,
              label_next="Ver resultados →" if es_ultima else "Siguiente →",
              on_next=lambda: _finalizar_completo() if es_ultima else _set_idx(idx + 1))

    _barra(idx + 1, total, "Fase 3 · Valores y contexto", fase=3)
    inyectar_navegacion_teclado(num_opciones=5)


def _finalizar_completo():
    """Marca el dominio explorado y va a resultados."""
    dom = st.session_state.get("dominio_activo")
    if dom:
        exp = list(st.session_state.get("dominios_explorados", []))
        if dom not in exp:
            exp.append(dom)
        st.session_state["dominios_explorados"] = exp
    ir_a(ETAPA_RESULTADOS)


# ── RESULTADOS ───────────────────────────────────────────────────
def pantalla_resultados():
    render_header()
    vector = st.session_state["vector_usuario"]
    if vector is None:
        st.warning("Aún no hay vector calculado.")
        if st.button("Volver al inicio"):
            reiniciar()
        return

    doms     = cargar_dominios()
    dom_map  = {d["id"]: d for d in doms}
    dom_id   = st.session_state.get("dominio_activo", "")
    dom_info = dom_map.get(dom_id, {})
    pref_dur = st.session_state.get("pref_duracion", "ambas")

    icono  = dom_info.get('icono', '')
    nombre = dom_info.get('nombre', '')
    st.markdown(
        f"## Resultados &nbsp; <span style='font-size:1rem;font-weight:400;"
        f"color:#666;'>{icono} {nombre}</span>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    catalogo     = catalogo_dominio(dom_id) if dom_id else cargar_catalogo()
    ranking_base = ranking_carreras(vector, catalogo)
    # Aplicar boosts de Fase 3 si existen
    pathway  = st.session_state.get("pathway_activo")
    resp_f3  = st.session_state.get("resp_f3", {})
    if pathway and resp_f3:
        ranking = aplicar_boosts_f3(ranking_base, resp_f3, pathway["preguntas"])
    else:
        ranking = ranking_base
    top5    = ranking[:5]

    if top5 and top5[0]["afinidad_pct"] == 0:
        st.warning("Patrón de respuestas muy uniforme — intentá marcar más diferencias.")
        if st.button("🔄 Rehacer", type="primary"):
            reiniciar()
        return

    n_cat = len(catalogo)
    if pref_dur == "ambas":
        _show_ranking("Top carreras recomendadas", top5, ranking, n_cat)
    else:
        pref = [c for c in ranking if c.get("duracion") == pref_dur]
        otra = [c for c in ranking if c.get("duracion") != pref_dur]
        dur_label = {"tecnicatura": "⚡ Tecnicaturas", "grado": "🎓 Licenciaturas e Ingenierías"}
        if pref:
            _show_ranking(f"{dur_label[pref_dur]} — Recomendadas", pref[:5], pref, n_cat)
        if otra:
            alt = dur_label["grado" if pref_dur == "tecnicatura" else "tecnicatura"]
            with st.expander(f"Ver también: {alt}"):
                for i, c in enumerate(otra[:5], 1):
                    tarjeta_recomendacion(c, posicion=i)

    st.markdown("---")
    scores    = calcular_scores()
    explorados = st.session_state.get("dominios_explorados", [])
    proximos  = [did for did, _ in scores if did not in explorados]
    prox_info = dom_map.get(proximos[0]) if proximos else None

    c1, c2, c3 = st.columns(3)
    _reset_f2f3 = ("resp_pairwise","resp_f3","vector_usuario",
                   "dominio_activo","pathway_activo","idx","orden","_err_idx")
    with c1:
        if st.button("↩ Cambiar dominio", type="secondary", use_container_width=True):
            for k in _reset_f2f3:
                st.session_state.pop(k, None)
            ir_a(ETAPA_TRANSICION)
    with c2:
        if prox_info:
            if st.button(f"Explorar {prox_info['icono']} {prox_info['nombre']} →",
                         type="primary", use_container_width=True):
                for k in _reset_f2f3:
                    st.session_state.pop(k, None)
                ir_a(ETAPA_TRANSICION)
        else:
            st.caption("Ya exploraste todos los dominios.")
    with c3:
        if st.button("🔄 Empezar de nuevo", type="secondary", use_container_width=True):
            reiniciar()


def _show_ranking(titulo, top5, ranking_full, n_cat):
    if titulo != "Top carreras recomendadas":
        st.markdown(f"##### {titulo}")
    for i, c in enumerate(top5, 1):
        tarjeta_recomendacion(c, posicion=i)
    with st.expander(f"Ver las {len(ranking_full)} carreras del dominio"):
        for i, c in enumerate(ranking_full, 1):
            badge = " `tec`" if c.get("duracion") == "tecnicatura" else ""
            st.markdown(f"**{i:02d}.** {c['nombre']}{badge} — `{c['afinidad_pct']}%`")


# =================================================================
# HELPERS
# =================================================================
def _set_idx(n):
    st.session_state.pop("_err_idx", None)
    st.session_state["idx"] = n
    st.rerun()

def _botonera(idx, tiene_resp, es_ultima, label_next, on_next):
    with st.container(key="quiz_actions"):
        c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("✕ Salir", key="quiz_exit", type="secondary"):
            reiniciar()
    with c2:
        if st.button("← Anterior", key="quiz_prev", type="secondary", disabled=(idx == 0)):
            st.session_state.pop("_err_idx", None)
            st.session_state["idx"] = max(0, idx - 1)
            st.rerun()
    with c3:
        if st.button(label_next, key="quiz_next", type="primary"):
            if not tiene_resp:
                st.session_state["_err_idx"] = idx
                st.rerun()
            else:
                st.session_state.pop("_err_idx", None)
                on_next()

def _barra(n, total, label, fase: int = 0):
    """Barra de progreso con indicador de fases integrado como label."""
    pct = n / total * 100

    if fase in (1, 2, 3):
        pasos = []
        for i, nombre in enumerate(("Fase 1", "Fase 2", "Fase 3"), 1):
            if i < fase:
                texto = f"✓ {nombre}"
                estilo = ("color:var(--card);background:var(--ink);"
                          "border:1.5px solid var(--ink);")
            elif i == fase:
                texto = f"● {nombre} · {n}/{total}"
                estilo = ("color:var(--ink);background:var(--lime);"
                          "border:1.5px solid var(--ink);font-weight:700;")
            else:
                texto = nombre
                estilo = "color:#999;border:1.5px solid #ccc;"
            pasos.append(
                f"<span style='padding:1px 9px;border-radius:20px;"
                f"font-size:0.74rem;white-space:nowrap;{estilo}'>{texto}</span>"
            )
        sep = "<span style='color:#ccc;font-size:0.65rem;'>───</span>"
        label_html = (
            f"<div style='display:flex;align-items:center;gap:0.25rem;'>"
            f"{sep.join(pasos)}</div>"
        )
    else:
        label_html = (
            f"<span style='font-size:0.78rem;color:#555;'>{label} — {n} de {total}</span>"
        )

    st.markdown(
        f"""<div class="quiz-progress">
            <div class="quiz-progress__label">{label_html}</div>
            <div class="quiz-progress__track">
                <div class="quiz-progress__fill" style="width:{pct:.1f}%;"></div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


# =================================================================
# ROUTER
# =================================================================
def pantalla_editor_wrapper():
    from ui.editor import pantalla_editor
    pantalla_editor(reiniciar, ir_a, ETAPA_BIENVENIDA)


def main():
    init_session()
    etapa = st.session_state["etapa"]
    dispatch = {
        ETAPA_BIENVENIDA: pantalla_bienvenida,
        ETAPA_F1:         pantalla_f1,
        ETAPA_TRANSICION: pantalla_transicion,
        ETAPA_F2:         pantalla_f2,
        ETAPA_TRANS_F3:   pantalla_trans_f3,
        ETAPA_F3:         pantalla_f3,
        ETAPA_RESULTADOS: pantalla_resultados,
        ETAPA_EDITOR:     pantalla_editor_wrapper,
    }
    dispatch.get(etapa, reiniciar)()

main()
