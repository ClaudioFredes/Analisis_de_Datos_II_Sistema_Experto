# Guión de Presentación — ORIENTAI
## Sistema Experto de Orientación Vocacional · Análisis de Datos II

> **Duración total estimada: ~10 minutos**
> Cada sección incluye el tiempo sugerido. Si algún slide va largo, recortá la última oración.

---

## Slide 00 · Portada
**Presentador: Angel Zambrano** | ⏱ ~0:20

Buenos días / Buenas tardes. Somos el grupo de Análisis de Datos II y hoy les presentamos **ORIENTAI**, un sistema experto de orientación vocacional. Lo desarrollamos como trabajo final de la materia y lo vamos a recorrer en estos diez minutos.

---

## Slide 01 · ¿Qué hace ORIENTAI?
**Presentador: Angel Zambrano** | ⏱ ~1:00

ORIENTAI responde una pregunta muy concreta: **¿qué carrera universitaria debería estudiar?**

Esta pregunta tiene tres características que la hacen ideal para un sistema experto. Primero, es **personalizada**: cada persona tiene un perfil vocacional distinto, no hay una respuesta universal. Segundo, requiere **conocimiento experto**: usamos el modelo RIASEC y la base de datos O*NET del Departamento de Trabajo de Estados Unidos, que clasifica miles de ocupaciones. Y tercero, tiene que ser **explicable**: el usuario no solo recibe una lista de carreras, también entiende por qué cada una le fue recomendada.

El flujo de punta a punta es el que ven abajo: el usuario completa tres fases de preguntas, eso alimenta un motor de reglas que cruza el perfil con noventa carreras, y el resultado son el top cinco de recomendaciones con sus justificaciones y universidades argentinas donde cursarlas.

---

## Slide 02 · Cómo está construido ORIENTAI
**Presentador: Lucía Tomasin** | ⏱ ~0:50

El sistema tiene tres componentes. El **primero** es la base de conocimiento: noventa carreras representadas como vectores RIASEC, organizadas en seis dominios vocacionales. El **segundo** es la elicitación del perfil: tres fases de preguntas que construyen los hechos del usuario —su dominio, su vector RIASEC y sus valores laborales, más el ajuste de boost. El **tercero** es el motor de inferencia: usa la librería **Experta** de Python con encadenamiento hacia adelante. Las reglas evalúan los hechos y producen recomendaciones explicadas en el hecho `Reco`.

El flujo es: las tres fases cargan los hechos → el motor los evalúa contra la base de conocimiento → se obtienen las recomendaciones.

---

## Slide 03 · La base de conocimiento
**Presentador: Lucía Tomasin** | ⏱ ~1:30

La base de conocimiento tiene dos partes que se complementan.

La primera es el **modelo RIASEC**, de John Holland. Define seis tipos de interés vocacional: Realista, Investigador, Artístico, Social, Emprendedor y Convencional. La base O*NET del gobierno americano publica puntajes RIASEC para miles de ocupaciones. Nosotros tomamos esos puntajes y los normalizamos de escala 1–7 a una escala 1–5, lo que nos permite comparar el perfil del usuario con las carreras directamente.

La segunda parte son las **noventa carreras** del catálogo, organizadas en seis dominios: Tecnología, Ciencias Naturales, Salud, Arte y Comunicación, Negocios y Humanidades. Cada carrera tiene un **código Holland de tres letras** —las tres dimensiones con mayor valor—, que es lo que el motor va a comparar contra los intereses del usuario. Al elegir un dominio en la primera fase, el espacio de búsqueda se reduce de noventa a unas quince carreras aproximadamente.

---

## Slide 04 · La arquitectura en tres fases
**Presentador: Ariel Abal** | ⏱ ~0:40

El proceso de elicitación tiene tres fases. La **Fase 1** usa dieciocho preguntas Likert para detectar el dominio vocacional. La **Fase 2** usa diez comparaciones forzadas —las tríadas— para construir el vector RIASEC. Y la **Fase 3** usa cinco preguntas bipolares que refuerzan carreras concretas según los valores del usuario. En total son treinta y tres preguntas.

El sistema rankea y propone, pero la decisión siempre es del usuario: puede elegir un dominio distinto al recomendado.

---

## Slide 05 · Fase 1: Detección del dominio
**Presentador: Ariel Abal** | ⏱ ~1:00

En la primera fase, el usuario evalúa dieciocho actividades en una escala del uno al cinco. Hay tres actividades por dominio. Por ejemplo: *"¿Cuánto te gustaría escribir código para crear una aplicación?"* El sistema promedia las respuestas por dominio y presenta el ranking. El usuario ve cuál es su dominio más afín y lo elige —o elige uno distinto si así lo prefiere.

También elige en esta fase si prefiere **tecnicatura** o **licenciatura**, lo que va a influir más adelante en las reglas expertas.

