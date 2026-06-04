# -*- coding: utf-8 -*-
"""
Genera la base de conocimiento de ORIENTAI.

Produce `data/carreras_reglas.json` con las 90 carreras de los 6 dominios.
Para cada carrera incluye:
  - la LISTA de dominios a los que pertenece (una carrera puede estar en varios),
  - su CÓDIGO HOLLAND (las 3 letras RIASEC dominantes),
  - el nivel discretizado por dimensión (bajo/medio/alto).

Uso:  python build_kb.py
"""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
DIMS = ("R", "I", "A", "S", "E", "C")


def nivel(v: float) -> str:
    """Discretiza un valor RIASEC 1-5 en bajo/medio/alto."""
    if v <= 2.5:
        return "bajo"
    if v <= 3.6:
        return "medio"
    return "alto"


def codigo_holland(riasec: dict, n: int = 3) -> list[str]:
    """Las n dimensiones con mayor puntaje (código Holland), dominante primero."""
    return [d for d, _ in sorted(riasec.items(), key=lambda kv: -kv[1])[:n]]


def main():
    carreras = json.loads((RAIZ / "data" / "carreras.json").read_text("utf-8"))["carreras"]
    dominios = json.loads((RAIZ / "data" / "dominios.json").read_text("utf-8"))["dominios"]

    orden_dom = [d["id"] for d in dominios]
    dom_info = {d["id"]: {"nombre": d["nombre"], "icono": d["icono"]} for d in dominios}

    # id_carrera -> lista de dominios a los que pertenece (en orden canónico)
    dom_de = {}
    for d in dominios:
        for cid in d["carreras"]:
            dom_de.setdefault(cid, []).append(d["id"])

    salida = []
    for c in carreras:
        cid = c["id"]
        doms = dom_de.get(cid, [])
        if not doms:                      # carrera sin dominio -> se omite
            continue
        riasec = {d: float(c["riasec"][d]) for d in DIMS}
        salida.append({
            "id": cid,
            "nombre": c["nombre"],
            "dominios": doms,
            "area": c.get("area", ""),
            "duracion": c.get("duracion", "grado"),
            "riasec": riasec,
            "code": codigo_holland(riasec, 3),
            "niveles": {d: nivel(v) for d, v in riasec.items()},
            "etiquetas": c.get("etiquetas", []),
            "universidades": c.get("universidades", []),
        })

    out = {
        "_meta": {
            "descripcion": "Base de conocimiento de ORIENTAI. "
                           "90 carreras, 6 dominios. 'dominios' = lista (una carrera puede "
                           "estar en varios). 'code' = 3 letras RIASEC dominantes.",
            "dominios": dom_info,
            "orden_dominios": orden_dom,
            "total": len(salida),
        },
        "carreras": salida,
    }
    dest = AQUI / "data" / "carreras_reglas.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), "utf-8")
    print(f"OK -> {dest.name}: {len(salida)} carreras en {len(dom_info)} dominios")
    multi = [c for c in salida if len(c["dominios"]) > 1]
    print(f"  ({len(multi)} carreras pertenecen a más de un dominio)")

    preg = json.loads((RAIZ / "data" / "preguntas.json").read_text("utf-8"))

    # ── Preguntas de Fase 1: 18 preguntas Likert, 3 por dominio ──
    f1 = [{"id": q["id"], "dominio": q["dominio"], "texto": q["pregunta"],
           "ponderacion": q.get("ponderacion", 1.0)}
          for q in preg.get("preguntas_fase1", [])]
    out_f1 = {
        "_meta": {"descripcion": "Preguntas de Fase 1 (detección de dominio). Likert 1-5."},
        "fase1_dominio": f1,
    }
    dest_f1 = AQUI / "data" / "f1_reglas.json"
    dest_f1.write_text(json.dumps(out_f1, ensure_ascii=False, indent=2), "utf-8")
    print(f"OK -> {dest_f1.name}: {len(f1)} preguntas de Fase 1")

    # ── Tríadas de Fase 2: comparación forzada 1 de 3 ────────────
    triadas = preg.get("triadas_por_dominio", {})
    out_t = {
        "_meta": {"descripcion": "Tríadas de Fase 2 por dominio (1 de 3, comparación forzada)."},
        "triadas_por_dominio": triadas,
    }
    dest_t = AQUI / "data" / "triadas_reglas.json"
    dest_t.write_text(json.dumps(out_t, ensure_ascii=False, indent=2), "utf-8")
    tot = sum(len(v) for v in triadas.values())
    print(f"OK -> {dest_t.name}: {tot} tríadas en {len(triadas)} dominios")

    # ── Fase 3: pathways + preguntas bipolares con boosts por carrera ──
    fase3 = preg.get("fase3_por_dominio", {})
    out_f3 = {
        "_meta": {"descripcion": "Fase 3 por dominio: cada dominio tiene pathways "
                                 "(sub-perfiles) con dims_trigger y 5 preguntas bipolares; "
                                 "cada polo aporta boosts a carreras específicas."},
        "fase3_por_dominio": fase3,
    }
    dest_f3 = AQUI / "data" / "fase3_reglas.json"
    dest_f3.write_text(json.dumps(out_f3, ensure_ascii=False, indent=2), "utf-8")
    npath = sum(len(v) for v in fase3.values())
    print(f"OK -> {dest_f3.name}: {npath} pathways en {len(fase3)} dominios")


if __name__ == "__main__":
    main()
