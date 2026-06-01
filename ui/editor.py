"""
=================================================================
MODO EDITOR — Panel de mantenimiento del sistema experto
=================================================================
Accesible desde la bienvenida con clave de acceso.
Tres módulos:
  1. Simulador  — probar perfiles RIASEC contra el catálogo
  2. Calibrador — ajustar PESO_COSENO y ver el impacto en vivo
  3. Carreras   — CRUD completo del catálogo de carreras
=================================================================
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from engine.inference import (
    DIMENSIONES_RIASEC,
    PESO_COSENO,
    ranking_carreras,
)
from ui.visualizations import (
    ETIQUETAS_RIASEC,
    radar_chart_riasec,
)

_DATA      = Path(__file__).resolve().parents[1] / "data"
_PATH_CAT  = _DATA / "carreras.json"
_PATH_DOM  = _DATA / "dominios.json"

_AREAS = [
    "Ingeniería y Tecnología",
    "Ciencias Naturales y Exactas",
    "Ciencias de la Salud",
    "Arte y Diseño",
    "Ciencias Sociales y Humanidades",
    "Ciencias Económicas y Administrativas",
    "Educación",
]
_ETIQUETAS_DISP = [
    "matematica_intensa",
    "programacion",
    "contacto_pacientes",
    "trabajo_fisico",
    "exposicion_publica",
    "expresion_artistica",
]
_PERFILES_PRUEBA = {
    "Investigador puro (I alto)":   {"R":2.0,"I":5.0,"A":2.0,"S":2.0,"E":2.0,"C":3.0},
    "Social (S alto)":              {"R":2.0,"I":2.0,"A":3.0,"S":5.0,"E":2.0,"C":2.0},
    "Técnico R+C (Instrumentadora)":{"R":5.0,"I":2.0,"A":1.0,"S":3.0,"E":1.0,"C":5.0},
    "Artístico puro (A alto)":      {"R":2.0,"I":2.0,"A":5.0,"S":2.0,"E":3.0,"C":2.0},
    "Emprendedor E+S":              {"R":2.0,"I":2.0,"A":3.0,"S":4.0,"E":5.0,"C":2.0},
    "Multipotencial R+S":           {"R":5.0,"I":2.0,"A":2.0,"S":5.0,"E":2.0,"C":2.0},
}

_PLOT_CFG = {"scrollZoom": False, "displayModeBar": False, "doubleClick": False}


# =================================================================
# Helpers de datos
# =================================================================
def _cargar_catalogo_raw() -> dict:
    return json.loads(_PATH_CAT.read_text(encoding="utf-8"))

def _guardar_catalogo(data: dict) -> None:
    _PATH_CAT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _cargar_dominios_raw() -> list[dict]:
    return json.loads(_PATH_DOM.read_text(encoding="utf-8"))["dominios"]

def _vector_from_state(prefix: str) -> dict[str, float]:
    return {d: float(st.session_state.get(f"{prefix}_{d}", 3.0)) for d in DIMENSIONES_RIASEC}


# =================================================================
# TAB 1 · Simulador
# =================================================================
def _tab_simulador() -> None:
    st.markdown("### Simulador de perfiles RIASEC")
    st.caption("Ajustá las 6 dimensiones y mirá qué carreras recomienda el motor.")

    # Presets rápidos
    preset = st.selectbox("Cargar perfil de prueba", ["— personalizado —"] + list(_PERFILES_PRUEBA.keys()),
                          key="sim_preset")
    if preset != "— personalizado —":
        for d, v in _PERFILES_PRUEBA[preset].items():
            st.session_state[f"sim_{d}"] = v

    # Sliders RIASEC
    cols = st.columns(6)
    for col, dim in zip(cols, DIMENSIONES_RIASEC):
        col.slider(ETIQUETAS_RIASEC[dim], 1.0, 5.0,
                   st.session_state.get(f"sim_{dim}", 3.0),
                   0.1, key=f"sim_{dim}")
    vector = _vector_from_state("sim")

    # Filtro de dominio
    doms = _cargar_dominios_raw()
    dom_opts = {"Todos (catálogo completo)": None}
    for d in doms:
        dom_opts[f"{d['icono']} {d['nombre']}"] = d["id"]
    dom_label = st.selectbox("Filtrar por dominio", list(dom_opts.keys()), key="sim_dom")
    dom_id = dom_opts[dom_label]

    # Cargar catálogo
    raw = _cargar_catalogo_raw()["carreras"]
    if dom_id:
        dom_obj = next((d for d in doms if d["id"] == dom_id), None)
        ids_dom = set(dom_obj["carreras"]) if dom_obj else set()
        catalogo = [c for c in raw if c["id"] in ids_dom]
    else:
        catalogo = raw

    col_radar, col_rank = st.columns([1, 1.2])
    with col_radar:
        fig = radar_chart_riasec(vector, titulo="Perfil simulado")
        st.plotly_chart(fig, use_container_width=True, config=_PLOT_CFG)

    with col_rank:
        ranking = ranking_carreras(vector, catalogo)
        st.markdown(f"**Top 10** sobre {len(catalogo)} carreras")
        for i, c in enumerate(ranking[:10], 1):
            dur = "⚡" if c.get("duracion") == "tecnicatura" else "🎓"
            st.markdown(
                f"`{i:02d}` {dur} **{c['nombre']}** &nbsp; `{c['afinidad_pct']}%`",
                unsafe_allow_html=True,
            )


# =================================================================
# TAB 2 · Calibrador de pesos
# =================================================================
def _tab_calibrador() -> None:
    st.markdown("### Calibrador de PESO_COSENO")
    st.caption(
        f"El peso actual en producción es **{PESO_COSENO}** (calibrado por Monte Carlo). "
        "Modificalo aquí para explorar el impacto en el ranking antes de aplicarlo."
    )

    peso_nuevo = st.slider(
        "PESO_COSENO (peso del coseno en el score híbrido)",
        0.0, 0.5, PESO_COSENO, 0.05,
        key="cal_peso",
        help="0 = solo Pearson (forma del perfil) · 0.5 = partes iguales",
    )

    # Info visual
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Peso Coseno", f"{peso_nuevo:.2f}")
    col_b.metric("Peso Pearson", f"{1 - peso_nuevo:.2f}")
    col_c.metric("Δ vs producción", f"{peso_nuevo - PESO_COSENO:+.2f}")

    st.markdown("---")

    # Perfil de prueba
    perfil_sel = st.selectbox("Perfil de comparación", list(_PERFILES_PRUEBA.keys()), key="cal_perfil")
    vector = {d: float(v) for d, v in _PERFILES_PRUEBA[perfil_sel].items()}

    raw = _cargar_catalogo_raw()["carreras"]
    rk_actual = ranking_carreras(vector, raw, PESO_COSENO)
    rk_nuevo  = ranking_carreras(vector, raw, peso_nuevo)

    ids_actual = [c["id"] for c in rk_actual[:10]]
    ids_nuevo  = [c["id"] for c in rk_nuevo[:10]]

    col_act, col_new = st.columns(2)
    with col_act:
        st.markdown(f"**Producción** · `PESO_COSENO = {PESO_COSENO}`")
        for i, c in enumerate(rk_actual[:10], 1):
            salida = "🔴 " if c["id"] not in ids_nuevo else ""
            st.markdown(f"`{i:02d}` {salida}{c['nombre']} `{c['afinidad_pct']}%`")

    with col_new:
        st.markdown(f"**Nuevo** · `PESO_COSENO = {peso_nuevo}`")
        for i, c in enumerate(rk_nuevo[:10], 1):
            entrada = "🟢 " if c["id"] not in ids_actual else ""
            st.markdown(f"`{i:02d}` {entrada}{c['nombre']} `{c['afinidad_pct']}%`")

    st.markdown("---")
    if peso_nuevo != PESO_COSENO:
        st.info("Para aplicar este valor permanentemente, modificá la línea en `engine/inference.py`:")
        st.code(f"PESO_COSENO: float = {peso_nuevo}", language="python")
    else:
        st.success("El peso actual coincide con el valor en producción.")


# =================================================================
# TAB 3 · Editor de carreras
# =================================================================
def _tab_carreras() -> None:
    st.markdown("### Editor de carreras")

    raw_data = _cargar_catalogo_raw()
    carreras = raw_data["carreras"]
    ids      = [c["id"] for c in carreras]
    opciones = ["➕ Nueva carrera"] + [f"{c['nombre']} ({c['id']})" for c in carreras]

    sel = st.selectbox("Seleccioná una carrera", opciones, key="ed_car_sel")

    es_nueva = sel == "➕ Nueva carrera"
    carrera_actual: dict = {}
    if not es_nueva:
        idx_sel = opciones.index(sel) - 1
        carrera_actual = carreras[idx_sel]

    # Inicializar universidades en session state
    univ_key = f"ed_univs_{carrera_actual.get('id','_nueva')}"
    if univ_key not in st.session_state:
        st.session_state[univ_key] = list(carrera_actual.get("universidades", []))

    st.markdown("---")

    col_form, col_riasec = st.columns([1.1, 1])

    with col_form:
        nombre = st.text_input("Nombre de la carrera",
                               value=carrera_actual.get("nombre", ""), key="ed_nombre")
        cid    = st.text_input("ID (snake_case, único)",
                               value=carrera_actual.get("id", ""), key="ed_id",
                               disabled=not es_nueva)
        area   = st.selectbox("Área", _AREAS,
                              index=_AREAS.index(carrera_actual["area"])
                              if carrera_actual.get("area") in _AREAS else 0,
                              key="ed_area")
        dur    = st.radio("Duración", ["grado", "tecnicatura"],
                          index=0 if carrera_actual.get("duracion","grado") == "grado" else 1,
                          horizontal=True, key="ed_dur")
        onet_soc   = st.text_input("Código SOC O*NET",
                                   value=carrera_actual.get("onet_soc",""), key="ed_soc")
        onet_titulo = st.text_input("Título O*NET",
                                    value=carrera_actual.get("onet_titulo",""), key="ed_otit")
        etiquetas  = st.multiselect("Etiquetas de perfil", _ETIQUETAS_DISP,
                                    default=carrera_actual.get("etiquetas",[]),
                                    key="ed_etiq")

        # Universidades
        st.markdown("**Universidades donde se dicta:**")
        univs: list[dict] = st.session_state[univ_key]
        for i, u in enumerate(univs):
            c1, c2, c3 = st.columns([2, 2, 0.5])
            c1.markdown(f"**{u['nombre']}**")
            c2.markdown(u["ciudad"])
            if c3.button("✕", key=f"del_univ_{i}"):
                univs.pop(i)
                st.rerun()

        with st.expander("Agregar universidad"):
            u_nom = st.text_input("Nombre (ej. UBA – FCEyN)", key="ed_unom")
            u_ciu = st.text_input("Ciudad", key="ed_uciu")
            if st.button("Agregar", key="ed_uadd"):
                if u_nom and u_ciu:
                    univs.append({"nombre": u_nom, "ciudad": u_ciu})
                    st.rerun()

    with col_riasec:
        st.markdown("**Perfil RIASEC:**")
        riasec_actual = carrera_actual.get("riasec", {d: 3.0 for d in DIMENSIONES_RIASEC})
        for dim in DIMENSIONES_RIASEC:
            riasec_actual[dim] = st.slider(
                ETIQUETAS_RIASEC[dim], 1.0, 5.0,
                float(riasec_actual.get(dim, 3.0)), 0.05,
                key=f"ed_r_{dim}",
            )
        fig = radar_chart_riasec(riasec_actual, titulo="Perfil de la carrera")
        st.plotly_chart(fig, use_container_width=True, config=_PLOT_CFG)

    st.markdown("---")
    col_save, col_del = st.columns([1, 1])

    with col_save:
        if st.button("💾 Guardar carrera", type="primary", use_container_width=True):
            if not nombre.strip():
                st.error("El nombre es obligatorio.")
            elif es_nueva and (not cid.strip() or cid in ids):
                st.error("El ID es obligatorio y debe ser único." if not cid else "Ese ID ya existe.")
            else:
                nueva = {
                    "id":           cid if es_nueva else carrera_actual["id"],
                    "nombre":       nombre.strip(),
                    "area":         area,
                    "onet_soc":     onet_soc.strip(),
                    "onet_titulo":  onet_titulo.strip(),
                    "riasec":       {d: round(float(st.session_state[f"ed_r_{d}"]), 4)
                                     for d in DIMENSIONES_RIASEC},
                    "etiquetas":    etiquetas,
                    "duracion":     dur,
                    "universidades": univs,
                }
                if es_nueva:
                    raw_data["carreras"].append(nueva)
                else:
                    raw_data["carreras"][idx_sel] = nueva
                _guardar_catalogo(raw_data)
                # Limpiar caché de Streamlit para reflejar cambios
                st.cache_data.clear()
                st.success(f"✓ Carrera '{nombre}' guardada correctamente.")
                st.session_state.pop(univ_key, None)
                st.rerun()

    with col_del:
        if not es_nueva:
            if st.button("🗑 Eliminar carrera", type="secondary", use_container_width=True):
                st.session_state["ed_confirm_del"] = True

            if st.session_state.get("ed_confirm_del"):
                st.warning(f"¿Eliminar **{carrera_actual['nombre']}**? Esta acción no se puede deshacer.")
                c1, c2 = st.columns(2)
                if c1.button("Sí, eliminar", type="primary", use_container_width=True):
                    raw_data["carreras"].pop(idx_sel)
                    _guardar_catalogo(raw_data)
                    st.cache_data.clear()
                    st.session_state.pop("ed_confirm_del", None)
                    st.session_state.pop(univ_key, None)
                    st.success("Carrera eliminada.")
                    st.rerun()
                if c2.button("Cancelar", type="secondary", use_container_width=True):
                    st.session_state.pop("ed_confirm_del", None)
                    st.rerun()


# =================================================================
# Entrada principal
# =================================================================
def pantalla_editor(reiniciar_fn, ir_a_fn, etapa_bienvenida: str) -> None:
    from ui.header import render_header
    render_header()

    # Verificación de clave
    if not st.session_state.get("_editor_auth"):
        st.markdown("## ⚙ Modo Editor")
        st.markdown("Ingresá la clave de acceso para continuar.")
        clave = st.text_input("Clave", type="password", key="ed_clave_input")
        if st.button("Ingresar", type="primary"):
            if clave == "orientai2024":
                st.session_state["_editor_auth"] = True
                st.rerun()
            else:
                st.error("Clave incorrecta.")
        st.markdown("&nbsp;")
        if st.button("← Volver", type="secondary"):
            ir_a_fn(etapa_bienvenida)
        return

    st.markdown("## ⚙ Modo Editor")
    st.caption("Los cambios en el editor de carreras se escriben directamente en `data/carreras.json`.")

    if st.button("← Volver al inicio", type="secondary"):
        st.session_state.pop("_editor_auth", None)
        ir_a_fn(etapa_bienvenida)

    st.markdown("---")

    tab_sim, tab_cal, tab_carr = st.tabs(["🧪 Simulador", "⚖ Calibrador de pesos", "📝 Editor de carreras"])

    with tab_sim:
        _tab_simulador()

    with tab_cal:
        _tab_calibrador()

    with tab_carr:
        _tab_carreras()
