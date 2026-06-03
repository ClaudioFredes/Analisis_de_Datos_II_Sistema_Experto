# -*- coding: utf-8 -*-
"""
=================================================================
MOTOR DE INFERENCIA POR REGLAS  (Experta / forward-chaining)
=================================================================
El razonamiento es 100% SIMBÓLICO: hechos + reglas.

HECHOS:
  Carrera(id, nombre, dominios, code, etiquetas)  <- base de conocimiento
  Usuario(dominio, altos, perfil)                 <- perfil del usuario
  Veto(etiqueta)                                  <- deal-breaker (opcional)
  Boost(carrera, valor)                           <- ajuste de Fase 3 por carrera
  Reco(id, nombre, score, afinidad, boost, ...)   <- conclusión inferida

REGLAS:
  R1 (Holland)  : si la carrera pertenece al dominio del usuario y sus letras
                  dominantes coinciden con sus intereses altos, concluye una
                  recomendación con un puntaje de CERTEZA (3/2/1 por posición).
  R2 (Veto)     : si el usuario vetó una etiqueta, retracta toda recomendación
                  de carreras que la tengan.
  R3 (Boost)    : aplica el ajuste de Fase 3 (boost por carrera específica,
                  calculado de las preguntas bipolares del pathway) a su Reco.

DESEMPATE: la CERTEZA (discreta, por reglas) es el orden primario. Para separar
las carreras que empatan, se usa una AFINIDAD continua = intensidad real del
perfil del usuario sobre las letras del código de la carrera (ponderada por
posición). Así el ranking final es fino sin dejar de ser dirigido por reglas.
=================================================================
"""
import compat  # noqa: F401  (aplica shims antes de importar experta)
from experta import KnowledgeEngine, DefFacts, Rule, Fact, MATCH, AS, TEST

DIMS = ("R", "I", "A", "S", "E", "C")
IDX = {d: i for i, d in enumerate(DIMS)}
NOMBRES = {"R": "Realista", "I": "Investigador", "A": "Artístico",
           "S": "Social", "E": "Emprendedor", "C": "Convencional"}
ROLES = ["dominante", "secundaria", "terciaria"]
PESOS = [3, 2, 1]


class Carrera(Fact):
    """Una carrera del catálogo (base de conocimiento)."""
    pass


class Usuario(Fact):
    """Perfil del usuario: dominio elegido, letras altas (frozenset) y
    perfil RIASEC completo (tupla en orden R,I,A,S,E,C) para el desempate."""
    pass


class Veto(Fact):
    """Etiqueta vetada por aversión (Fase 3)."""
    pass


class Boost(Fact):
    """Ajuste de Fase 3: refuerzo acumulado para una carrera específica
    (calculado a partir de las preguntas bipolares del pathway)."""
    pass


class Reco(Fact):
    """Recomendación inferida para una carrera."""
    pass


def letras_altas(perfil: dict) -> list:
    """Letras RIASEC 'altas' del usuario: promedio >= 3.5 (al menos 2, hasta 4)."""
    orden = sorted(DIMS, key=lambda d: -perfil[d])
    altos = [d for d in orden if perfil[d] >= 3.5]
    if len(altos) < 2:
        altos = orden[:2]
    return altos[:4]


def seleccionar_pathway(pathways, perfil):
    """Elige el pathway cuyo `dims_trigger` contiene la dimensión dominante del
    perfil del usuario (igual que el sistema original). Fallback: el primero."""
    if not pathways:
        return None
    top = max(DIMS, key=lambda d: perfil[d])
    for p in pathways:
        if top in p.get("dims_trigger", []):
            return p
    return pathways[0]


def boosts_de_fase3(pathway, respuestas):
    """Acumula los boosts por carrera de la Fase 3 (fórmula del original).

    Para cada pregunta bipolar: factor = (respuesta - 3) / 2  ->  [-1, +1].
      factor < 0  -> aplica boosts_polo_a * |factor|
      factor > 0  -> aplica boosts_polo_b * factor
    """
    acum = {}
    if not pathway:
        return acum
    for q in pathway.get("preguntas", []):
        r = respuestas.get(q["id"])
        if r is None:
            continue
        factor = (r - 3) / 2.0
        if factor < 0:
            for cid, val in q.get("boosts_polo_a", {}).items():
                acum[cid] = acum.get(cid, 0.0) + val * abs(factor)
        elif factor > 0:
            for cid, val in q.get("boosts_polo_b", {}).items():
                acum[cid] = acum.get(cid, 0.0) + val * factor
    return {cid: round(v, 3) for cid, v in acum.items()}


