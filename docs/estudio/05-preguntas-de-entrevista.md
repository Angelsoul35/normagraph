# 05 — Preguntas de entrevista

Preguntas típicas sobre este proyecto y cómo responderlas con seguridad.
Practica diciéndolas en voz alta en inglés también.

## Sobre el modelo

**¿Por qué un grafo y no una base de datos de documentos?**
Porque las preguntas que importan en regulación son sobre relaciones entre normas
—de qué depende, qué depende de ella, qué la modifica, qué se derogó— y un almacén
plano no las captura. Con un grafo dirigido con tipos, esas preguntas son
consultas.

**¿Por qué un MultiDiGraph?**
Porque dos normas pueden tener varias relaciones a la vez (p. ej. referenciar y
modificar). Un grafo simple perdería una arista; el multigrafo conserva todas con
su tipo.

**¿Qué tipos de relación modelas?**
`references` (cita), `amends` (modifica), `repeals` (deroga) e `implements`
(implementa). Cada uno dirige consultas distintas.

## Sobre el impacto

**¿Cómo defines "impacto"?**
Como alcanzabilidad inversa por aristas de dependencia: todo lo que depende
transitivamente de una norma vía `references` o `implements`, recorriendo hacia
atrás, con un límite de saltos opcional. Es una definición precisa, no "lo
relacionado".

**¿Por qué amends y repeals no cuentan para el impacto?**
Porque describen lo que una norma hace a otra, no una dependencia permanente de
ella. Solo `references` e `implements` son dependencias reales.

**¿Qué limita la calidad del análisis de impacto?**
Las referencias registradas. Una dependencia que está en el texto pero no se
capturó como arista no aparece. Por eso la extracción del grafo es donde hay que
invertir.

## Sobre integridad

**¿Qué defectos detectas y cómo?**
Referencias colgantes, dependencias de normas derogadas, normas derogadas aún
marcadas vigentes, ciclos de modificación y normas huérfanas. Cada regla es una
consulta sobre el grafo que produce un hallazgo tipado.

**¿Son comprobaciones de fondo legal?**
No: son **estructurales** (sobre el grafo registrado), no de sustancia jurídica.
Eso las hace objetivas y sin falsos positivos. La integridad estructural es la
base necesaria.

## Sobre recuperación y QA

**¿Por qué expandes la recuperación por el grafo?**
Porque en regulación el contexto alrededor de una coincidencia (definiciones,
modificaciones, implementaciones) suele ser lo que el lector necesita. TF-IDF
encuentra la coincidencia; el grafo añade los vecinos. Cada resultado dice si vino
por texto o por grafo.

**¿Qué pasa con la QA si no hay LLM?**
Devuelve el texto de la norma mejor puntuada con su id como cita. Siempre
fundamentada y trazable. Con LLM, escribe una respuesta usando solo las normas
recuperadas y citándolas.

## Sobre el diseño

**¿Por qué este proyecto no usa blockchain?**
Porque su valor es el análisis de grafo de un corpus regulatorio, no un registro
inmutable compartido. Meter una cadena sería artificial. Elijo la herramienta
adecuada.

**¿Qué cubren las pruebas?**
Las consultas de grafo (citas, impacto, cadena, vecinos), las comprobaciones de
integridad (incluidos casos construidos para ciclos y derogada-aún-vigente), la
recuperación expandida, la QA (LLM y fallback), la API y la CLI. Ninguna toca la
red. Cobertura mínima en CI del 80 %.

## Pregunta trampa

**Si subes `expand_hops` a 3, ¿qué pasa?**
La recuperación añade muchos más vecinos, varios con puntuación de texto cero, y
puede diluir la relevancia e inflar el contexto que ve el LLM. Por eso la
expansión es superficial por defecto (un salto): añade el contexto directamente
conectado sin inundar. Es una palanca configurable según el corpus.
