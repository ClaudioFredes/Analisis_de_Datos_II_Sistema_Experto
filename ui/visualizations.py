"""
=================================================================
PASO 4.3 - DASHBOARD ANALÍTICO Y RESULTADOS
=================================================================
Funciones de visualización:

  - radar_chart_riasec(): grafica el perfil del usuario contra el
    perfil de una carrera en formato Radar Chart MONOCROMÁTICO
    (negro / gris) con Plotly. Sin colores festivos, sin leyendas
    flotantes intrusivas.

  - tarjeta_recomendacion(): renderiza una tarjeta tipo "card"
    para cada uno de los Top-5 resultados, con título bold grande
    y porcentaje de afinidad en tipografía monoespaciada alineado
    a la derecha. Usa HTML personalizado para sortear las
    limitaciones de st.expander.

Todo se mantiene en la paleta blanco / negro / gris definida en
config.toml y styles.py.
=================================================================
"""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from engine.inference import DIMENSIONES_RIASEC


# Etiquetas humanas para los ejes del radar (más legibles que R/I/A/S/E/C).
ETIQUETAS_RIASEC: dict[str, str] = {
    "R": "Realista",
    "I": "Investigador",
    "A": "Artístico",
    "S": "Social",
    "E": "Emprendedor",
    "C": "Convencional",
}


def radar_chart_riasec(
    vector_usuario: dict[str, float],
    vector_carrera: dict[str, int] | None = None,
    titulo: str = "Tu perfil RIASEC",
) -> go.Figure:
    """Construye un Radar Chart con uno o dos polígonos superpuestos.

    Args:
        vector_usuario: dict {R..C: float} con el perfil del usuario.
        vector_carrera: opcional, dict {R..C: int} de una carrera para
                        superponer y comparar visualmente.
        titulo: título mostrado arriba del gráfico.

    Returns:
        figura Plotly lista para `st.plotly_chart(fig, use_container_width=True)`.

    Decisiones estéticas:
      - template "plotly_white": sin grilla oscura ni fondo azulado.
      - polígono usuario: línea NEGRA + fill translúcido rgba(0,0,0,0.1).
      - polígono carrera: línea GRIS + fill aún más sutil.
      - sin leyenda flotante: se usa el título del trace en hover.
    """
    # Cerramos el polígono repitiendo el primer punto al final.
    # Plotly necesita la lista cerrada para que la línea se vea continua.
    etiquetas = [ETIQUETAS_RIASEC[d] for d in DIMENSIONES_RIASEC]
    etiquetas_cerradas = etiquetas + [etiquetas[0]]

    valores_usuario = [vector_usuario[d] for d in DIMENSIONES_RIASEC]
    valores_usuario_cerrados = valores_usuario + [valores_usuario[0]]

    fig = go.Figure()

    # ---- Trace 1: usuario (acento violeta de la marca + contorno tinta) ----
    fig.add_trace(go.Scatterpolar(
        r=valores_usuario_cerrados,
        theta=etiquetas_cerradas,
        fill="toself",
        name="Tu perfil",
        line=dict(color="#111111", width=2.5),
        fillcolor="rgba(196,181,253,0.45)",   # --violet translúcido
        hovertemplate="<b>%{theta}</b><br>Tu nivel: %{r:.2f}<extra></extra>",
    ))

    # ---- Trace 2 (opcional): carrera (acento lima, contorno punteado) ----
    if vector_carrera is not None:
        valores_carrera = [vector_carrera[d] for d in DIMENSIONES_RIASEC]
        valores_carrera_cerrados = valores_carrera + [valores_carrera[0]]
        fig.add_trace(go.Scatterpolar(
            r=valores_carrera_cerrados,
            theta=etiquetas_cerradas,
            fill="toself",
            name="Carrera",
            line=dict(color="#5b5b5b", width=2, dash="dot"),
            fillcolor="rgba(198,255,77,0.25)",   # --lime translúcido
            hovertemplate="<b>%{theta}</b><br>Carrera: %{r}<extra></extra>",
        ))

    fig.update_layout(
        # Fondos transparentes: dejan ver el "papel técnico" con puntos del
        # contenedor, integrando el gráfico a la estética neo-brutalista.
        title=dict(
            text=titulo,
            font=dict(size=18, color="#111111", family="Inter, sans-serif"),
            x=0.0, xanchor="left",
        ),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickvals=[1, 2, 3, 4, 5],
                tickfont=dict(size=10, color="#999999"),
                gridcolor="rgba(17,17,17,0.12)",
                linecolor="rgba(17,17,17,0.12)",
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color="#111111", family="Inter, sans-serif"),
                gridcolor="rgba(17,17,17,0.10)",
                linecolor="rgba(17,17,17,0.18)",
            ),
        ),
        showlegend=vector_carrera is not None,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=-0.15,
            xanchor="center", x=0.5,
            font=dict(size=11, color="#111111"),
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        # dragmode=False: sin pan/zoom por arrastre. Junto con scrollZoom=False
        # y touch-action:pan-y (CSS), el gráfico sólo reacciona a tooltips y no
        # secuestra el scroll ni hace zoom por error en mobile.
        dragmode=False,
    )

    return fig


