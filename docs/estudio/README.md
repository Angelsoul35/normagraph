# Guía de estudio — NormaGraph

Esta carpeta es una guía en español para entender NormaGraph a fondo. El código,
los comentarios y la documentación técnica están en inglés (nivel B2) a
propósito, para que el proyecto sea creíble y sirva para practicar. Esta guía
explica el "por qué" de cada decisión en tu idioma, para estudiar con calma.

## Orden sugerido de lectura

1. **[01-grafo-de-normas.md](01-grafo-de-normas.md)** — por qué modelamos el
   corpus como un grafo dirigido con tipos, y qué consultas permite.
2. **[02-impacto-e-integridad.md](02-impacto-e-integridad.md)** — el análisis de
   impacto (qué se rompe si cambio una norma) y las comprobaciones de integridad.
3. **[03-recuperacion-y-qa.md](03-recuperacion-y-qa.md)** — la recuperación que usa
   el grafo y la capa de preguntas y respuestas con LLM.
4. **[04-arquitectura-y-diseno.md](04-arquitectura-y-diseno.md)** — cómo encajan
   las piezas y qué decisiones de diseño se tomaron.
5. **[05-preguntas-de-entrevista.md](05-preguntas-de-entrevista.md)** — preguntas
   típicas y cómo responderlas con seguridad.

## Resumen en una frase

NormaGraph modela un corpus de normas como un grafo dirigido con relaciones
tipadas (referencia, modifica, deroga, implementa) y responde lo que un almacén
plano no puede: de qué depende una norma, qué depende de ella, qué se rompería si
cambia, y dónde el corpus es inconsistente — más una recuperación que usa el grafo
y respuestas de un LLM fundamentadas en las normas recuperadas.
