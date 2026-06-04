# -*- coding: utf-8 -*-
"""Tests rápidos del motor de reglas (sin framework, corre con: python test_motor.py)."""
import json
from pathlib import Path
from motor_reglas import recomendar

KB = json.loads((Path(__file__).parent / "data" / "carreras_reglas.json").read_text("utf-8"))["carreras"]

# Perfiles de prueba (RIASEC 1-5)
P_IC = {"R": 2, "I": 5.0, "A": 1.5, "S": 2, "E": 2.5, "C": 4.5}   # I+C alto
P_SR = {"R": 4.0, "I": 3, "A": 2, "S": 5.0, "E": 2, "C": 2.5}     # S+R alto


def top_nombres(recos, n=5):
    return [r["nombre"] for r in recos[:n]]


def test_holland_basico():
    """Perfil I+C en Tecnología -> arriba carreras I/C (Sistemas, Ciencia de Datos…)."""
    recos = recomendar(KB, "tecnologia", P_IC)
    assert recos, "debería haber recomendaciones"
    assert all(r["score"] > 0 for r in recos)
    nombres = " ".join(top_nombres(recos))
    assert "Ciencia de Datos" in nombres or "Sistemas" in nombres


def test_veto_retracta():
    """Vetar 'programacion' elimina las carreras con esa etiqueta."""
    sin = recomendar(KB, "tecnologia", P_IC)
    con = recomendar(KB, "tecnologia", P_IC, vetos={"programacion"})
    assert len(con) < len(sin), "el veto debe reducir el conjunto"
    assert all("programacion" not in r["etiquetas"] for r in con)


def test_boost_f3():
    """Un boost de Fase 3 suma al ajuste total y mejora la posición efectiva."""
    base = recomendar(KB, "tecnologia", P_IC)                           # solo reglas expertas
    con = recomendar(KB, "tecnologia", P_IC, boosts_f3={"ciencia_datos": 0.5})
    cd_base = next(r for r in base if r["id"] == "ciencia_datos")
    cd = next(r for r in con if r["id"] == "ciencia_datos")
    assert cd["boost"] > cd_base["boost"], "el boost de F3 debe sumar al ajuste"
    assert (cd["score"] + cd["boost"]) > (cd_base["score"] + cd_base["boost"])


def test_pathway_seleccion():
    """El pathway se elige por la dimensión dominante del perfil (dims_trigger)."""
    import json as _json
    from pathlib import Path as _Path
    from motor_reglas import seleccionar_pathway
    F3 = _json.loads((_Path(__file__).parent / "data" / "fase3_reglas.json").read_text("utf-8"))["fase3_por_dominio"]
    # perfil I-dominante en tecnología -> pathway con I en dims_trigger
    pw = seleccionar_pathway(F3["tecnologia"], {"R": 2, "I": 5, "A": 2, "S": 2, "E": 2, "C": 3})
    assert "I" in pw["dims_trigger"]


def test_explicabilidad():
    """Cada recomendación trae motivos (reglas que la sostienen)."""
    recos = recomendar(KB, "salud", P_SR)
    assert all(len(r["motivos"]) >= 1 for r in recos)


def test_desempate_afinidad():
    """Entre carreras con la misma certeza, la afinidad las ordena (no quedan al azar)."""
    recos = recomendar(KB, "tecnologia", P_IC)
    # tomar el grupo top con igual score y verificar que la afinidad va descendente
    top_score = recos[0]["score"]
    grupo = [r for r in recos if r["score"] == top_score]
    afs = [r["afinidad"] for r in grupo]
    assert afs == sorted(afs, reverse=True), "el grupo empatado debe ir por afinidad desc"


def test_multidominio():
    """Una carrera multidominio (Bioingeniería) aparece en sus distintos dominios."""
    en_tec = {r["id"] for r in recomendar(KB, "tecnologia", {"R": 4, "I": 5, "A": 2, "S": 2.5, "E": 2, "C": 3.5})}
    en_cie = {r["id"] for r in recomendar(KB, "ciencias", {"R": 4, "I": 5, "A": 2, "S": 2.5, "E": 2, "C": 3.5})}
    assert "bioingenieria" in en_tec and "bioingenieria" in en_cie


def test_regla_experta_E3_y_E1():
    """E3 premia la carrera cuya dominante es el interés #1; E1 penaliza el confound."""
    perfil = {"R": 1.5, "I": 5.0, "A": 2.0, "S": 2.0, "E": 2.5, "C": 4.0}
    by_id = {r["id"]: r for r in recomendar(KB, "tecnologia", perfil)}
    cd = by_id["ciencia_datos"]                 # I-C-E, dominante I = interés #1
    assert "E3" in cd["reglas"] and cd["boost"] > 0
    im = by_id["ingenieria_mecanica"]           # R-I-C, dominante R (no es interés)
    assert "E1" in im["reglas"] and im["boost"] < 0


def test_regla_experta_E4_duracion():
    """E4 refuerza las carreras que coinciden con la duración preferida."""
    perfil = {"R": 2, "I": 5, "A": 2, "S": 2, "E": 2.5, "C": 4}
    by_id = {r["id"]: r for r in recomendar(KB, "tecnologia", perfil, dur_pref="tecnicatura")}
    tp = by_id["tec_programacion"]
    assert tp["duracion"] == "tecnicatura" and "E4" in tp["reglas"]


if __name__ == "__main__":
    fns = [test_holland_basico, test_veto_retracta, test_boost_f3, test_pathway_seleccion,
           test_explicabilidad, test_desempate_afinidad, test_multidominio,
           test_regla_experta_E3_y_E1, test_regla_experta_E4_duracion]
    ok = 0
    for fn in fns:
        try:
            fn()
            print(f"  OK   {fn.__name__}")
            ok += 1
        except AssertionError as e:
            print(f"  FAIL {fn.__name__}: {e}")
    print(f"\n{ok}/{len(fns)} tests OK")
