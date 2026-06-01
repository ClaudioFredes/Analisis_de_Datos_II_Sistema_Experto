# ORIENTAI — Guión de Presentación
**Duración total: 12 minutos · 6 integrantes · 2 minutos por alumno**

> **Cómo usar este guión:** cada sección es independiente. Estudiá solo la tuya. Los textos son una guía — no los leas textualmente, usalos para entender qué decir y practicá con tus propias palabras. El tiempo indicado es orientativo.

---

## ALUMNO 1 · Slides 1 y 2 · ~2 minutos

### Slide 1 — Portada (30 segundos)

*[Presentarse y presentar al grupo]*

"Buenas tardes. Somos el grupo [X] de Análisis de Datos II. Hoy les presentamos ORIENTAI, un sistema experto de orientación vocacional que desarrollamos para ayudar a jóvenes de entre 17 y 20 años a elegir una carrera."

"En 12 minutos les vamos a contar cómo funciona, cómo evolucionó, y qué decisiones técnicas tomamos en el camino."

*[Pasar a la siguiente slide]*

---

### Slide 2 — ¿Qué es un Sistema Experto? (90 segundos)

"Un sistema experto es un programa que captura el conocimiento de un especialista y lo aplica automáticamente para resolver un problema. Tiene tres componentes."

"La **base de conocimiento** contiene los hechos del dominio. En nuestro caso: 90 carreras con sus perfiles vocacionales tomados del estándar internacional O\*NET, organizadas en 6 dominios y 18 sub-perfiles."

"El **motor de inferencia** aplica ese conocimiento a los datos del usuario. Usamos una combinación de dos métricas matemáticas, que vamos a ver en detalle más adelante."

"La **interfaz de usuario** es el quiz adaptativo en Streamlit, con radar chart y tarjetas de resultado."

"Abajo ven las 6 dimensiones del modelo RIASEC de Holland, que es el estándar psicométrico que usamos: Realista, Investigador, Artístico, Social, Emprendedor y Convencional."

*[Pasar a la siguiente slide — es el turno del Alumno 2]*

---

## ALUMNO 2 · Slide 3 · ~2 minutos

### Slide 3 — Evolución del sistema (2 minutos)

"Cuando empezamos, el sistema era mucho más simple. Y tuvimos que iterarlo varias veces para llegar a lo que ven hoy."

"La primera versión tenía 30 preguntas Likert — el usuario respondía del 1 al 5 cuánto le gustaba cada actividad. El problema fue que los valores O\*NET se redondeaban a enteros, lo que hacía que 16 carreras distintas tuvieran exactamente el mismo vector matemático. Resultado: siempre ganaba la primera en el archivo. A esas las llamamos 'carreras imán'."

"Aumentamos a 50 preguntas pensando que más datos iban a ayudar. Pero el problema no era la cantidad — era la estructura. Con más preguntas del mismo tipo seguíamos obteniendo resultados genéricos."

"El giro fue separar el sistema en fases. Primero: detectar en cuál de 6 grandes mundos está el usuario. Eso redujo el espacio de búsqueda de 90 carreras a unas 15 del dominio elegido."

"Después reemplazamos las preguntas Likert por tríadas — el usuario elige una de tres actividades. Comparar es más discriminativo que evaluar en absoluto."

"Y finalmente agregamos una capa de valores: preguntas bipolares sobre contexto laboral, no sobre actividades."

"Como ven acá: pasamos de 50 preguntas con resultados vagos a 33 preguntas bien estructuradas."

*[Pasar a la siguiente slide — turno del Alumno 3]*

---

## ALUMNO 3 · Slides 4 y 5 · ~2 minutos

### Slide 4 — Arquitectura (60 segundos)

"Acá ven el flujo completo del sistema."

"El usuario arranca con la Fase 1: 18 preguntas que detectan el dominio. Luego elige el dominio que más le interesa y su preferencia de duración de carrera."