def codigo_holland(riasec: dict[str, int]) -> str:
    """Devuelve el código de Holland de una carrera (sus 3 dimensiones
    dominantes), ej. {R:5,I:4,...} -> "RIC".

    Es la forma estándar de resumir un perfil RIASEC: las 3 letras de
    mayor puntaje, en orden descendente.
    """
    top3 = sorted(DIMENSIONES_RIASEC, key=lambda d: riasec[d], reverse=True)[:3]
    return "".join(top3)


_DUR_BADGE = {
    "tecnicatura": ("⚡", "Tecnicatura · 2-3 años"),
    "grado":       ("🎓", "Licenciatura / Ingeniería · 4-6 años"),
}

_ETIQUETA_LABEL = {
    "matematica_intensa":  "Matemática intensa",
    "programacion":        "Programación",
    "contacto_pacientes":  "Atención a pacientes",
    "trabajo_fisico":      "Trabajo físico",
    "exposicion_publica":  "Exposición pública",
    "expresion_artistica": "Expresión artística",
}


def tarjeta_recomendacion(carrera: dict, posicion: int) -> None:
    """Tarjeta expandible: el header ES el botón — no hay botón separado."""
    cod   = codigo_holland(carrera["riasec"])
    dur   = carrera.get("duracion", "")
    dur_icono, dur_texto = _DUR_BADGE.get(dur, ("", ""))
    boost = carrera.get("boost_f3", 0.0)

    boost_tag = "  ✦" if boost > 0.01 else ""
    dur_tag   = f"  ·  {dur_icono} {dur_texto}" if dur_texto else ""

    label = (
        f"**`#{posicion:02d}`**  {carrera['nombre']}{boost_tag}"
        f"  ·  {carrera.get('area', '')}  ·  `{cod}`{dur_tag}"
        f"  —  **{carrera['afinidad_pct']}%**"
    )

    with st.expander(label):
        col_info, col_radar = st.columns([1, 1.3])

        with col_info:
            # Universidades donde se dicta
            universidades = carrera.get("universidades", [])
            if universidades:
                filas_html = "".join(
                    f"<tr>"
                    f"<td style='padding:2px 8px 2px 0;font-weight:600;"
                    f"font-size:0.82rem;white-space:nowrap;'>{u['nombre']}</td>"
                    f"<td style='padding:2px 0;font-size:0.82rem;"
                    f"color:#555;'>{u['ciudad']}</td>"
                    f"</tr>"
                    for u in universidades
                )
                st.markdown(
                    f"**Dónde estudiarla:**"
                    f"<table style='margin-top:0.3rem;border-collapse:collapse;"
                    f"width:100%;'>{filas_html}</table>",
                    unsafe_allow_html=True,
                )
                st.markdown("")

            st.markdown("")
            if etiquetas := carrera.get("etiquetas"):
                labels_txt = " · ".join(_ETIQUETA_LABEL.get(e, e) for e in etiquetas)
                st.caption(f"**Requiere:** {labels_txt}")
            if boost > 0.01:
                st.caption(f"**Ajuste F3:** +{boost:.2f} por compatibilidad de valores.")
            st.caption(
                f"**O\\*NET:** {carrera.get('onet_titulo', '—')} "
                f"`{carrera.get('onet_soc', '—')}`"
            )

        with col_radar:
            if "vector_usuario" in st.session_state:
                fig = radar_chart_riasec(
                    st.session_state["vector_usuario"],
                    carrera["riasec"],
                    titulo=f"Vos vs. {carrera['nombre']}",
                )
                st.plotly_chart(fig, use_container_width=True,
                                config={"scrollZoom": False, "displayModeBar": False,
                                        "doubleClick": False})
