"""
=================================================================
TESTS DEL MOTOR DE INFERENCIA — SISTEMA EXPERTO VOCACIONAL
=================================================================
Valida el pipeline RIASEC con perfiles sintéticos:
  calcular_vector_usuario / calcular_vector_pairwise -> ranking_carreras

No prueba la UI ni el flujo de Streamlit; solo el motor puro.

Ejecución:
    python tests/test_perfiles.py     # reporte legible
    pytest tests/test_perfiles.py     # como suite pytest
=================================================================
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from engine.inference import (  # noqa: E402
    DIMENSIONES_RIASEC,
    calcular_vector_pairwise,
    correlacion_pearson,
    ranking_carreras,
    similitud_coseno,
)

_DATA    = RAIZ / "data"
CATALOGO = json.loads((_DATA / "carreras.json").read_text(encoding="utf-8"))["carreras"]


# -----------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------
def _vector(niveles: dict[str, int]) -> dict[str, float]:
    """Vector RIASEC sintético directo — sin pasar por preguntas F1.
    Las preguntas F1 mapean a dominios vocacionales, no a dimensiones
    RIASEC, por lo que calcular_vector_usuario no aplica aquí."""
    return {dim: float(niveles.get(dim, 3)) for dim in DIMENSIONES_RIASEC}


def _ranking(niveles: dict[str, int]) -> list[dict]:
    return ranking_carreras(_vector(niveles), CATALOGO)


def _ids(ranking: list[dict], n: int | None = None) -> list[str]:
    return [c["id"] for c in (ranking[:n] if n else ranking)]


# -----------------------------------------------------------------
# Tests de perfiles RIASEC
# -----------------------------------------------------------------
def test_perfil_social() -> None:
    """Perfil Social alto -> recomendaciones de ayuda / educación / salud."""
    rk = _ranking({"R": 2, "I": 2, "A": 2, "S": 5, "E": 2, "C": 2})
    assert rk[0]["area"] in {
        "Ciencias de la Salud", "Ciencias Sociales y Humanidades", "Educación"
    }
    assert "trabajo_social" in _ids(rk, 6)


def test_perfil_artistico() -> None:
    """Perfil Artístico alto -> el #1 es del área Arte y Diseño."""
    rk = _ranking({"R": 2, "I": 2, "A": 5, "S": 2, "E": 2, "C": 2})
    assert rk[0]["area"] == "Arte y Diseño"


def test_perfil_realista() -> None:
    """Perfil Realista+Investigador -> el #1 es fuertemente Realista y las
    ingenierías aparecen arriba."""
    rk = _ranking({"R": 5, "I": 4, "A": 2, "S": 2, "E": 2, "C": 2})
    assert rk[0]["riasec"]["R"] >= 4, rk[0]["id"]
    assert "ingenieria_mecanica" in _ids(rk, 3)
    assert sum(c["area"] == "Ingeniería y Tecnología" for c in rk[:5]) >= 2


def test_vector_nulo() -> None:
    """Responder todo igual -> afinidad 0 para todas las carreras."""
    rk = _ranking({"R": 3, "I": 3, "A": 3, "S": 3, "E": 3, "C": 3})
    assert rk[0]["afinidad_pct"] == 0


# -----------------------------------------------------------------
# Tests del motor híbrido Coseno + Pearson
# -----------------------------------------------------------------
def test_coseno_y_pearson_son_distintos() -> None:
    """El híbrido combina DOS señales reales. Coseno y Pearson deben diferir."""
    u = {"R": 5, "I": 4, "A": 2, "S": 2, "E": 3, "C": 3}
    c = {"R": 4.5, "I": 4.1, "A": 1.5, "S": 1.0, "E": 2.1, "C": 3.0}
    cos  = similitud_coseno(u, c)
    pear = correlacion_pearson(u, c)
    assert abs(cos - pear) > 1e-3
    assert -1.0 <= cos <= 1.0 and -1.0 <= pear <= 1.0