class MotorVocacional(KnowledgeEngine):
    def __init__(self, carreras):
        super().__init__()
        self._carreras = carreras

    @DefFacts()
    def _cargar_base(self):
        for c in self._carreras:
            yield Carrera(
                id=c["id"], nombre=c["nombre"], dominios=tuple(c["dominios"]),
                code=tuple(c["code"]), etiquetas=tuple(c["etiquetas"]),
            )

    # ── R1: emparejamiento por código Holland ─────────────────────
    @Rule(Usuario(dominio=MATCH.dom, altos=MATCH.altos, perfil=MATCH.perfil),
          Carrera(id=MATCH.cid, nombre=MATCH.nom, dominios=MATCH.doms,
                  code=MATCH.code, etiquetas=MATCH.tags),
          TEST(lambda dom, doms: dom in doms),
          salience=30)
    def r_holland(self, dom, altos, perfil, cid, nom, doms, code, tags):
        score, motivos, afinidad = 0, [], 0.0
        for i, letra in enumerate(code):
            afinidad += PESOS[i] * perfil[IDX[letra]]   # desempate (intensidad)
            if letra in altos:
                score += PESOS[i]
                motivos.append(
                    f"Tu interés {NOMBRES[letra]} ({letra}) coincide con la "
                    f"letra {ROLES[i]} de la carrera")
        if score > 0:
            self.declare(Reco(id=cid, nombre=nom, score=score,
                              afinidad=round(afinidad, 3), motivos=tuple(motivos),
                              etiquetas=tuple(tags), code=tuple(code),
                              boost=0.0, f3=False))

    # ── R2: veto por aversión (retracta la recomendación) ─────────
    @Rule(Veto(etiqueta=MATCH.et),
          AS.reco << Reco(etiquetas=MATCH.tags),
          TEST(lambda et, tags: et in tags),
          salience=20)
    def r_veto(self, reco, et, tags):
        self.retract(reco)

    # ── R3: ajuste de Fase 3 (boost a carreras específicas) ───────
    @Rule(Boost(carrera=MATCH.cid, valor=MATCH.v),
          AS.reco << Reco(id=MATCH.cid, boost=MATCH.b, f3=MATCH.done, motivos=MATCH.m),
          TEST(lambda done: not done),
          salience=10)
    def r_boost_f3(self, reco, cid, v, b, done, m):
        self.modify(reco, boost=round(b + v, 3), f3=True,
                    motivos=m + (f"Ajuste de Fase 3 (+{round(v, 2)}) por tus respuestas de valores",))


def _iter_facts(engine):
    """Itera los hechos del motor de forma robusta entre versiones de Experta."""
    fl = engine.facts
    try:
        return list(fl.values())
    except AttributeError:
        return [fl[k] for k in list(fl)]


def recomendar(carreras, dominio, perfil, vetos=(), boosts_f3=None):
    """Corre el motor y devuelve las recomendaciones ordenadas.

    Args:
        carreras:  base de conocimiento (lista de dicts).
        dominio:   id del dominio elegido por el usuario.
        perfil:    dict RIASEC del usuario {R:.., I:.., ...} en escala 1-5.
        vetos:     iterable de etiquetas vetadas (deal-breakers, opcional).
        boosts_f3: dict {carrera_id: refuerzo} acumulado de la Fase 3.

    Returns:
        lista de Reco ordenada por (certeza + boost desc, afinidad desc, nombre).
        El boost de Fase 3 ajusta finamente el orden entre carreras parecidas.
    """
    altos = letras_altas(perfil)
    perfil_t = tuple(float(perfil[d]) for d in DIMS)
    boosts_f3 = boosts_f3 or {}

    eng = MotorVocacional(carreras)
    eng.reset()
    eng.declare(Usuario(dominio=dominio, altos=frozenset(altos), perfil=perfil_t))
    for et in vetos:
        eng.declare(Veto(etiqueta=et))
    for cid, v in boosts_f3.items():
        if v:
            eng.declare(Boost(carrera=cid, valor=round(float(v), 3)))
    eng.run()

    recos = [f for f in _iter_facts(eng) if isinstance(f, Reco)]
    recos.sort(key=lambda r: (-(r["score"] + r["boost"]), -r["afinidad"], r["nombre"]))
    return recos
