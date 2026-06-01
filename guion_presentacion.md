# ORIENTAI — Guión de Presentación
**Duración total: 12 minutos · 6 integrantes · ~2 minutos por alumno**

> **Cómo usar este guión:** cada sección es independiente. Estudiá solo la tuya. Los textos son una guía — no los leas textualmente, usalos para entender qué decir y practicá con tus propias palabras. El tiempo es orientativo. La presentación tiene **11 diapositivas** (portada + 10).
>
> **Atajo útil:** durante la presentación, la tecla **N** muestra/oculta las notas del orador de cada slide.

---

## ALUMNO 1 · Slides 1 y 2 · ~2 minutos

### Slide 1 — Portada (40 segundos)

*[Presentarse y presentar al grupo]*

"Buenas tardes. Somos el grupo de Análisis de Datos II — Sistemas Expertos y Redes de Conocimiento, de la Universidad de la Ciudad de Buenos Aires. Hoy les presentamos **ORIENTAI**, un sistema experto de orientación vocacional."

"En 12 minutos les vamos a contar qué hace, cómo evolucionó y qué decisiones técnicas tomamos en el camino."

*[Pasar a la siguiente slide]*

---

### Slide 2 — ¿Qué es ORIENTAI? (80 segundos)

"ORIENTAI es un **sistema experto**: captura el conocimiento de un dominio y lo aplica para asesorar a un usuario. En nuestro caso, ayuda a un joven a encontrar sus áreas de interés y decidir qué carrera seguir."

"Su **base de conocimiento** son 90 carreras, cada una representada como un **vector del modelo RIASEC** —seis dimensiones de interés vocacional— derivados del estándar internacional **O\\*NET** del Departamento de Trabajo de Estados Unidos."

"Algo importante: el sistema **no decide por el usuario**. Detecta su perfil y lo asesora con un Top 5 de carreras afines, con universidades argentinas donde cursarlas."

"El flujo, abajo, es simple: construimos el **perfil del usuario** con 33 preguntas, lo pasamos por un **motor de inferencia**, y devolvemos el **Top 5**. Todo en unos 10 minutos."

*[Pasar a la siguiente slide — turno del Alumno 2]*

---

## ALUMNO 2 · Slides 3 y 4 · ~2 minutos

### Slide 3 — El modelo que adoptamos: RIASEC (50 segundos)

"Para construir el sistema necesitábamos una base teórica. Usamos el modelo **RIASEC** de John Holland: seis dimensiones de interés — Realista, Investigador, Artístico, Social, Emprendedor y Convencional."

"Lo potente es que **O\\*NET** publica puntajes RIASEC para cada ocupación. Así, cada carrera queda representada como un **vector de seis números**. Los reescalamos de la escala 1–7 de O\\*NET a 1–5, **sin redondear** — y ese detalle, como vamos a ver ahora, fue clave."

---

### Slide 4 — El primer intento y lo que salió mal (70 segundos)

"La primera versión era simple: 30 preguntas Likert, un promedio por dimensión y **similitud de coseno** contra el catálogo. Una sola pasada. Tenía **dos fallas de raíz**."

"La primera: **colisiones de vectores**. Al redondear los puntajes a enteros, 16 carreras distintas terminaban con el mismo vector — por ejemplo Medicina y Enfermería, ambas {R:4, I:4, S:5}. Como el desempate era por orden en el archivo, **siempre ganaba la primera de la lista**. Lo llamábamos 'carrera imán'."

"La segunda: **porcentajes distorsionados**. El porcentaje mostrado elevaba el score al cubo, sin justificación matemática. Un score real de 0.90 se mostraba como 73%, hundiendo todos los valores y desordenando el ranking."

*[Pasar a la siguiente slide — turno del Alumno 3]*

---

## ALUMNO 3 · Slides 5 y 6 · ~2 minutos

### Slide 5 — Tres cambios que lo transformaron (55 segundos)

"Identificados los problemas, hicimos tres cambios."

"**Primero: vectores float en lugar de enteros.** No redondear eliminó las 16 colisiones de un saque — pasamos a cero."