def test_sin_colisiones_de_vectores() -> None:
    """El catálogo no debe tener vectores RIASEC duplicados."""
    grupos: dict[tuple, list[str]] = {}
    for c in CATALOGO:
        clave = tuple(c["riasec"][d] for d in DIMENSIONES_RIASEC)
        grupos.setdefault(clave, []).append(c["id"])
    colisiones = [ids for ids in grupos.values() if len(ids) > 1]
    assert colisiones == [], colisiones
    assert len(grupos) == len(CATALOGO)


def test_desempate_no_depende_del_orden_del_catalogo() -> None:
    """El ranking es estable ante permutaciones del catálogo."""
    import random as _r
    vector = _vector({"R": 4, "I": 5, "A": 2, "S": 2, "E": 3, "C": 3})
    base     = _ids(ranking_carreras(vector, CATALOGO))
    barajado = list(CATALOGO)
    _r.Random(0).shuffle(barajado)
    assert _ids(ranking_carreras(vector, barajado)) == base


def test_afinidad_sin_castigo_al_cubo() -> None:
    """Match casi perfecto debe dar afinidad >= 85% y ser monótono."""
    rk = _ranking({"R": 5, "I": 4, "A": 2, "S": 2, "E": 3, "C": 3})
    assert rk[0]["afinidad_pct"] >= 85
    pcts = [c["afinidad_pct"] for c in rk]
    assert pcts == sorted(pcts, reverse=True)


# -----------------------------------------------------------------
# Tests de calcular_vector_pairwise (motor de Fase 2)
# -----------------------------------------------------------------
def test_pairwise_dimension_dominante() -> None:
    """Si el usuario elige siempre la opción de dimensión I, el vector
    debe tener I como dimensión máxima."""
    triadas = [
        {"id": "T1", "opciones": [
            {"id": "T1_I", "dimension": "I"},
            {"id": "T1_R", "dimension": "R"},
            {"id": "T1_A", "dimension": "A"},
        ]},
        {"id": "T2", "opciones": [
            {"id": "T2_I", "dimension": "I"},
            {"id": "T2_S", "dimension": "S"},
            {"id": "T2_C", "dimension": "C"},
        ]},
    ]
    elecciones = {"T1": "T1_I", "T2": "T2_I"}
    vector = calcular_vector_pairwise(elecciones, triadas)
    assert vector["I"] == 5.0
    assert max(vector.values()) == vector["I"]


def test_pairwise_dimension_nunca_elegida() -> None:
    """Una dimensión que nunca aparece en las tríadas recibe valor neutro 3.0."""
    triadas = [
        {"id": "T1", "opciones": [
            {"id": "T1_R", "dimension": "R"},
            {"id": "T1_I", "dimension": "I"},
            {"id": "T1_A", "dimension": "A"},
        ]},
    ]
    elecciones = {"T1": "T1_R"}
    vector = calcular_vector_pairwise(elecciones, triadas)
    # S, E, C nunca aparecieron -> neutro
    assert vector["S"] == 3.0
    assert vector["E"] == 3.0
    assert vector["C"] == 3.0


def test_pairwise_rango_valido() -> None:
    """El vector pairwise siempre vive en [1.0, 5.0]."""
    triadas = [
        {"id": f"T{i}", "opciones": [
            {"id": f"T{i}_R", "dimension": "R"},
            {"id": f"T{i}_I", "dimension": "I"},
            {"id": f"T{i}_S", "dimension": "S"},
        ]} for i in range(5)
    ]
    elecciones = {f"T{i}": f"T{i}_R" for i in range(5)}
    vector = calcular_vector_pairwise(elecciones, triadas)
    for dim, val in vector.items():
        assert 1.0 <= val <= 5.0, f"{dim}={val} fuera de rango"