"La Fase 2 son 10 tríadas donde elige 1 de 3 actividades. Con eso construimos el vector RIASEC del usuario. El sistema muestra ese perfil como un radar y detecta el sub-perfil dentro del dominio."

"La Fase 3 son 5 preguntas bipolares sobre valores laborales. Y al final el usuario recibe el Top 5 de carreras con todas las carrera."

"El catálogo tiene 90 carreras, 6 dominios y 18 sub-perfiles."

---

### Slide 5 — Base de conocimiento: O\*NET + RIASEC (60 segundos)

"Ahora explico de dónde salen los datos de cada carrera."

"O\*NET es el estándar del Departamento de Trabajo de Estados Unidos. Cada ocupación tiene un código SOC y puntajes de interés vocacional en escala 1 a 7."

"Nosotros los reescalamos a escala 1 a 5 usando esta fórmula. Lo crítico es que lo hacemos **sin redondear** — mantenemos el valor como número decimal. Eso fue el fix de la primera iteración: con enteros teníamos 16 colisiones, con float tenemos cero."

"En la tabla ven tres ejemplos reales. Ingeniería en Sistemas tiene I alto, Psicología tiene S alto, Diseño Gráfico tiene un perfil más distribuido."

"Cada carrera incluye además el área, la duración, etiquetas de perfil y las universidades argentinas donde se dicta."

*[Pasar a la siguiente slide — turno del Alumno 4]*

---

## ALUMNO 4 · Slides 6 y 7 · ~2 minutos

### Slide 6 — Motor de inferencia (60 segundos)

"El corazón del sistema es el scoring híbrido. Usamos dos métricas porque cada una captura una señal distinta."

"La similitud de coseno mide la alineación direccional: si el usuario y la carrera 'apuntan' al mismo lado en el espacio RIASEC."

"La correlación de Pearson mide la forma del perfil — los picos y valles relativos — independientemente de si el usuario tiende a responder alto o bajo en general."

"El score final es 30% coseno y 70% Pearson. Ese peso lo calibramos con una simulación Monte Carlo de 500 perfiles."

"¿Por qué hace falta el Pearson? Porque el coseno solo cometía errores. Un perfil de Instrumentadora Quirúrgica — alto en R y C — recibía Martillero Público en el Top-3, porque ambos comparten la dimensión C. Pearson lo corrige porque compara si C es dominante en ambos, no si aparece en alguno."

---

### Slide 7 — Las tres fases (60 segundos)

"Las tres fases capturan señales diferentes e independientes."

"La Fase 1 detecta el mundo vocacional. Es rápida: 18 preguntas, atajos de teclado del 1 al 5."

"La Fase 2 construye el vector RIASEC por comparación forzada. No pregunta '¿cuánto te gusta desarrollar IA?' sino '¿entre desarrollar IA, diseñar interfaces o armar redes, cuál elegís?' Esa diferencia hace que el resultado sea mucho más informativo."

"La Fase 3 agrega la capa de valores. Dos carreras pueden tener el mismo perfil RIASEC pero diferir completamente en contexto laboral: una implica autonomía, la otra trabajo en equipo. Esto lo captura la escala bipolar."

"La tarjeta de resumen abajo lo dice todo: F1 detecta el dominio, F2 el vector RIASEC, F3 los valores y el contexto. Tres señales complementarias."

*[Pasar a la siguiente slide — turno del Alumno 5]*

---

## ALUMNO 5 · Slides 8 y 9 · ~2 minutos

### Slide 8 — Resultado (60 segundos)

"Esto es lo que ve el usuario al terminar las tres fases."

"Cada tarjeta muestra el número de ranking, el nombre de la carrera, el área, el código Holland — que son las tres letras dominantes del perfil RIASEC — y el porcentaje de afinidad."

"Al hacer clic en la tarjeta, se expande y muestra: las universidades argentinas donde se puede cursar esa carrera — con el nombre de la institución y la ciudad —, un radar comparativo entre el perfil del usuario y el perfil de la carrera, y detalles técnicos del motor."