Este paso reduce el espacio de búsqueda de noventa a aproximadamente quince carreras, que son las que pertenecen al dominio elegido.

---

## Slide 06 · Fase 2: las tríadas
**Presentador: Claudio Fredes** | ⏱ ~1:00

En la segunda fase el usuario hace diez comparaciones forzadas. ¿Por qué no usamos Likert directo? Porque con Likert podés darle cinco sobre cinco a todo sin revelar prioridades reales. La tríada obliga a elegir una sola actividad entre tres, lo que fuerza un ordenamiento genuino de intereses.

Por ejemplo: *"¿Qué actividad preferirías: desarrollar algoritmos de IA, diseñar interfaces de usuario, o administrar servidores en red?"* Si elegís IA, eso suma una victoria a la dimensión **I**, Investigador.

Al final de las diez tríadas, el sistema cuenta cuántas veces elegiste cada dimensión. **Más victorias = interés más alto.** El resultado es tu perfil RIASEC de uno a cinco en cada letra, que es el insumo central del motor.

---

## Slide 07 · Fase 3: Valores laborales
**Presentador: Claudio Fredes** | ⏱ ~1:00

Dos carreras pueden tener el mismo código RIASEC y ser muy distintas en la práctica. La tercera fase captura eso mediante **preguntas bipolares** sobre valores laborales.

Según la dimensión dominante del perfil, el sistema detecta un **pathway** —un sub-perfil— y presenta cinco preguntas calibradas para ese sub-perfil. Por ejemplo, si dominás la dimensión I en Tecnología, tu pathway es *Analítica & Software* y una de las preguntas es: *"¿Preferís trabajar solo con autonomía, o en equipo con comunicación constante?"* Según dónde respondas en esa escala del uno al cinco, el sistema refuerza unas carreras concretas sobre otras.

Hay dieciocho pathways con cinco preguntas cada uno: noventa ajustes finos al ranking final.

---

## Slide 08 · El motor de inferencia
**Presentador: Jorge Rearte** | ⏱ ~1:20

El motor usa **Experta** con encadenamiento hacia adelante: carga los hechos y dispara reglas hasta que no haya más que disparar.

Tiene dos reglas principales. La **regla R1** implementa el matching de Holland: si las letras altas del usuario coinciden con el código de una carrera, genera una recomendación con un puntaje de certeza —tres puntos por la letra dominante, dos por la secundaria, uno por la terciaria. La **regla R3** aplica los ajustes de la Fase 3 sobre ese puntaje.

Las **reglas expertas** agregan el conocimiento humano que el matching puro no tiene. El radar ilustra por qué son necesarias con un caso concreto.

Valentina tiene dos intereses dominantes: le apasiona investigar —dimensión I— y también le importa mucho ayudar a las personas —dimensión S. R1 le asigna certeza 5 tanto a Psicología como a Biología: ambas tienen I y S entre sus letras, ambas le encajan. El motor queda en empate exacto.

Ahí entra **E3**: el sistema detecta que Biología es *I-dominante* —la ciencia y el análisis es lo que la define— y que I es precisamente el interés número uno de Valentina. Le suma +0.5. Ese pequeño ajuste rompe el empate y Biología queda primera.

Si miramos el radar, los dos polígonos son casi idénticos; la diferencia es sutil —uno tiene el pico en S, el otro en I. Eso es exactamente lo que el ojo humano de un orientador vería, y lo que la regla experta codifica.

El ordenamiento final usa certeza más ajustes como criterio primario, y la afinidad continua como desempate.

---

## Slide 09 · Lo que recibe el usuario
**Presentador: Florencia Ardanaz** | ⏱ ~1:00

El resultado final es el top cinco de carreras recomendadas. Cada tarjeta muestra el nombre, el área, el código Holland, la duración y el puntaje de certeza. El símbolo **▲** indica que la Fase 3 o las reglas expertas movieron esa carrera en el ranking.

Al expandir cada tarjeta, el usuario ve dos cosas: **dónde estudiarla** —universidades argentinas donde se dicta— y **por qué fue recomendada** —las reglas concretas que la sostienen, con su contribución al puntaje.

Todo corre localmente en Streamlit. No hay servidor, no hay datos guardados. La explicabilidad es el eje: el sistema no solo recomienda, justifica cada decisión con las reglas que la generaron. Eso es lo que lo hace un **sistema experto** y no un filtro numérico.

Muchas gracias.

---

> **Notas de ritmo**
> - Si van lentos en las fases (slides 05, 06, 07), recorten el último párrafo de cada una.
> - Si van rápido, el motor (slide 08) admite extenderse con más detalle sobre las reglas expertas.
> - El cierre de Florencia puede usarse para abrir preguntas del público si el tiempo lo permite.