# -----------------------------------------------------------------
# Edge cases del motor
# -----------------------------------------------------------------
def test_perfil_instrumentadora() -> None:
    """Caso R+C alto (Instrumentadora): su carrera debe ser #1, Salud domina
    el Top-5 y las carreras comerciales quedan muy por debajo."""
    rk = _ranking({"R": 5, "I": 2, "A": 1, "S": 3, "E": 1, "C": 5})
    idx = {c["id"]: i for i, c in enumerate(rk)}

    assert rk[0]["id"] == "tec_instrumentacion_quirurgica", rk[0]["id"]
    assert sum(c["area"] == "Ciencias de la Salud" for c in rk[:5]) >= 3
    top20 = _ids(rk, 20)
    assert "martillero_publico" not in top20
    assert "administracion_empresas" not in top20
    assert idx["medicina"] < idx["martillero_publico"]
    medicina = next(c for c in rk if c["id"] == "medicina")
    assert medicina["afinidad_pct"] > 0


def test_perfil_plano_indeciso() -> None:
    """Todo 3: catálogo completo con afinidad 0, sin colapso."""
    rk = _ranking({"R": 3, "I": 3, "A": 3, "S": 3, "E": 3, "C": 3})
    assert len(rk) == len(CATALOGO)
    assert all(c["afinidad_pct"] == 0 for c in rk)


def test_perfil_extremo() -> None:
    """5 en R, 1 en todo lo demás: el #1 es Realista y los % son monótonos."""
    rk = _ranking({"R": 5, "I": 1, "A": 1, "S": 1, "E": 1, "C": 1})
    top = rk[0]["riasec"]
    assert top["R"] >= 4, rk[0]["id"]
    assert top["R"] == max(top.values()), rk[0]["id"]
    assert rk[0]["afinidad_pct"] >= 70
    pcts = [c["afinidad_pct"] for c in rk]
    assert pcts == sorted(pcts, reverse=True)
    assert all(0 <= p <= 100 for p in pcts)


def test_perfil_multipotencial() -> None:
    """R y S altos (dimensiones opuestas): el Top-10 tiene carreras de ambos
    polos y Kinesiología (puente R+S) aparece en el podio."""
    rk = _ranking({"R": 5, "I": 1, "A": 1, "S": 5, "E": 1, "C": 1})
    top10 = rk[:10]
    assert any(c["riasec"]["R"] >= 4 for c in top10)
    assert any(c["riasec"]["S"] >= 4 for c in top10)
    assert "kinesiologia" in _ids(rk, 5)
    pcts = [c["afinidad_pct"] for c in rk]
    assert pcts == sorted(pcts, reverse=True)


# -----------------------------------------------------------------
# Runner standalone
# -----------------------------------------------------------------
def _main() -> int:
    tests = [
        ("Perfil social",                          test_perfil_social),
        ("Perfil artístico",                       test_perfil_artistico),
        ("Perfil realista",                        test_perfil_realista),
        ("Vector nulo",                            test_vector_nulo),
        ("Coseno != Pearson (híbrido real)",        test_coseno_y_pearson_son_distintos),
        ("Sin colisiones de vectores",             test_sin_colisiones_de_vectores),
        ("Desempate neutral",                      test_desempate_no_depende_del_orden_del_catalogo),
        ("Afinidad sin castigo al cubo",           test_afinidad_sin_castigo_al_cubo),
        ("Pairwise: dimensión dominante",          test_pairwise_dimension_dominante),
        ("Pairwise: dimensión nunca elegida",      test_pairwise_dimension_nunca_elegida),
        ("Pairwise: rango válido [1, 5]",          test_pairwise_rango_valido),
        ("Edge: Instrumentadora (R+C)",            test_perfil_instrumentadora),
        ("Edge: Plano / indeciso",                 test_perfil_plano_indeciso),
        ("Edge: Extremo (una dim al máximo)",      test_perfil_extremo),
        ("Edge: Multipotencial (R y S opuestos)",  test_perfil_multipotencial),
    ]
    fallidos = 0
    for nombre, fn in tests:
        try:
            fn()
            print(f"  PASS  {nombre}")
        except AssertionError as e:
            fallidos += 1
            print(f"  FAIL  {nombre}  -> {e}")
        except Exception as e:
            fallidos += 1
            print(f"  ERROR {nombre}  -> {type(e).__name__}: {e}")

    print(f"\n{len(tests) - fallidos}/{len(tests)} tests OK.")
    return 1 if fallidos else 0


if __name__ == "__main__":
    sys.exit(_main())
