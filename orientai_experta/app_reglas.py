# -*- coding: utf-8 -*-
"""
ORIENTAI · versión por REGLAS (Experta) — app Streamlit de 3 fases.

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
DOM_INFO = KB["_meta"]["dominios"]
TRI = TRI_DATA["triadas_por_dominio"]
F1 = F1_DATA["fase1_dominio"]
F3 = F3_DATA["fase3_por_dominio"]
BIPOLAR = {1: "Totalmente ←", 2: "Más bien ←", 3: "Neutro", 4: "Más bien →", 5: "Totalmente →"}

st.set_page_config(page_title="ORIENTAI · Reglas", page_icon="🧩", layout="centered")


def init():
    st.session_state.setdefault("stage", "bienvenida")
    st.session_state.setdefault("resp_f1", {})
    st.session_state.setdefault("resp_triadas", {})
    st.session_state.setdefault("f2_idx", 0)
    st.session_state.setdefault("dominio", None)
    st.session_state.setdefault("perfil", None)
    st.session_state.setdefault("altos", None)
    st.session_state.setdefault("pathway", None)
    st.session_state.setdefault("resp_f3", {})


def ir(stage):
    st.session_state["stage"] = stage
    st.rerun()


def likert(label, key, default=3):
    return st.radio(label, [1, 2, 3, 4, 5], index=default - 1, horizontal=True,
                    format_func=lambda v: LIKERT[v], key=key)


# ─────────────────────────────────────────────────────────────
def pantalla_bienvenida():
    st.title("🧩 ORIENTAI · versión por reglas")
    st.caption("Sistema experto basado en reglas (Experta) — 90 carreras, 6 dominios")
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
            f"motor: **Experta** (reglas R1 Holland · R2 Veto · R3 Valor)")
    if st.button("Comenzar →", type="primary", use_container_width=True):
        ir("f1")


# ─────────────────────────────────────────────────────────────
def pantalla_f1():
    st.subheader("Fase 1 · ¿Qué mundo te atrae más?")
    st.caption("¿Cuánto te gustaría hacer cada actividad?")
    with st.form("f1"):
        resp = {}
        for q in F1:
            resp[q["id"]] = likert(q["texto"], key="f1_" + q["id"])
        ok = st.form_submit_button("Ver mi dominio →", type="primary", use_container_width=True)
    if ok:
        st.session_state["resp_f1"] = resp
        ir("f1_elegir")


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
    c1, c2 = st.columns(2)
    if c1.button("← Volver", use_container_width=True):
        ir("f1")
    if c2.button("Continuar a Fase 2 →", type="primary", use_container_width=True):
        st.session_state["dominio"] = dom
        ir("f2")


# ─────────────────────────────────────────────────────────────
def _perfil_de_triadas(elecciones, triadas):
    """Fórmula pairwise del sistema original:
    score_dim = 1 + (victorias_dim / apariciones_dim) * 4   (3.0 si no aparece)."""
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

    st.subheader("Fase 3 · Valores y contexto")
    if not pathway:
        st.session_state["resp_f3"] = {}
        ir("resultados")
        return

    st.info(f"**Perfil detectado: {pathway['nombre']}**  \n{pathway.get('descripcion', '')}")
    st.caption("Estas preguntas están calibradas para tu perfil y **ajustan finamente** "
               "el ranking (refuerzan carreras concretas, no dimensiones genéricas).")

    with st.form("f3"):
        resp = {}
        for q in pathway["preguntas"]:
            st.markdown(f"**{q['pregunta']}**")
            ca, cb = st.columns(2)
            ca.caption(f"← {q['polo_a']}")
            cb.markdown(f"<div style='text-align:right;color:#888;font-size:.875rem'>"
                        f"{q['polo_b']} →</div>", unsafe_allow_html=True)
            resp[q["id"]] = st.radio(q["id"], [1, 2, 3, 4, 5], index=2, horizontal=True,
                                     format_func=lambda v: BIPOLAR[v],
                                     label_visibility="collapsed", key="f3_" + q["id"])
            st.markdown("")
        ok = st.form_submit_button("Ver mis resultados →", type="primary", use_container_width=True)
    if ok:
        st.session_state["resp_f3"] = resp
        ir("resultados")


# ─────────────────────────────────────────────────────────────
def pantalla_resultados():
    dom = st.session_state["dominio"]
    perfil = st.session_state["perfil"]
    altos = st.session_state["altos"]
    pathway = st.session_state.get("pathway")
    resp_f3 = st.session_state.get("resp_f3", {})

    boosts = boosts_de_fase3(pathway, resp_f3) if pathway else {}
    recos = recomendar(CARRERAS, dom, perfil, boosts_f3=boosts)

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
            estrella = " ✦" if r["boost"] else ""
            extra = f" · ajuste F3 +{r['boost']:.2f}" if r["boost"] else ""
            c1.markdown(f"**{i}. {r['nombre']}{estrella}**  \n"
                        f"<span style='color:#888'>código Holland: {'-'.join(r['code'])} · "
                        f"afinidad {r['afinidad']}{extra}</span>", unsafe_allow_html=True)
            c2.metric("certeza", r["score"])
            with st.expander("¿Por qué? (reglas que la sostienen)"):
                for m in r["motivos"]:
                    st.markdown(f"- {m}")
    if any(r["boost"] for r in recos[:5]):
        st.caption("✦ = la **Fase 3** reforzó esta carrera y ajustó su posición.")

    with st.expander("🧠 Cómo razonó el sistema (reglas aplicadas)"):
        n_boost = sum(1 for r in recos if r["boost"])
        st.markdown(
            f"""
- **R1 · Holland**: emparejó tu perfil (**{', '.join(altos)}**) con el código de
  cada carrera del dominio *{info['nombre']}*. Dominante = +3, secundaria = +2, terciaria = +1.
- **R3 · Ajuste de Fase 3**: { f'el pathway *{pathway["nombre"]}* reforzó {n_boost} carreras concretas según tus respuestas bipolares (boost por carrera, como el sistema original).' if pathway and n_boost else 'el pathway no movió el ranking (respuestas neutrales).' }

El orden final es **certeza + ajuste de Fase 3**; ante empates, se usa la
**afinidad** (intensidad del perfil sobre el código de la carrera). Todo el
razonamiento es explicable y dirigido por reglas.
            """
        )

    if st.button("🔄 Empezar de nuevo", use_container_width=True):
        reiniciar()


def reiniciar():
    for k in ("stage", "resp_f1", "resp_triadas", "f2_idx", "dominio", "perfil", "altos", "pathway", "resp_f3"):
        st.session_state.pop(k, None)
    init()
    st.rerun()


# ─────────────────────────────────────────────────────────────
def main():
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