"**Segundo: tres fases en lugar de una sola pasada.** La Fase 1 rankea los seis dominios vocacionales, y acá es importante: **el sistema propone, pero el usuario elige** sobre cuál profundizar. Eso reduce el espacio de búsqueda de 90 carreras a unas 15."

"**Tercero: tríadas en lugar de solo Likert.** En vez de '¿cuánto te gusta programar?', preguntamos '¿entre IA, UX y redes, cuál elegís?'. **Comparar es más discriminativo que evaluar** en absoluto. Pasamos de 50 preguntas genéricas a 33 estructuradas."

---

### Slide 6 — La arquitectura en tres fases (65 segundos)

"Esta es la arquitectura final. Acá ven el flujo completo."

"La **Fase 1** son 18 preguntas Likert que detectan el dominio. Después, el usuario **elige** el dominio que más le interesa y su preferencia de duración — tecnicatura o licenciatura."

"La **Fase 2** son 10 tríadas que construyen el vector RIASEC. El sistema muestra ese perfil como un radar y detecta el **sub-perfil** o pathway dentro del dominio."

"La **Fase 3** son 5 preguntas de valores laborales. Y al final, el Top 5 con universidades."

"El mensaje clave es el del centro: **el sistema rankea y propone, pero la decisión final es del usuario. Asesora, no reemplaza.**"

*[Pasar a la siguiente slide — turno del Alumno 4]*

---

## ALUMNO 4 · Slides 7 y 8 · ~2 minutos

### Slide 7 — Caso en vivo: Martina (55 segundos)

"Para que se entienda, sigamos a una usuaria: **Martina, 17 años**."

"En la Fase 1 elige **Tecnología**. Sus 10 tríadas construyen su perfil RIASEC — un vector con **Investigador dominante**. El sistema detecta el pathway **Analítica & Software**."

"En el radar ven por qué funciona: el perfil de Martina (en azul) **se superpone con el de Ciencia de Datos** (en verde) — los dos tienen el pico en la I. Por eso hay match."

"En la Fase 3 prioriza **autonomía y trabajar con datos**, y ese boost sube **Ciencia de Datos al puesto #1, con 84%**, por encima de Ingeniería en Sistemas. Pero, ¿cómo decide el motor ese ranking? Eso lo explica la siguiente slide."

---

### Slide 8 — El motor de inferencia (65 segundos)

"El motor compara el vector del usuario con cada carrera. La métrica obvia —el coseno— tiene una **trampa**: sobre vectores 1 a 5, que son siempre positivos, da entre 0.7 y 1.0 para **casi cualquier par**. Es decir, **infla la afinidad** y premia coincidencias en una dimensión secundaria."

"El caso que nos lo mostró: el perfil de una **Instrumentadora Quirúrgica** —alto en R y C— sacaba coseno altísimo con el **Martillero Público**, solo porque comparten la C, aunque no comparten la R."

"La solución es **Pearson**: centra cada vector por su media y compara la **forma** del perfil — el código Holland dominante. Miren los números: para ese par, el **coseno da 0.87 y los confunde**, pero el **Pearson da 0.10 y los separa**. Por eso el score final pesa **30% coseno y 70% Pearson**."

*[Pasar a la siguiente slide — turno del Alumno 5]*

---

## ALUMNO 5 · Slides 9 y 10 · ~2 minutos

### Slide 9 — ¿Cómo sabemos que funciona? (60 segundos)

"El sistema fue **validado con rigor**, no solo implementado."

"Por un lado, **15 tests automatizados** que se corren con un comando: verifican perfiles arquetípicos, que coseno y Pearson sean métricas distintas, que no haya colisiones, las tríadas y los casos extremos."

"Por otro, una **simulación Monte Carlo**: 500 perfiles sintéticos por 3 escenarios. De ahí salió la calibración 0.3 / 0.7, y **confirmó el fix a escala**: los falsos positivos comerciales —como el Martillero que acabamos de ver— cayeron de **16% a 6%**, y la cobertura subió de **67 a 69** carreras distintas en el Top-1."

---

