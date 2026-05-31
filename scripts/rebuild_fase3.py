"""
Reemplaza fase3_por_dominio en preguntas.json con la nueva estructura
de preguntas de valores y contexto (escala bipolar 1-5).
"""
import json
from pathlib import Path

NUEVA_F3 = {
  "tecnologia": [
    {
      "id": "tec_analitica",
      "nombre": "Analítica & Software",
      "descripcion": "Tu perfil muestra preferencia por el análisis, los algoritmos y la construcción de sistemas de software.",
      "dims_trigger": ["I", "C"],
      "preguntas": [
        {
          "id": "TF3_01",
          "pregunta": "¿Cómo preferís trabajar habitualmente?",
          "polo_a": "Solo, con autonomía, en tareas técnicas profundas",
          "polo_b": "En equipo, con comunicación y coordinación constante",
          "boosts_polo_a": {"ciberseguridad": 0.12, "tec_programacion": 0.10, "lic_computacion": 0.08},
          "boosts_polo_b": {"tecnologias_digitales": 0.12, "ingenieria_sistemas": 0.08}
        },
        {
          "id": "TF3_02",
          "pregunta": "¿Qué tipo de problema te resulta más atractivo?",
          "polo_a": "Un problema bien definido con una solución correcta",
          "polo_b": "Un problema abierto sin una única respuesta",
          "boosts_polo_a": {"tec_programacion": 0.12, "ciberseguridad": 0.10},
          "boosts_polo_b": {"ciencia_datos": 0.12, "lic_computacion": 0.08}
        },
        {
          "id": "TF3_03",
          "pregunta": "¿Qué ritmo de resultados preferís?",
          "polo_a": "Ver el resultado de mi trabajo en días o semanas",
          "polo_b": "Proyectos de largo plazo cuyo impacto es gradual",
          "boosts_polo_a": {"tec_programacion": 0.12, "tecnologias_digitales": 0.08},
          "boosts_polo_b": {"ciencia_datos": 0.12, "lic_computacion": 0.10}
        },
        {
          "id": "TF3_04",
          "pregunta": "¿Cómo preferís desarrollarte profesionalmente?",
          "polo_a": "Especializarme en una tecnología hasta dominarla profundamente",
          "polo_b": "Moverme entre distintas áreas según el problema",
          "boosts_polo_a": {"ciberseguridad": 0.12, "ciencia_datos": 0.10},
          "boosts_polo_b": {"ingenieria_sistemas": 0.12, "tecnologias_digitales": 0.10}
        },
        {
          "id": "TF3_05",
          "pregunta": "¿Qué entorno de trabajo te atrae más?",
          "polo_a": "Contextos estables y predecibles, con procesos maduros",
          "polo_b": "Entornos de cambio rápido e incertidumbre constante",
          "boosts_polo_a": {"tec_programacion": 0.10, "ciberseguridad": 0.10, "ingenieria_sistemas": 0.08},
          "boosts_polo_b": {"ciencia_datos": 0.12, "tecnologias_digitales": 0.10}
        }
      ]
    },
    {
      "id": "tec_hardware",
      "nombre": "Hardware & Sistemas Físicos",
      "descripcion": "Tu perfil muestra preferencia por los sistemas físicos, la infraestructura y el trabajo técnico con equipos.",
      "dims_trigger": ["R"],
      "preguntas": [
        {
          "id": "TF3_06",
          "pregunta": "¿Qué tipo de trabajo físico preferís?",
          "polo_a": "Trabajo con las manos en equipos y materiales en el lugar",
          "polo_b": "Trabajo sentado diseñando, calculando y planificando",
          "boosts_polo_a": {"tec_mantenimiento_industrial": 0.12, "tec_redes": 0.10},
          "boosts_polo_b": {"ingenieria_civil": 0.12, "ingenieria_mecanica": 0.10, "ingenieria_mecatronica": 0.08}
        },
        {
          "id": "TF3_07",
          "pregunta": "¿Qué actividad te resulta más satisfactoria?",
          "polo_a": "Mantener y mejorar sistemas que ya existen",
          "polo_b": "Diseñar e implementar sistemas desde cero",
          "boosts_polo_a": {"tec_mantenimiento_industrial": 0.12, "tec_redes": 0.08},
          "boosts_polo_b": {"ingenieria_mecanica": 0.12, "ingenieria_mecatronica": 0.10, "ingenieria_civil": 0.08}
        },
        {
          "id": "TF3_08",
          "pregunta": "¿Cómo preferís desarrollarte técnicamente?",
          "polo_a": "Dominar profundamente un área técnica específica",
          "polo_b": "Gestionar proyectos integrando distintas disciplinas",
          "boosts_polo_a": {"ingenieria_electronica": 0.12, "ingenieria_electrica": 0.10, "tec_energias_renovables": 0.08},
          "boosts_polo_b": {"ingenieria_industrial": 0.12, "ingenieria_mecatronica": 0.10}
        },
        {
          "id": "TF3_09",
          "pregunta": "¿Dónde preferís trabajar habitualmente?",
          "polo_a": "En fábricas, plantas o talleres cerrados",
          "polo_b": "En obras, campo abierto o infraestructura exterior",
          "boosts_polo_a": {"tec_mantenimiento_industrial": 0.12, "ingenieria_electronica": 0.08},
          "boosts_polo_b": {"ingenieria_civil": 0.12, "tec_energias_renovables": 0.10, "ingenieria_ambiental": 0.08}
        },
        {
          "id": "TF3_10",
          "pregunta": "¿Qué impacto te motiva más de tu trabajo?",
          "polo_a": "La eficiencia y la productividad del sistema",
          "polo_b": "El impacto ambiental y la sustentabilidad",
          "boosts_polo_a": {"ingenieria_industrial": 0.12, "ingenieria_mecanica": 0.10, "tec_mantenimiento_industrial": 0.08},
          "boosts_polo_b": {"tec_energias_renovables": 0.12, "ingenieria_ambiental": 0.12}
        }
      ]
    },
    {
      "id": "tec_creativo",
      "nombre": "Diseño Digital & Gestión Tech",
      "descripcion": "Tu perfil combina tecnología con creatividad o con la visión estratégica de proyectos y productos digitales.",
      "dims_trigger": ["A", "E", "S"],
      "preguntas": [
        {
          "id": "TF3_11",
          "pregunta": "¿Qué tipo de creación te impulsa más?",
          "polo_a": "Crear con libertad total, sin restricciones de cliente",
          "polo_b": "Diseñar para resolver necesidades concretas de usuarios",
          "boosts_polo_a": {"creacion_videojuegos": 0.12, "diseno_multimedial": 0.10},
          "boosts_polo_b": {"diseno_ux_ui": 0.12, "tecnologias_digitales": 0.08}
        },
        {
          "id": "TF3_12",
          "pregunta": "¿Cuál es tu rol preferido en un proyecto?",
          "polo_a": "Ejecutar y producir el trabajo creativo o técnico",
          "polo_b": "Liderar, coordinar y llevar la visión estratégica",
          "boosts_polo_a": {"diseno_ux_ui": 0.10, "diseno_multimedial": 0.10, "creacion_videojuegos": 0.08},
          "boosts_polo_b": {"tecnologias_digitales": 0.12, "ingenieria_industrial": 0.10}
        },
        {
          "id": "TF3_13",
          "pregunta": "¿Qué ciclo de proyecto te atrae más?",
          "polo_a": "Proyectos cortos con resultados visibles en semanas",
          "polo_b": "Proyectos largos y complejos de varios meses",
          "boosts_polo_a": {"diseno_ux_ui": 0.12, "diseno_multimedial": 0.08},
          "boosts_polo_b": {"creacion_videojuegos": 0.12, "tecnologias_digitales": 0.10}
        },
        {
          "id": "TF3_14",
          "pregunta": "¿Qué aspecto del trabajo creativo te apasiona más?",
          "polo_a": "La precisión técnica: el código, las herramientas, los detalles",
          "polo_b": "El concepto y la idea detrás del diseño",
          "boosts_polo_a": {"creacion_videojuegos": 0.12, "diseno_multimedial": 0.08},
          "boosts_polo_b": {"diseno_ux_ui": 0.12, "tecnologias_digitales": 0.08}
        },
        {
          "id": "TF3_15",
          "pregunta": "¿Qué tipo de organización preferís?",
          "polo_a": "Equipos pequeños y ágiles con mucha autonomía",
          "polo_b": "Estructuras organizadas con roles y procesos definidos",
          "boosts_polo_a": {"creacion_videojuegos": 0.12, "diseno_ux_ui": 0.08},
          "boosts_polo_b": {"tecnologias_digitales": 0.12, "ingenieria_industrial": 0.10}
        }
      ]
    }
  ],
  "ciencias": [
    {
      "id": "cn_teorica",
      "nombre": "Investigación Teórica",
      "descripcion": "Tu perfil muestra inclinación hacia la ciencia abstracta, el modelado matemático y la investigación de fondo.",
      "dims_trigger": ["I", "C"],
      "preguntas": [
        {
          "id": "CF3_01",
          "pregunta": "¿Qué tipo de conocimiento te atrae más construir?",
          "polo_a": "Modelos matemáticos y teorías abstractas y formales",
          "polo_b": "Resultados empíricos obtenidos de experimentos y datos",
          "boosts_polo_a": {"matematica": 0.14, "fisica": 0.12},
          "boosts_polo_b": {"biologia": 0.12, "biotecnologia": 0.10, "quimica": 0.10}
        },
        {
          "id": "CF3_02",
          "pregunta": "¿Qué relación tenés con la incertidumbre en tu trabajo?",
          "polo_a": "Me atraen los resultados exactos y las demostraciones rigurosas",
          "polo_b": "Disfruto explorar sin saber con certeza adónde lleva",
          "boosts_polo_a": {"matematica": 0.14},
          "boosts_polo_b": {"biologia": 0.10, "biotecnologia": 0.12, "bioingenieria": 0.10}
        },
        {
          "id": "CF3_03",
          "pregunta": "¿En qué contexto te imaginás trabajando?",
          "polo_a": "La academia: investigar, publicar y enseñar en universidad",
          "polo_b": "La industria: que mi conocimiento tenga impacto clínico o productivo",
          "boosts_polo_a": {"matematica": 0.12, "fisica": 0.12, "biologia": 0.10},
          "boosts_polo_b": {"biotecnologia": 0.12, "bioingenieria": 0.12, "ingenieria_quimica": 0.08, "ingenieria_alimentos": 0.08}
        },
        {
          "id": "CF3_04",
          "pregunta": "¿Cómo preferís trabajar en tu investigación?",
          "polo_a": "Solo, con mucha concentración e independencia",
          "polo_b": "Colaborando con otros investigadores y grupos",
          "boosts_polo_a": {"matematica": 0.12, "fisica": 0.10},
          "boosts_polo_b": {"biotecnologia": 0.12, "bioingenieria": 0.10, "biologia": 0.08}
        },
        {
          "id": "CF3_05",
          "pregunta": "¿Qué horizonte temporal de impacto aceptás?",
          "polo_a": "Mis resultados pueden tardar años o décadas en tener impacto",
          "polo_b": "Necesito ver la utilidad concreta de mi trabajo en el corto plazo",
          "boosts_polo_a": {"matematica": 0.12, "fisica": 0.12, "biologia": 0.08},
          "boosts_polo_b": {"ingenieria_quimica": 0.12, "ingenieria_alimentos": 0.10, "bioingenieria": 0.10}
        }
      ]
    },
    {
      "id": "cn_experimental",
      "nombre": "Ciencia Experimental & De Campo",
      "descripcion": "Tu perfil muestra preferencia por el trabajo práctico, el laboratorio y la exploración del mundo natural.",
      "dims_trigger": ["R"],
      "preguntas": [
        {
          "id": "CF3_06",
          "pregunta": "¿Dónde preferís desarrollar tu trabajo científico?",
          "polo_a": "En el campo, en la naturaleza, al aire libre",
          "polo_b": "En el laboratorio, con microscopio y reactivos",
          "boosts_polo_a": {"geologia": 0.14, "agronomia": 0.12, "tec_produccion_agropecuaria": 0.10, "geografia": 0.10},
          "boosts_polo_b": {"quimica": 0.12, "tec_laboratorio": 0.12, "biotecnologia": 0.08}
        },
        {
          "id": "CF3_07",
          "pregunta": "¿Qué objetivo final te motiva más?",
          "polo_a": "Producir: procesos industriales con resultados concretos",
          "polo_b": "Investigar: entender los mecanismos fundamentales",
          "boosts_polo_a": {"agronomia": 0.12, "tec_produccion_agropecuaria": 0.12, "ingenieria_alimentos": 0.10},
          "boosts_polo_b": {"biologia": 0.12, "quimica": 0.10, "geologia": 0.08}
        },
        {
          "id": "CF3_08",
          "pregunta": "¿Qué objeto de estudio te atrae más?",
          "polo_a": "Los seres vivos: plantas, animales, microorganismos",
          "polo_b": "Los materiales: rocas, suelos, sustancias químicas",
          "boosts_polo_a": {"biologia": 0.12, "agronomia": 0.10, "tec_produccion_agropecuaria": 0.10, "biotecnologia": 0.08},
          "boosts_polo_b": {"quimica": 0.12, "geologia": 0.12, "ingenieria_quimica": 0.08, "tec_laboratorio": 0.08}
        },
        {
          "id": "CF3_09",
          "pregunta": "¿Cómo preferís estructurar tu trabajo?",
          "polo_a": "Diseñar y ejecutar experimentos de forma independiente",
          "polo_b": "Trabajar en equipos técnicos con roles complementarios",
          "boosts_polo_a": {"biologia": 0.10, "quimica": 0.10, "geologia": 0.10},
          "boosts_polo_b": {"ingenieria_alimentos": 0.12, "tec_laboratorio": 0.10, "biotecnologia": 0.10}
        },
        {
          "id": "CF3_10",
          "pregunta": "¿En qué escala preferís operar?",
          "polo_a": "Precisión y detalle a escala pequeña: moléculas, muestras",
          "polo_b": "Impacto a gran escala: producción, territorios, ecosistemas",
          "boosts_polo_a": {"tec_laboratorio": 0.12, "quimica": 0.10},
          "boosts_polo_b": {"agronomia": 0.12, "geologia": 0.10, "ingenieria_alimentos": 0.10, "geografia": 0.08}
        }
      ]
    },
    {
      "id": "cn_aplicada",
      "nombre": "Ciencia Aplicada & Ambiental",
      "descripcion": "Tu perfil apunta hacia la ciencia en contextos concretos: medioambiente, producción, industria.",
      "dims_trigger": ["E", "S", "A"],
      "preguntas": [
        {
          "id": "CF3_11",
          "pregunta": "¿Cuál es tu motivación principal como científico/a?",
          "polo_a": "Proteger y restaurar el medioambiente",
          "polo_b": "Optimizar la producción y los procesos industriales",
          "boosts_polo_a": {"ingenieria_ambiental": 0.14, "geografia": 0.10},
          "boosts_polo_b": {"agronomia": 0.12, "ingenieria_alimentos": 0.12, "tec_produccion_agropecuaria": 0.08}
        },
        {
          "id": "CF3_12",
          "pregunta": "¿En qué sector te imaginás trabajando?",
          "polo_a": "Organismos públicos, municipios o ONGs",
          "polo_b": "Empresas privadas, consultoras o laboratorios",
          "boosts_polo_a": {"ingenieria_ambiental": 0.12, "geografia": 0.10},
          "boosts_polo_b": {"ingenieria_alimentos": 0.12, "biotecnologia": 0.10, "ingenieria_quimica": 0.10}
        },
        {
          "id": "CF3_13",
          "pregunta": "¿Dónde preferís trabajar?",
          "polo_a": "En el territorio: campo, obras o instalaciones",
          "polo_b": "En laboratorio u oficina técnica",
          "boosts_polo_a": {"agronomia": 0.12, "tec_produccion_agropecuaria": 0.12, "geologia": 0.08},
          "boosts_polo_b": {"tec_laboratorio": 0.12, "biotecnologia": 0.10, "ingenieria_alimentos": 0.08}
        },
        {
          "id": "CF3_14",
          "pregunta": "¿Qué impulsa más tu curiosidad profesional?",
          "polo_a": "Tecnologías de punta y alta innovación",
          "polo_b": "Procesos probados y bien establecidos para optimizarlos",
          "boosts_polo_a": {"biotecnologia": 0.12, "bioingenieria": 0.12},
          "boosts_polo_b": {"ingenieria_alimentos": 0.10, "quimica": 0.10, "tec_laboratorio": 0.08}
        },
        {
          "id": "CF3_15",
          "pregunta": "¿Qué tipo de impacto valorás más?",
          "polo_a": "El impacto en comunidades y en la sociedad",
          "polo_b": "La precisión técnica y los resultados medibles",
          "boosts_polo_a": {"ingenieria_ambiental": 0.12, "agronomia": 0.10},
          "boosts_polo_b": {"ingenieria_alimentos": 0.12, "biotecnologia": 0.10, "ingenieria_quimica": 0.08}
        }
      ]
    }
  ],
  "salud": [
    {
      "id": "sa_clinica",
      "nombre": "Atención Clínica Directa",
      "descripcion": "Tu perfil muestra vocación por el trato directo con personas: diagnosticar, tratar y acompañar pacientes.",
      "dims_trigger": ["S", "R"],
      "preguntas": [
        {
          "id": "SF3_01",
          "pregunta": "¿Qué ritmo de trabajo clínico preferís?",
          "polo_a": "La urgencia: situaciones críticas donde cada minuto importa",
          "polo_b": "El seguimiento a largo plazo y la evolución del paciente",
          "boosts_polo_a": {"medicina": 0.12, "enfermeria": 0.10, "tec_anestesia": 0.10},
          "boosts_polo_b": {"kinesiologia": 0.12, "nutricion": 0.12, "fonoaudiologia": 0.08}
        },
        {
          "id": "SF3_02",
          "pregunta": "¿Qué aspecto del trabajo de salud te atrae más?",
          "polo_a": "La parte técnica y manual: procedimientos, cirugías, técnicas",
          "polo_b": "Acompañar, enseñar y guiar al paciente en su proceso",
          "boosts_polo_a": {"odontologia": 0.12, "tec_instrumentacion_quirurgica": 0.12, "tec_anestesia": 0.10, "kinesiologia": 0.08},
          "boosts_polo_b": {"nutricion": 0.12, "fonoaudiologia": 0.10, "psicopedagogia": 0.08}
        },
        {
          "id": "SF3_03",
          "pregunta": "¿Qué es lo más importante para vos en la relación con el paciente?",
          "polo_a": "El vínculo humano: escuchar, contener, estar presente",
          "polo_b": "La resolución clínica y biológica del problema",
          "boosts_polo_a": {"enfermeria": 0.12, "psicopedagogia": 0.10, "fonoaudiologia": 0.08},
          "boosts_polo_b": {"medicina": 0.12, "odontologia": 0.10, "veterinaria": 0.08}
        },
        {
          "id": "SF3_04",
          "pregunta": "¿Qué parte del proceso clínico disfrutás más?",
          "polo_a": "Analizar, interpretar síntomas y llegar a un diagnóstico",
          "polo_b": "Ejecutar: operar, rehabilitar, intervenir",
          "boosts_polo_a": {"medicina": 0.12, "nutricion": 0.10},
          "boosts_polo_b": {"odontologia": 0.12, "kinesiologia": 0.12, "tec_instrumentacion_quirurgica": 0.08}
        },
        {
          "id": "SF3_05",
          "pregunta": "¿Cómo preferís ejercer la profesión?",
          "polo_a": "Como parte de un equipo interdisciplinario",
          "polo_b": "De forma independiente, con tu propia práctica",
          "boosts_polo_a": {"medicina": 0.10, "enfermeria": 0.12, "tec_anestesia": 0.08},
          "boosts_polo_b": {"nutricion": 0.12, "odontologia": 0.10, "kinesiologia": 0.10, "veterinaria": 0.08}
        }
      ]
    },
    {
      "id": "sa_tecnico",
      "nombre": "Técnico & Diagnóstico",
      "descripcion": "Tu perfil apunta hacia roles técnicos de análisis, apoyo en procedimientos o gestión farmacéutica.",
      "dims_trigger": ["I", "C"],
      "preguntas": [
        {
          "id": "SF3_06",
          "pregunta": "¿Cuánto contacto directo con pacientes querés en tu trabajo?",
          "polo_a": "Prefiero el rol técnico, con mínima interacción con pacientes",
          "polo_b": "Aunque sea técnico, quiero interactuar con los pacientes",
          "boosts_polo_a": {"tec_laboratorio": 0.12, "farmacia": 0.12},
          "boosts_polo_b": {"tec_instrumentacion_quirurgica": 0.10, "tec_anestesia": 0.10, "enfermeria": 0.08}
        },
        {
          "id": "SF3_07",
          "pregunta": "¿Qué entorno clínico te atrae más?",
          "polo_a": "Máxima precisión y control: nada puede salir mal",
          "polo_b": "Situaciones cambiantes que requieren adaptar la respuesta",
          "boosts_polo_a": {"tec_laboratorio": 0.12, "farmacia": 0.12},
          "boosts_polo_b": {"tec_anestesia": 0.12, "tec_instrumentacion_quirurgica": 0.10}
        },
        {
          "id": "SF3_08",
          "pregunta": "¿Cómo preferís tomar decisiones en el trabajo?",
          "polo_a": "Siguiendo protocolos establecidos y normas claras",
          "polo_b": "Con autonomía para tomar decisiones técnicas propias",
          "boosts_polo_a": {"tec_laboratorio": 0.12, "farmacia": 0.10},
          "boosts_polo_b": {"medicina": 0.10, "tec_anestesia": 0.10}
        },
        {
          "id": "SF3_09",
          "pregunta": "¿Qué dimensión del trabajo de salud te motiva más?",
          "polo_a": "La investigación: nuevos fármacos, nuevas técnicas",
          "polo_b": "La aplicación clínica directa y el trabajo con pacientes",
          "boosts_polo_a": {"farmacia": 0.12, "tec_laboratorio": 0.10},
          "boosts_polo_b": {"tec_instrumentacion_quirurgica": 0.12, "tec_anestesia": 0.10, "enfermeria": 0.08}
        },
        {
          "id": "SF3_10",
          "pregunta": "¿Qué escala de impacto te importa más?",
          "polo_a": "El impacto directo en cada paciente que atiendo",
          "polo_b": "Mejorar el sistema de salud a escala más amplia",
          "boosts_polo_a": {"tec_instrumentacion_quirurgica": 0.12, "tec_anestesia": 0.10, "farmacia": 0.08},
          "boosts_polo_b": {"tec_laboratorio": 0.12, "medicina": 0.08}
        }
      ]
    },
    {
      "id": "sa_apoyo",
      "nombre": "Apoyo Terapéutico & Rehabilitación",
      "descripcion": "Tu perfil muestra vocación por el acompañamiento, la rehabilitación y el desarrollo de las personas.",
      "dims_trigger": ["A", "E"],
      "preguntas": [
        {
          "id": "SF3_11",
          "pregunta": "¿Qué ritmo de cambio esperás ver en los pacientes?",
          "polo_a": "Tolero bien la lentitud: los cambios llevan meses o años",
          "polo_b": "Prefiero procesos donde los resultados son más rápidos",
          "boosts_polo_a": {"acompanamiento_terapeutico": 0.14, "psicopedagogia": 0.10},
          "boosts_polo_b": {"kinesiologia": 0.12, "fonoaudiologia": 0.10}
        },
        {
          "id": "SF3_12",
          "pregunta": "¿Qué tipo de vínculo terapéutico preferís?",
          "polo_a": "El vínculo emocional profundo es lo central de mi trabajo",
          "polo_b": "Prefiero un rol técnico donde el vínculo es secundario",
          "boosts_polo_a": {"acompanamiento_terapeutico": 0.14, "psicopedagogia": 0.10},
          "boosts_polo_b": {"kinesiologia": 0.12, "fonoaudiologia": 0.10, "terapia_ocupacional": 0.08}
        },
        {
          "id": "SF3_13",
          "pregunta": "¿Dónde preferís trabajar?",
          "polo_a": "Inserto/a en una institución: escuela, hospital, ONG",
          "polo_b": "En consultorio propio o como profesional autónomo/a",
          "boosts_polo_a": {"terapia_ocupacional": 0.12, "psicopedagogia": 0.10},
          "boosts_polo_b": {"acompanamiento_terapeutico": 0.12, "fonoaudiologia": 0.10}
        },
        {
          "id": "SF3_14",
          "pregunta": "¿Qué herramienta terapéutica preferís usar?",
          "polo_a": "Actividades creativas, lúdicas y artísticas",
          "polo_b": "Técnicas estructuradas y protocolos terapéuticos",
          "boosts_polo_a": {"terapia_ocupacional": 0.14, "acompanamiento_terapeutico": 0.10},
          "boosts_polo_b": {"fonoaudiologia": 0.12, "kinesiologia": 0.10, "psicopedagogia": 0.08}
        },
        {
          "id": "SF3_15",
          "pregunta": "¿Con qué población preferís trabajar?",
          "polo_a": "Principalmente con niños y adolescentes",
          "polo_b": "Con adultos, adultos mayores o situaciones de crisis",
          "boosts_polo_a": {"psicopedagogia": 0.12, "fonoaudiologia": 0.10},
          "boosts_polo_b": {"acompanamiento_terapeutico": 0.12, "terapia_ocupacional": 0.10}
        }
      ]
    }
  ],
  "arte": [
    {
      "id": "ar_visual",
      "nombre": "Creación Visual & Audiovisual",
      "descripcion": "Tu perfil muestra inclinación hacia la expresión artística, el diseño visual y la producción de imágenes.",
      "dims_trigger": ["A", "R"],
      "preguntas": [
        {
          "id": "ARF3_01",
          "pregunta": "¿Qué impulsa más tu creación?",
          "polo_a": "La expresión personal, el arte propio sin restricciones",
          "polo_b": "El diseño al servicio de una idea o necesidad del cliente",
          "boosts_polo_a": {"artes_visuales": 0.12, "musica": 0.10, "actuacion": 0.08, "fotografia": 0.08},
          "boosts_polo_b": {"diseno_grafico": 0.12, "diseno_industrial": 0.10, "diseno_indumentaria": 0.08}
        },
        {
          "id": "ARF3_02",
          "pregunta": "¿Cómo preferís crear?",
          "polo_a": "En soledad, con total control del proceso creativo",
          "polo_b": "En un equipo creativo colaborativo",
          "boosts_polo_a": {"artes_visuales": 0.12, "musica": 0.10, "fotografia": 0.10},
          "boosts_polo_b": {"artes_audiovisuales": 0.12, "diseno_multimedial": 0.10, "creacion_videojuegos": 0.08}
        },
        {
          "id": "ARF3_03",
          "pregunta": "¿Qué tipo de obra te atrae más crear?",
          "polo_a": "Arte en vivo: el momento único e irrepetible",
          "polo_b": "Obras físicas o digitales que perduran",
          "boosts_polo_a": {"actuacion": 0.14, "musica": 0.10},
          "boosts_polo_b": {"arquitectura": 0.12, "diseno_industrial": 0.10, "artes_visuales": 0.08, "fotografia": 0.08}
        },
        {
          "id": "ARF3_04",
          "pregunta": "¿En tu proceso creativo, qué manda más?",
          "polo_a": "La intuición y la espontaneidad",
          "polo_b": "La técnica, el oficio y la precisión",
          "boosts_polo_a": {"actuacion": 0.12, "artes_visuales": 0.10},
          "boosts_polo_b": {"arquitectura": 0.12, "diseno_industrial": 0.10, "diseno_grafico": 0.08, "musica": 0.08}
        },
        {
          "id": "ARF3_05",
          "pregunta": "¿Qué valorás más en tu trabajo creativo?",
          "polo_a": "El valor artístico y la expresión por sobre la utilidad",
          "polo_b": "Que el trabajo tenga una función concreta y útil",
          "boosts_polo_a": {"artes_visuales": 0.12, "musica": 0.10, "actuacion": 0.10},
          "boosts_polo_b": {"arquitectura": 0.12, "diseno_industrial": 0.10, "diseno_indumentaria": 0.08, "diseno_grafico": 0.08}
        }
      ]
    },
    {
      "id": "ar_comunicacion",
      "nombre": "Comunicación & Producción",
      "descripcion": "Tu perfil combina el arte con la comunicación de ideas, el trabajo en equipo y la producción de contenidos.",
      "dims_trigger": ["E", "S"],
      "preguntas": [
        {
          "id": "ARF3_06",
          "pregunta": "¿Qué rol preferís en una producción artística o comunicacional?",
          "polo_a": "El protagonismo: actuar, presentar, estar en primer plano",
          "polo_b": "Producir y coordinar para que otros brillen",
          "boosts_polo_a": {"actuacion": 0.14, "comunicacion_social": 0.08},
          "boosts_polo_b": {"artes_audiovisuales": 0.12, "diseno_grafico": 0.10, "relaciones_publicas": 0.08}
        },
        {
          "id": "ARF3_07",
          "pregunta": "¿Qué tipo de contenido te motiva más crear?",
          "polo_a": "Ficción: crear mundos, personajes, historias",
          "polo_b": "Realidad: informar, documentar, comunicar hechos",
          "boosts_polo_a": {"actuacion": 0.12, "letras": 0.12, "musica": 0.08},
          "boosts_polo_b": {"comunicacion_social": 0.12, "artes_audiovisuales": 0.10}
        },
        {
          "id": "ARF3_08",
          "pregunta": "¿Qué efecto querés provocar con tu trabajo?",
          "polo_a": "Mover emociones: hacer reír, llorar, sentir",
          "polo_b": "Informar, persuadir o generar cambios de opinión",
          "boosts_polo_a": {"actuacion": 0.12, "musica": 0.10, "letras": 0.08},
          "boosts_polo_b": {"comunicacion_social": 0.12, "relaciones_publicas": 0.10}
        },
        {
          "id": "ARF3_09",
          "pregunta": "¿Qué relación preferís con el mercado?",
          "polo_a": "Crear lo que quiero, sin importar si es comercialmente viable",
          "polo_b": "Adaptarme a lo que el público o el cliente necesita",
          "boosts_polo_a": {"letras": 0.12, "actuacion": 0.10, "musica": 0.08},
          "boosts_polo_b": {"comunicacion_social": 0.10, "relaciones_publicas": 0.10, "gastronomia": 0.08}
        },
        {
          "id": "ARF3_10",
          "pregunta": "¿A qué escala preferís trabajar?",
          "polo_a": "Trabajo artesanal de pequeña escala y proximidad",
          "polo_b": "Medios, productoras y trabajo a gran escala",
          "boosts_polo_a": {"gastronomia": 0.12, "letras": 0.10, "musica": 0.08},
          "boosts_polo_b": {"comunicacion_social": 0.12, "artes_audiovisuales": 0.12}
        }
      ]
    },
    {
      "id": "ar_tecnico",
      "nombre": "Diseño Aplicado & Técnico",
      "descripcion": "Tu perfil combina la creatividad con la precisión técnica o el diseño de objetos, espacios o sistemas.",
      "dims_trigger": ["I", "C"],
      "preguntas": [
        {
          "id": "ARF3_11",
          "pregunta": "¿Qué priorizás en un diseño?",
          "polo_a": "Que resuelva bien el problema funcional",
          "polo_b": "La belleza, la forma y la experiencia estética",
          "boosts_polo_a": {"diseno_ux_ui": 0.12, "diseno_industrial": 0.10, "arquitectura": 0.08},
          "boosts_polo_b": {"artes_visuales": 0.12, "diseno_indumentaria": 0.10}
        },
        {
          "id": "ARF3_12",
          "pregunta": "¿A qué escala preferís diseñar?",
          "polo_a": "A gran escala: edificios, espacios, sistemas",
          "polo_b": "A pequeña escala: objetos, prendas, pantallas",
          "boosts_polo_a": {"arquitectura": 0.16},
          "boosts_polo_b": {"diseno_industrial": 0.12, "diseno_indumentaria": 0.10, "diseno_ux_ui": 0.08}
        },
        {
          "id": "ARF3_13",
          "pregunta": "¿Qué tipo de disciplina preferís?",
          "polo_a": "Con normas técnicas y estándares claros",
          "polo_b": "Con experimentación como parte central del proceso",
          "boosts_polo_a": {"arquitectura": 0.12, "diseno_industrial": 0.10},
          "boosts_polo_b": {"diseno_indumentaria": 0.12, "artes_visuales": 0.10, "gastronomia": 0.08}
        },
        {
          "id": "ARF3_14",
          "pregunta": "¿Qué ciclo de proyecto preferís?",
          "polo_a": "Proyectos de larga duración donde profundizo mucho",
          "polo_b": "Ciclos cortos con iteraciones rápidas y feedback frecuente",
          "boosts_polo_a": {"arquitectura": 0.12, "diseno_industrial": 0.10},
          "boosts_polo_b": {"diseno_ux_ui": 0.12, "diseno_multimedial": 0.10, "creacion_videojuegos": 0.08, "gastronomia": 0.08}
        },
        {
          "id": "ARF3_15",
          "pregunta": "¿Qué relación preferís con la tecnología?",
          "polo_a": "Disciplinas con tradición, oficio y maestría manual",
          "polo_b": "Disciplinas que incorporan tecnología de punta",
          "boosts_polo_a": {"gastronomia": 0.12, "diseno_indumentaria": 0.10, "artes_visuales": 0.08},
          "boosts_polo_b": {"diseno_ux_ui": 0.12, "diseno_multimedial": 0.10, "creacion_videojuegos": 0.10}
        }
      ]
    }
  ],
  "negocios": [
    {
      "id": "ng_emprendimiento",
      "nombre": "Emprendimiento & Comercial",
      "descripcion": "Tu perfil muestra energía para crear, vender y liderar negocios.",
      "dims_trigger": ["E", "S"],
      "preguntas": [
        {
          "id": "NGF3_01",
          "pregunta": "¿Cuál es tu ambición profesional?",
          "polo_a": "Construir algo propio: mi empresa, mi marca, mi negocio",
          "polo_b": "Hacer carrera dentro de organizaciones existentes",
          "boosts_polo_a": {"marketing": 0.10, "negocios_digitales": 0.12, "martillero_publico": 0.08},
          "boosts_polo_b": {"administracion_empresas": 0.12, "recursos_humanos": 0.10, "relaciones_internacionales": 0.08}
        },
        {
          "id": "NGF3_02",
          "pregunta": "¿Cómo te relacionás con el riesgo?",
          "polo_a": "Me atrae: tomar decisiones con información incompleta",
          "polo_b": "Prefiero planificar en entornos estables y predecibles",
          "boosts_polo_a": {"marketing": 0.10, "negocios_digitales": 0.12, "martillero_publico": 0.08},
          "boosts_polo_b": {"administracion_empresas": 0.10, "recursos_humanos": 0.10, "finanzas": 0.08}
        },
        {
          "id": "NGF3_03",
          "pregunta": "¿Qué te energiza más en el trabajo?",
          "polo_a": "Trabajar con personas: convencer, liderar, motivar",
          "polo_b": "Trabajar con datos, modelos y análisis",
          "boosts_polo_a": {"recursos_humanos": 0.12, "relaciones_publicas": 0.10, "relaciones_internacionales": 0.08},
          "boosts_polo_b": {"finanzas": 0.12, "economia": 0.10, "negocios_digitales": 0.08}
        },
        {
          "id": "NGF3_04",
          "pregunta": "¿Cuál es tu horizonte geográfico preferido?",
          "polo_a": "El mercado local y nacional",
          "polo_b": "Lo internacional: otros países, culturas y mercados",
          "boosts_polo_a": {"martillero_publico": 0.12, "administracion_empresas": 0.08},
          "boosts_polo_b": {"relaciones_internacionales": 0.12, "comercio_internacional": 0.12, "lic_turismo": 0.08}
        },
        {
          "id": "NGF3_05",
          "pregunta": "¿Qué horizonte temporal de resultados preferís?",
          "polo_a": "Resultados rápidos y objetivos a corto plazo",
          "polo_b": "Construir estructuras y estrategias de largo plazo",
          "boosts_polo_a": {"marketing": 0.12, "negocios_digitales": 0.10, "martillero_publico": 0.08},
          "boosts_polo_b": {"administracion_empresas": 0.12, "relaciones_internacionales": 0.10, "recursos_humanos": 0.08}
        }
      ]
    },
    {
      "id": "ng_finanzas",
      "nombre": "Análisis & Finanzas",
      "descripcion": "Tu perfil muestra inclinación hacia los números, los mercados y el análisis riguroso de la información.",
      "dims_trigger": ["I", "C"],
      "preguntas": [
        {
          "id": "NGF3_06",
          "pregunta": "¿Qué tipo de trabajo preferís?",
          "polo_a": "Investigar, modelar y analizar para generar insights",
          "polo_b": "Ejecutar, controlar y gestionar procesos concretos",
          "boosts_polo_a": {"economia": 0.12, "finanzas": 0.10, "actuario": 0.10},
          "boosts_polo_b": {"contador_publico": 0.12, "tec_administracion_contable": 0.10, "logistica": 0.08}
        },
        {
          "id": "NGF3_07",
          "pregunta": "¿Qué relación preferís con la incertidumbre numérica?",
          "polo_a": "Me atraen los problemas de riesgo e incertidumbre",
          "polo_b": "Prefiero el control, la precisión y la certeza contable",
          "boosts_polo_a": {"actuario": 0.14, "economia": 0.10, "finanzas": 0.10},
          "boosts_polo_b": {"contador_publico": 0.12, "tec_administracion_contable": 0.10, "escribania": 0.08}
        },
        {
          "id": "NGF3_08",
          "pregunta": "¿En qué sector te imaginás?",
          "polo_a": "El sector público o regulatorio",
          "polo_b": "El sector privado: empresas, consultoras",
          "boosts_polo_a": {"administracion_publica": 0.14, "economia": 0.08},
          "boosts_polo_b": {"finanzas": 0.12, "actuario": 0.10, "contador_publico": 0.08}
        },
        {
          "id": "NGF3_09",
          "pregunta": "¿Cómo preferís trabajar?",
          "polo_a": "Trabajo técnico independiente, con poca interacción",
          "polo_b": "Asesorar clientes y tener relaciones de servicio",
          "boosts_polo_a": {"actuario": 0.12, "economia": 0.10, "finanzas": 0.08},
          "boosts_polo_b": {"contador_publico": 0.12, "escribania": 0.10, "comercio_internacional": 0.08}
        },
        {
          "id": "NGF3_10",
          "pregunta": "¿En qué escala de impacto preferís operar?",
          "polo_a": "Entender y actuar sobre la economía a nivel macro",
          "polo_b": "Generar impacto concreto en empresas o personas",
          "boosts_polo_a": {"economia": 0.14, "administracion_publica": 0.10},
          "boosts_polo_b": {"contador_publico": 0.10, "logistica": 0.10, "finanzas": 0.08, "tec_administracion_contable": 0.08}
        }
      ]
    },
    {
      "id": "ng_servicios",
      "nombre": "Servicios & Gestión",
      "descripcion": "Tu perfil combina el trato con personas y la organización metódica en contextos de servicio.",
      "dims_trigger": ["A", "R"],
      "preguntas": [
        {
          "id": "NGF3_11",
          "pregunta": "¿Qué es lo central de tu trabajo ideal?",
          "polo_a": "La relación con clientes o personas",
          "polo_b": "Gestionar operaciones y procesos internos",
          "boosts_polo_a": {"relaciones_publicas": 0.12, "recursos_humanos": 0.10, "martillero_publico": 0.10, "lic_turismo": 0.08},
          "boosts_polo_b": {"logistica": 0.12, "secretariado_ejecutivo": 0.10, "escribania": 0.08}
        },
        {
          "id": "NGF3_12",
          "pregunta": "¿Qué tipo de entorno preferís?",
          "polo_a": "Donde puedo innovar y proponer cosas nuevas",
          "polo_b": "Organizado con procesos claros y definidos",
          "boosts_polo_a": {"marketing": 0.12, "negocios_digitales": 0.10, "relaciones_publicas": 0.08},
          "boosts_polo_b": {"secretariado_ejecutivo": 0.12, "escribania": 0.10, "logistica": 0.10, "administracion_empresas": 0.08}
        },
        {
          "id": "NGF3_13",
          "pregunta": "¿Cómo preferís ejercer la profesión?",
          "polo_a": "Como profesional autónomo/a con mi propia cartera",
          "polo_b": "Dentro de un equipo u organización",
          "boosts_polo_a": {"martillero_publico": 0.14, "escribania": 0.10},
          "boosts_polo_b": {"recursos_humanos": 0.12, "administracion_empresas": 0.10, "relaciones_publicas": 0.08}
        },
        {
          "id": "NGF3_14",
          "pregunta": "¿Qué tipo de impacto valorás más?",
          "polo_a": "El impacto directo en las personas que atiendo",
          "polo_b": "Mejorar el funcionamiento de organizaciones",
          "boosts_polo_a": {"recursos_humanos": 0.12, "lic_turismo": 0.10, "tec_turismo": 0.08, "relaciones_publicas": 0.08},
          "boosts_polo_b": {"administracion_empresas": 0.12, "logistica": 0.10, "secretariado_ejecutivo": 0.08}
        },
        {
          "id": "NGF3_15",
          "pregunta": "¿Qué alcance geográfico preferís?",
          "polo_a": "Trabajo presencial, cara a cara, en el ámbito local",
          "polo_b": "Gestión global, viajes y entornos internacionales",
          "boosts_polo_a": {"martillero_publico": 0.12, "escribania": 0.10, "secretariado_ejecutivo": 0.08},
          "boosts_polo_b": {"relaciones_internacionales": 0.12, "lic_turismo": 0.10, "comercio_internacional": 0.10}
        }
      ]
    }
  ],
  "humanidades": [
    {
      "id": "hu_social",
      "nombre": "Social & Educación",
      "descripcion": "Tu perfil muestra vocación por acompañar, enseñar y trabajar directamente con personas y comunidades.",
      "dims_trigger": ["S", "E"],
      "preguntas": [
        {
          "id": "HUF3_01",
          "pregunta": "¿Qué escala de cambio te motiva más?",
          "polo_a": "Cambio estructural: políticas, comunidades, sistemas",
          "polo_b": "Cambio individual: acompañar a cada persona",
          "boosts_polo_a": {"trabajo_social": 0.12, "ciencias_educacion": 0.10},
          "boosts_polo_b": {"psicologia": 0.12, "psicopedagogia": 0.10}
        },
        {
          "id": "HUF3_02",
          "pregunta": "¿Qué tipo de vínculo profesional podés sostener?",
          "polo_a": "Vínculos emocionales intensos y situaciones dolorosas",
          "polo_b": "Prefiero cierta distancia profesional con los casos",
          "boosts_polo_a": {"psicologia": 0.12, "trabajo_social": 0.10},
          "boosts_polo_b": {"ciencias_educacion": 0.12, "psicopedagogia": 0.10}
        },
        {
          "id": "HUF3_03",
          "pregunta": "¿Con qué población preferís trabajar?",
          "polo_a": "Personas en situaciones de vulnerabilidad extrema",
          "polo_b": "La población general, sin foco en crisis",
          "boosts_polo_a": {"trabajo_social": 0.12, "psicologia": 0.10},
          "boosts_polo_b": {"ciencias_educacion": 0.12, "profesorado_educacion_primaria": 0.10, "educacion_fisica": 0.08}
        },
        {
          "id": "HUF3_04",
          "pregunta": "¿Cómo preferís ejercer la profesión?",
          "polo_a": "Dentro de instituciones: escuelas, hospitales, ONGs",
          "polo_b": "Consultorio propio o ejercicio independiente",
          "boosts_polo_a": {"trabajo_social": 0.12, "profesorado_educacion_primaria": 0.10, "educacion_fisica": 0.08},
          "boosts_polo_b": {"psicologia": 0.14, "psicopedagogia": 0.10}
        },
        {
          "id": "HUF3_05",
          "pregunta": "¿A través de qué dimensión preferís trabajar?",
          "polo_a": "El cuerpo, el movimiento y lo físico",
          "polo_b": "El lenguaje, el pensamiento y el aprendizaje",
          "boosts_polo_a": {"educacion_fisica": 0.18},
          "boosts_polo_b": {"psicologia": 0.10, "psicopedagogia": 0.10, "ciencias_educacion": 0.08}
        }
      ]
    },
    {
      "id": "hu_investigacion",
      "nombre": "Investigación & Derecho",
      "descripcion": "Tu perfil muestra inclinación hacia el análisis riguroso, el pensamiento crítico o el ejercicio del derecho.",
      "dims_trigger": ["I", "C"],
      "preguntas": [
        {
          "id": "HUF3_06",
          "pregunta": "¿Qué tipo de trabajo intelectual te atrae más?",
          "polo_a": "Convencer, debatir y defender una posición",
          "polo_b": "Analizar, comprender e interpretar sin defender",
          "boosts_polo_a": {"abogacia": 0.14, "ciencia_politica": 0.08},
          "boosts_polo_b": {"historia": 0.12, "sociologia": 0.10, "filosofia": 0.08}
        },
        {
          "id": "HUF3_07",
          "pregunta": "¿Qué dimensión temporal te atrae más estudiar?",
          "polo_a": "El pasado: fuentes históricas y documentos",
          "polo_b": "La coyuntura actual y los procesos en curso",
          "boosts_polo_a": {"historia": 0.16},
          "boosts_polo_b": {"sociologia": 0.10, "ciencia_politica": 0.10, "relaciones_internacionales": 0.08, "comunicacion_social": 0.08}
        },
        {
          "id": "HUF3_08",
          "pregunta": "¿Desde dónde preferís pensar?",
          "polo_a": "Categorías abstractas, conceptos y sistemas teóricos",
          "polo_b": "Casos concretos y problemas reales",
          "boosts_polo_a": {"filosofia": 0.14, "historia": 0.10, "sociologia": 0.08},
          "boosts_polo_b": {"abogacia": 0.12, "ciencia_politica": 0.10, "relaciones_internacionales": 0.08}
        },
        {
          "id": "HUF3_09",
          "pregunta": "¿Cómo se expresa principalmente tu trabajo?",
          "polo_a": "A través de la escritura y el análisis",
          "polo_b": "A través de la intervención y la acción",
          "boosts_polo_a": {"historia": 0.12, "filosofia": 0.10, "letras": 0.10, "sociologia": 0.08},
          "boosts_polo_b": {"abogacia": 0.12, "ciencia_politica": 0.10}
        },
        {
          "id": "HUF3_10",
          "pregunta": "¿Qué modo de trabajo preferís?",
          "polo_a": "Solitario: leer, investigar, escribir",
          "polo_b": "En red: reuniones, negociaciones, institución",
          "boosts_polo_a": {"historia": 0.12, "filosofia": 0.10, "letras": 0.10, "traductorado": 0.08},
          "boosts_polo_b": {"abogacia": 0.12, "ciencia_politica": 0.10, "relaciones_internacionales": 0.10}
        }
      ]
    },
    {
      "id": "hu_derecho",
      "nombre": "Derecho & Gestión Cultural",
      "descripcion": "Tu perfil combina la escritura, el análisis jurídico o la gestión de patrimonio y documentación.",
      "dims_trigger": ["A", "R"],
      "preguntas": [
        {
          "id": "HUF3_11",
          "pregunta": "¿Qué tipo de trabajo jurídico te atrae más?",
          "polo_a": "Juicios, alegatos y defensa de partes",
          "polo_b": "Dar certeza jurídica: documentar, escriturar, certificar",
          "boosts_polo_a": {"abogacia": 0.16},
          "boosts_polo_b": {"escribania": 0.14, "archivologia": 0.10}
        },
        {
          "id": "HUF3_12",
          "pregunta": "¿Qué ritmo de trabajo preferís?",
          "polo_a": "Los conflictos, las urgencias y la presión",
          "polo_b": "El trabajo metódico, archivístico y sin urgencias",
          "boosts_polo_a": {"abogacia": 0.14, "comunicacion_social": 0.08},
          "boosts_polo_b": {"escribania": 0.12, "archivologia": 0.12, "historia": 0.08}
        },
        {
          "id": "HUF3_13",
          "pregunta": "¿Qué impacto te motiva más?",
          "polo_a": "Resolver el problema concreto de una persona o empresa",
          "polo_b": "Preservar, comunicar e interpretar la cultura y la historia",
          "boosts_polo_a": {"abogacia": 0.12, "escribania": 0.10},
          "boosts_polo_b": {"archivologia": 0.12, "historia": 0.10, "ciencias_educacion": 0.08}
        },
        {
          "id": "HUF3_14",
          "pregunta": "¿Cómo preferís comunicarte profesionalmente?",
          "polo_a": "En forma oral: argumentar, presentar, dialogar",
          "polo_b": "En forma escrita: redactar, documentar, analizar",
          "boosts_polo_a": {"abogacia": 0.12, "comunicacion_social": 0.10},
          "boosts_polo_b": {"escribania": 0.12, "archivologia": 0.10, "historia": 0.08, "filosofia": 0.08}
        },
        {
          "id": "HUF3_15",
          "pregunta": "¿En qué sector te imaginás trabajando?",
          "polo_a": "Sector privado o ejercicio independiente",
          "polo_b": "Sector público, cultural u organismos",
          "boosts_polo_a": {"abogacia": 0.12, "escribania": 0.10},
          "boosts_polo_b": {"archivologia": 0.12, "historia": 0.10, "ciencias_educacion": 0.08, "ciencia_politica": 0.08}
        }
      ]
    }
  ]
}

PATH = Path(__file__).parent.parent / "data" / "preguntas.json"
data = json.loads(PATH.read_text(encoding="utf-8"))
data["fase3_por_dominio"] = NUEVA_F3

# Limpiar flag temporal si quedó
for dom_pathways in data["fase3_por_dominio"].values():
    for p in dom_pathways:
        p.pop("_NUEVA_ESTRUCTURA", None)

PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("OK fase3_por_dominio actualizado correctamente")

# Verificación rápida
total_preguntas = sum(
    len(p["preguntas"])
    for dom in data["fase3_por_dominio"].values()
    for p in dom
)
total_pathways = sum(len(v) for v in data["fase3_por_dominio"].values())
print(f"  {total_pathways} pathways, {total_preguntas} preguntas totales")
print(f"  Dominios: {list(data['fase3_por_dominio'].keys())}")
