"""Agrega el campo 'universidades' a cada carrera en data/carreras.json."""
import json
from pathlib import Path

# Formato: lista de (nombre_corto, ciudad)
# Se prioriza oferta pública y se incluye 1-2 privadas representativas.
UNIV: dict[str, list[tuple[str, str]]] = {
    # ── INGENIERÍA ─────────────────────────────────────────────────
    "ingenieria_mecanica": [
        ("UTN", "Múltiples sedes"), ("UBA – FIUBA", "Buenos Aires"),
        ("UNLP", "La Plata"), ("UNC", "Córdoba"), ("UNT", "Tucumán"),
    ],
    "ingenieria_civil": [
        ("UTN", "Múltiples sedes"), ("UBA – FIUBA", "Buenos Aires"),
        ("UNLP", "La Plata"), ("UNC", "Córdoba"), ("UNR", "Rosario"),
    ],
    "ingenieria_electronica": [
        ("UTN", "Múltiples sedes"), ("UBA – FIUBA", "Buenos Aires"),
        ("UNLP", "La Plata"), ("UNC", "Córdoba"), ("UNT", "Tucumán"),
    ],
    "ingenieria_industrial": [
        ("UTN", "Múltiples sedes"), ("UBA – FIUBA", "Buenos Aires"),
        ("UNLP", "La Plata"), ("UNC", "Córdoba"), ("UNR", "Rosario"),
    ],
    "ingenieria_quimica": [
        ("UBA – FIUBA", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNL", "Santa Fe"), ("UNT", "Tucumán"),
    ],
    "ingenieria_mecatronica": [
        ("UTN – Haedo", "Buenos Aires"), ("UNICEN", "Tandil"),
        ("UNS", "Bahía Blanca"), ("UNSJ", "San Juan"),
    ],
    "ingenieria_electrica": [
        ("UTN", "Múltiples sedes"), ("UBA – FIUBA", "Buenos Aires"),
        ("UNLP", "La Plata"), ("UNC", "Córdoba"),
    ],
    "ingenieria_sistemas": [
        ("UTN", "Múltiples sedes"), ("UBA – FIUBA", "Buenos Aires"),
        ("UNLP", "La Plata"), ("UNC", "Córdoba"), ("UNR", "Rosario"),
    ],
    "ciberseguridad": [
        ("UTN", "Múltiples sedes"), ("UADE", "Buenos Aires"),
        ("UP", "Buenos Aires"), ("UAI", "Buenos Aires"),
    ],
    "tecnologias_digitales": [
        ("UADE", "Buenos Aires"), ("UTN", "Múltiples sedes"),
        ("UAI", "Buenos Aires"), ("UBA – FCEyN", "Buenos Aires"),
    ],
    "tec_programacion": [
        ("UTN", "Múltiples sedes"), ("UNAJ", "Florencio Varela"),
        ("UNNOBA", "Junín / Pergamino"), ("ISFT / Terciarios", "Todo el país"),
    ],
    "ciencia_datos": [
        ("UBA – FCEyN", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UTN", "Múltiples sedes"), ("ITBA", "Buenos Aires"),
    ],
    "tec_energias_renovables": [
        ("UTN", "Múltiples sedes"), ("UNSJ", "San Juan"),
        ("UNCuyo", "Mendoza"),
    ],
    "tec_mantenimiento_industrial": [
        ("UTN", "Múltiples sedes"), ("UNS", "Bahía Blanca"),
        ("UNSJ", "San Juan"),
    ],
    "tec_higiene_seguridad": [
        ("UTN", "Múltiples sedes"), ("UADE", "Buenos Aires"),
        ("UNL", "Santa Fe"),
    ],
    "ingenieria_ambiental": [
        ("UTN", "Múltiples sedes"), ("UNQ", "Quilmes"),
        ("UNICEN", "Tandil"), ("UADER", "Entre Ríos"),
    ],
    "ingenieria_alimentos": [
        ("UBA – FIUBA", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNQ", "Quilmes"), ("UNL", "Santa Fe"), ("UNC", "Córdoba"),
    ],
    "bioingenieria": [
        ("UNT", "Tucumán"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"),
    ],
    "tec_redes": [
        ("UTN", "Múltiples sedes"), ("ISFT / Terciarios", "Todo el país"),
        ("UADE", "Buenos Aires"),
    ],
    # ── CIENCIAS ───────────────────────────────────────────────────
    "biologia": [
        ("UBA – FCEyN", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNMdP", "Mar del Plata"),
    ],
    "quimica": [
        ("UBA – FCEyN", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNL", "Santa Fe"),
    ],
    "matematica": [
        ("UBA – FCEyN", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNS", "Bahía Blanca"),
    ],
    "fisica": [
        ("UBA – FCEyN", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNT", "Tucumán"), ("UNS", "Bahía Blanca"),
    ],
    "biotecnologia": [
        ("UBA – FCEyN", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNQ", "Quilmes"), ("UNL", "Santa Fe"), ("UNC", "Córdoba"),
    ],
    "agronomia": [
        ("UBA – FAUBA", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNT", "Tucumán"),
    ],
    "tec_produccion_agropecuaria": [
        ("UNDEF / Terciarios", "Varias provincias"),
        ("UTN – Agro", "Múltiples sedes"),
    ],
    "geologia": [
        ("UBA – FCEyN", "Buenos Aires"), ("UNC", "Córdoba"),
        ("UNS", "Bahía Blanca"), ("UNSJ", "San Juan"), ("UNPSJB", "Comodoro Rivadavia"),
    ],
    "geografia": [
        ("UBA – FFyL", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"),
    ],
    # ── SALUD ──────────────────────────────────────────────────────
    "medicina": [
        ("UBA", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNT", "Tucumán"),
        ("UNMdP", "Mar del Plata"),
    ],
    "odontologia": [
        ("UBA", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNT", "Tucumán"),
    ],
    "enfermeria": [
        ("UBA", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNT", "Tucumán"),
    ],
    "kinesiologia": [
        ("UBA", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"),
    ],
    "nutricion": [
        ("UBA", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNT", "Tucumán"),
    ],
    "fonoaudiologia": [
        ("UBA", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNT", "Tucumán"),
    ],
    "veterinaria": [
        ("UBA – FVET", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Casilda"), ("UNT", "Tucumán"),
    ],
    "farmacia": [
        ("UBA – FFyB", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNT", "Tucumán"),
    ],
    "tec_laboratorio": [
        ("UNSAM", "Buenos Aires"), ("UTN", "Múltiples sedes"),
        ("ISFT / Terciarios", "Todo el país"),
    ],
    "tec_instrumentacion_quirurgica": [
        ("ISFT / Terciarios", "CABA, Córdoba, Rosario"),
        ("UCES", "Buenos Aires"),
    ],
    "tec_anestesia": [
        ("ISFT / Terciarios", "CABA, La Plata, Córdoba"),
        ("UCES", "Buenos Aires"),
    ],
    "acompanamiento_terapeutico": [
        ("ISFT / Terciarios", "CABA, GBA, Córdoba, Rosario"),
    ],
    "psicopedagogia": [
        ("UBA – FFyL", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UAI", "Buenos Aires"), ("USAL", "Buenos Aires"),
    ],
    "terapia_ocupacional": [
        ("UBA", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"),
    ],
    # ── ARTE Y DISEÑO ──────────────────────────────────────────────
    "gastronomia": [
        ("UNLP", "La Plata"), ("IAG", "Buenos Aires"),
        ("ISCH", "Buenos Aires"), ("Terciarios privados", "Todo el país"),
    ],
    "arquitectura": [
        ("UBA – FADU", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNT", "Tucumán"),
    ],
    "diseno_grafico": [
        ("UBA – FADU", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UP", "Buenos Aires"),
    ],
    "diseno_industrial": [
        ("UBA – FADU", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"),
    ],
    "diseno_indumentaria": [
        ("UBA – FADU", "Buenos Aires"), ("UNA", "Buenos Aires"),
        ("UP", "Buenos Aires"), ("Terciarios", "CABA y GBA"),
    ],
    "diseno_multimedial": [
        ("UNA", "Buenos Aires"), ("UP", "Buenos Aires"),
        ("UNLP", "La Plata"), ("Terciarios", "CABA y GBA"),
    ],
    "diseno_ux_ui": [
        ("UP", "Buenos Aires"), ("UCES", "Buenos Aires"),
        ("UTN – cursos", "Múltiples sedes"), ("Terciarios", "CABA y GBA"),
    ],
    "artes_visuales": [
        ("UNA", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNSAM", "Buenos Aires"),
    ],
    "musica": [
        ("UNA", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNT", "Tucumán"), ("UNMdP", "Mar del Plata"),
    ],
    "artes_audiovisuales": [
        ("UNA", "Buenos Aires"), ("UNTREF", "Buenos Aires"),
        ("UNC", "Córdoba"), ("UNSAM", "Buenos Aires"), ("UP", "Buenos Aires"),
    ],
    "fotografia": [
        ("UNTREF", "Buenos Aires"), ("UP", "Buenos Aires"),
        ("Terciarios", "CABA y GBA"),
    ],
    "actuacion": [
        ("UNA – IUNA", "Buenos Aires"), ("UNC", "Córdoba"),
        ("Conservatorios", "CABA, Córdoba, Rosario"),
    ],
    "creacion_videojuegos": [
        ("UTN", "Múltiples sedes"), ("UP", "Buenos Aires"),
        ("UADE", "Buenos Aires"), ("CAECE", "Buenos Aires"),
    ],
    # ── HUMANIDADES Y CS SOCIALES ──────────────────────────────────
    "psicologia": [
        ("UBA – FFYB", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNT", "Tucumán"),
    ],
    "trabajo_social": [
        ("UBA – FSOC", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNT", "Tucumán"),
    ],
    "sociologia": [
        ("UBA – FSOC", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"),
    ],
    "ciencia_politica": [
        ("UBA – FSOC", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"),
    ],
    "abogacia": [
        ("UBA – Derecho", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNT", "Tucumán"),
        ("UNMdP", "Mar del Plata"),
    ],
    "comunicacion_social": [
        ("UBA – FSOC", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNT", "Tucumán"),
    ],
    "letras": [
        ("UBA – FFyL", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNT", "Tucumán"),
    ],
    "traductorado": [
        ("UBA – FFYL", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("IES / Institutos", "Todo el país"),
    ],
    "archivologia": [
        ("UBA – FFyL", "Buenos Aires"), ("UNMdP", "Mar del Plata"),
        ("UNL", "Santa Fe"),
    ],
    "ciencias_educacion": [
        ("UBA – FFYL", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"),
    ],
    "profesorado_educacion_primaria": [
        ("ISFD / Institutos terciarios", "Todo el país"),
        ("UNC", "Córdoba"), ("UNLP", "La Plata"),
    ],
    "profesorado_ciencias_exactas": [
        ("ISFD / Institutos terciarios", "Todo el país"),
        ("UTN", "Múltiples sedes"), ("UNC", "Córdoba"),
    ],
    "historia": [
        ("UBA – FFyL", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNT", "Tucumán"),
    ],
    "filosofia": [
        ("UBA – FFyL", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"),
    ],
    "educacion_fisica": [
        ("UNLP – FHCE", "La Plata"), ("UNC", "Córdoba"),
        ("UNTREF", "Buenos Aires"), ("ISEF / Institutos", "Todo el país"),
    ],
    # ── NEGOCIOS ───────────────────────────────────────────────────
    "administracion_empresas": [
        ("UBA – FCE", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UADE", "Buenos Aires"),
    ],
    "marketing": [
        ("UBA – FCE", "Buenos Aires"), ("UADE", "Buenos Aires"),
        ("UP", "Buenos Aires"), ("UAI", "Buenos Aires"),
    ],
    "relaciones_publicas": [
        ("UADE", "Buenos Aires"), ("USAL", "Buenos Aires"),
        ("UP", "Buenos Aires"), ("UAI", "Buenos Aires"),
    ],
    "recursos_humanos": [
        ("UBA – FCE", "Buenos Aires"), ("UADE", "Buenos Aires"),
        ("UAI", "Buenos Aires"), ("USAL", "Buenos Aires"),
    ],
    "comercio_internacional": [
        ("UBA – FCE", "Buenos Aires"), ("UADE", "Buenos Aires"),
        ("UAI", "Buenos Aires"), ("UCES", "Buenos Aires"),
    ],
    "negocios_digitales": [
        ("UADE", "Buenos Aires"), ("UP", "Buenos Aires"),
        ("UAI", "Buenos Aires"), ("Terciarios", "CABA y GBA"),
    ],
    "tec_turismo": [
        ("Terciarios", "Todo el país"), ("UNA", "Buenos Aires"),
        ("UNLP", "La Plata"),
    ],
    "lic_turismo": [
        ("UNLP", "La Plata"), ("UNC", "Córdoba"),
        ("UNComahue", "Neuquén"), ("UNMdP", "Mar del Plata"),
    ],
    "martillero_publico": [
        ("Colegios de Martilleros", "CABA, La Plata, Córdoba, Rosario"),
        ("UADE", "Buenos Aires"), ("UAI", "Buenos Aires"),
    ],
    "contador_publico": [
        ("UBA – FCE", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNT", "Tucumán"),
    ],
    "economia": [
        ("UBA – FCE", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNT", "Tucumán"),
    ],
    "finanzas": [
        ("UBA – FCE", "Buenos Aires"), ("UADE", "Buenos Aires"),
        ("USAL", "Buenos Aires"), ("UP", "Buenos Aires"),
    ],
    "actuario": [
        ("UBA – FCE", "Buenos Aires"), ("UNC", "Córdoba"),
    ],
    "administracion_publica": [
        ("UBA – FCE", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNSAM", "Buenos Aires"),
    ],
    "logistica": [
        ("UTN", "Múltiples sedes"), ("UADE", "Buenos Aires"),
        ("USAL", "Buenos Aires"), ("UAI", "Buenos Aires"),
    ],
    "tec_administracion_contable": [
        ("UTN", "Múltiples sedes"), ("UADE", "Buenos Aires"),
        ("ISFT / Terciarios", "Todo el país"),
    ],
    "secretariado_ejecutivo": [
        ("USAL", "Buenos Aires"), ("UCES", "Buenos Aires"),
        ("Terciarios", "CABA y GBA"),
    ],
    "relaciones_internacionales": [
        ("UBA – FSOC", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("USAL", "Buenos Aires"),
    ],
    "escribania": [
        ("UBA – Derecho", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNT", "Tucumán"),
    ],
    "lic_computacion": [
        ("UBA – FCEyN", "Buenos Aires"), ("UNLP", "La Plata"),
        ("UNC", "Córdoba"), ("UNR", "Rosario"), ("UNS", "Bahía Blanca"),
    ],
}

PATH = Path(__file__).parent.parent / "data" / "carreras.json"
data = json.loads(PATH.read_text(encoding="utf-8"))

sin_datos = []
for c in data["carreras"]:
    cid = c["id"]
    if cid in UNIV:
        c["universidades"] = [
            {"nombre": n, "ciudad": ciudad}
            for n, ciudad in UNIV[cid]
        ]
    else:
        c["universidades"] = []
        sin_datos.append(cid)

PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"OK - {len(data['carreras'])} carreras actualizadas.")
if sin_datos:
    print(f"Sin datos: {sin_datos}")
