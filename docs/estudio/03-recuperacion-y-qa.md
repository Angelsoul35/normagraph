# 03 — Recuperación y preguntas/respuestas

## Recuperación que usa el grafo

Para responder una pregunta sobre la regulación, primero hay que **encontrar** las
normas relevantes. La recuperación de texto simple (TF-IDF) encuentra normas cuyas
palabras coinciden con la consulta. Pero en un corpus regulatorio, la norma que
coincide casi nunca basta: un artículo sobre consentimiento no significa nada sin
las definiciones de las que depende, y un artículo puede haber sido modificado por
otro que comparte pocas palabras con la consulta.

Por eso recuperamos en **dos pasos**:

1. **Coincidencia de texto:** TF-IDF + similitud coseno sobre el título y el texto
   de cada norma → los `top_k` mejores.
2. **Expansión por el grafo:** por cada coincidencia, se añaden sus vecinos (hasta
   `hops` saltos) — lo que referencia, lo que la referencia, etc.

Cada norma devuelta se etiqueta con cómo llegó: `match` (coincidencia de texto) o
`graph` (vecino). Así se ve por qué está cada una.

### Por qué expandir

Porque los vecinos suelen ser justo lo que el lector necesita: las definiciones,
las modificaciones, la regulación que implementa. La expansión es **superficial**
(un salto por defecto) para añadir el contexto directamente conectado sin inundar
el resultado. El número de saltos es configurable.

## La capa de preguntas y respuestas (QA)

`RegulationQA` junta la recuperación (con expansión) y construye un bloque de
contexto con el texto de esas normas. Luego pide al LLM que responda usando
**solo** ese contexto y que **cite** los ids de las normas en las que se apoya.

El LLM es el cliente agnóstico del proveedor con cascada (Anthropic, OpenAI,
Gemini, DeepSeek, Ollama). Si está disponible, escribe una respuesta fundamentada
y con citas (`source = "llm"`).

### El respaldo (fallback)

Si el LLM no está disponible (sin claves, cascada agotada), se devuelve el texto de
la **norma mejor puntuada** con su id como cita (`source = "retrieval"`). Es una
respuesta siempre **fundamentada y trazable**, aunque menos pulida.

Así, la QA funciona sin conexión (así corren la demo y las pruebas) y mejora sola
en cuanto hay una clave de API.

## Para fijar la idea

- Recuperación en dos pasos: coincidencia de texto + expansión por el grafo.
- Cada resultado dice si vino por `match` o por `graph`.
- La QA responde con el LLM usando solo las normas recuperadas y citándolas; sin
  LLM, devuelve la mejor norma con su id. Siempre fundamentada.