### Slide 10 — Lo que recibe el usuario (60 segundos)

"Esto es lo que ve Martina al terminar — el caso que seguimos."

"Cada tarjeta muestra la posición, el nombre, el área, el **código Holland** —las tres letras dominantes—, la duración y el **porcentaje de afinidad**. El símbolo ✦ marca que la Fase 3 modificó el orden: acá subió Ciencia de Datos al #1."

"Al expandir cada tarjeta aparecen las **universidades argentinas** donde se cursa, un **radar comparativo** y los datos del motor. El porcentaje no es inventado: es el score matemático multiplicado por 100."

"Y todo corre **sin servidor y sin guardar datos**: al cerrar la pestaña, no queda nada."

*[Opcional, si hay tiempo: demo en vivo en `localhost:8501`. Pasar al Alumno 6.]*

---

## ALUMNO 6 · Slide 11 · ~2 minutos

### Slide 11 — Aprendizajes y próximos pasos (2 minutos)

"Para cerrar, **cuatro aprendizajes** que se llevan más allá de este sistema."

"**Primero: estructura más que cantidad.** 33 preguntas bien pensadas superan a 50 genéricas. Más datos del mismo tipo no arreglan un problema de arquitectura."

"**Segundo: comparar más que evaluar.** Las tríadas le dan al usuario una tarea más natural —elegir entre opciones— y producen datos más discriminativos que poner un número en absoluto."

"**Tercero: validar con datos reales.** La simulación Monte Carlo detectó el falso positivo del Martillero, algo que el testing manual no veía."

"**Cuarto, y el que más nos marcó: lo que creés que hace tu código no siempre es lo que corre.** Descubrimos que decíamos usar 'coseno' pero, al centrar los vectores, en realidad calculábamos solo Pearson — una métrica disfrazada de otra. Auditar el código fue tan importante como escribirlo."

"Como **trabajo futuro** nos queda el **editor de conocimiento**: una interfaz para agregar carreras, ajustar pesos y simular perfiles sin tocar código. Eso es lo que distingue a un sistema experto mantenible de uno estático."

"Muchas gracias. Quedamos a disposición para preguntas."

---

## Resumen de tiempos

| Alumno | Slides | Tema | Tiempo |
|--------|--------|------|--------|
| Alumno 1 | 1 y 2 | Portada · ¿Qué es ORIENTAI? | ~2 min |
| Alumno 2 | 3 y 4 | RIASEC · El primer intento y lo que salió mal | ~2 min |
| Alumno 3 | 5 y 6 | Tres cambios · Arquitectura en tres fases | ~2 min |
| Alumno 4 | 7 y 8 | Caso Martina · El motor de inferencia | ~2 min |
| Alumno 5 | 9 y 10 | Validación · Lo que recibe el usuario | ~2 min |
| Alumno 6 | 11 | Aprendizajes y próximos pasos | ~2 min |
| **Total** | **11 slides** | | **~12 min** |

---

## Consejos para la presentación

- **No leer el guión.** Usalo para estudiar los conceptos; después presentá con tus palabras.
- **Antes de pasar de slide**, mirá al público y hacé una pequeña pausa.
- **Hilo narrativo**: la presentación cuenta una historia — qué es → el modelo → el primer intento que falló → los tres cambios → cómo funciona → un caso concreto (Martina) → por qué el motor es inteligente → la prueba → el resultado → los aprendizajes. Cada uno toma la posta donde la dejó el anterior.
- **Conexión clave entre slides 7 y 8**: la slide 7 muestra un *acierto* (el perfil de Martina hace match con Ciencia de Datos) y la 8 muestra el *error histórico* que corrigió Pearson (Instrumentadora vs Martillero). Son las dos caras de la misma decisión.
- **Si el docente pregunta**: responde primero el alumno que presentó ese tema.
- **Demo en vivo** (opcional, Alumno 5): si hay tiempo, mostrar el sistema en `localhost:8501`. Filtrar por dominio Tecnología y responder un perfil I-alto.
- **Tiempo**: practicá cada sección con cronómetro. 2 minutos es más corto de lo que parece.