"Lo importante del porcentaje: no es inventado, es el score matemático del motor multiplicado por 100. El orden y el número siempre son consistentes."

"Y todo esto corre sin servidor, sin guardar datos. Al cerrar la pestaña del navegador, todo desaparece."

---

### Slide 9 — Validación (60 segundos)

"Queremos mostrar que el sistema fue desarrollado con rigor, no solo implementado."

"Tenemos 15 tests automatizados que se corren con un solo comando. Cubren: perfiles arquetípicos — que un perfil Social llegue a carreras de salud o educación —, el motor híbrido — que coseno y Pearson sean realmente métricas distintas, que no haya carreras con vectores idénticos —, los algoritmos de tríadas, y casos extremos."

"La simulación Monte Carlo corrió 500 perfiles sintéticos en tres escenarios distintos. Fue lo que nos permitió calibrar el peso del coseno en 0.3 y verificar que el sistema distribuye bien las recomendaciones entre el catálogo."

"El caso concreto que más nos costó resolver: el perfil de Instrumentadora Quirúrgica. R y C alto, S medio. El motor anterior devolvía Martillero Público. El motor actual devuelve Instrumentación como número uno, con Salud dominando el Top 5."

*[Pasar a la siguiente slide — turno del Alumno 6]*

---

## ALUMNO 6 · Slide 10 · ~2 minutos

### Slide 10 — Conclusiones (2 minutos)

"Para cerrar, tres aprendizajes que se llevan más allá de este sistema."

"Primero: **estructura es más importante que cantidad**. 50 preguntas genéricas nos dieron peores resultados que 33 bien pensadas en tres fases. Más datos del mismo tipo no resuelven un problema de arquitectura."

"Segundo: **comparar es más rico que evaluar**. Las tríadas pairwise le dan al usuario una tarea cognitivamente más fácil — elegir entre tres opciones — y producen datos más discriminativos que responder cuánto le gusta algo en absoluto."

"Tercero: **la validación automatizada encuentra lo que el testing manual no ve**. El caso de la Instrumentadora y el Martillero Público nunca lo hubiéramos encontrado sin correr el sistema sobre cientos de perfiles sintéticos."

"En cuanto al estado actual: tenemos 90 carreras con vectores float de O\*NET, tres fases diferenciadas, motor calibrado, 18 pathways, universidades argentinas reales y 15 tests pasando."

"Como trabajo futuro nos quedó pendiente el editor de conocimiento: una interfaz para agregar carreras, modificar pesos, simular perfiles y ver el impacto antes de publicar cualquier cambio. Eso es lo que distingue a un sistema experto mantenible de uno estático."

"Muchas gracias. Quedamos a disposición para preguntas."

---

## Resumen de tiempos

| Alumno | Slides | Tiempo |
|--------|--------|--------|
| Alumno 1 | 1 y 2 | ~2 min |
| Alumno 2 | 3     | ~2 min |
| Alumno 3 | 4 y 5 | ~2 min |
| Alumno 4 | 6 y 7 | ~2 min |
| Alumno 5 | 8 y 9 | ~2 min |
| Alumno 6 | 10    | ~2 min |
| **Total** |      | **~12 min** |

---

## Consejos para la presentación

- **No leer el guión**. Usalo para estudiar los conceptos, después presentá con tus palabras.
- **Antes de pasar de slide**, mirá al público y hacé una pequeña pausa.
- **Si te pregunta algo el docente**: el Alumno que presentó ese tema responde primero.
- **Demo en vivo** (opcional, Alumno 5): si hay tiempo, mostrar el sistema corriendo en `localhost:8501`. Filtrar por dominio Tecnología, responder un perfil I alto.
- **Tiempo**: practicá cada sección con cronómetro. 2 minutos es más corto de lo que parece.
