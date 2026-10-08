# 02 — Análisis de impacto e integridad

## El análisis de impacto: ¿qué se rompe si cambio esto?

La pregunta más valiosa en un grafo de normas es: *si cambio (o derogo) esta
norma, ¿qué más se ve afectado?* Necesitábamos una definición **precisa** de
"afectado", no una vaga de "relacionado".

No toda arista es una dependencia:

- Si A **referencia** a B, A depende de B → A se ve afectado si B cambia. Igual con
  **implements**.
- **amends** y **repeals** describen lo que una norma **hace** a otra, no una
  dependencia permanente de ella.

### La definición

**Impacto** = todo lo alcanzable recorriendo las aristas de dependencia
(`references`, `implements`) **hacia atrás** desde la norma objetivo.

Es decir: empieza en la norma, sigue las aristas entrantes de referencia/implementa
hacia las normas que dependen de ella, y repite desde cada una, transitivamente.
Es una **alcanzabilidad inversa** (reverse reachability), con una búsqueda en
anchura (BFS) y un límite opcional de saltos.

### Ejemplo

`impact_of("ART-2")` (Definiciones) devuelve ART-3, ART-4, ART-5, ART-6, ART-7,
ART-8 y REG-2019: cambiar las definiciones afecta a casi todo el corpus. Con
`max_hops=1`, solo los dependientes directos: ART-3, ART-4, ART-7, ART-8.

El impacto es tan completo como las referencias registradas: una dependencia que
está en el texto pero no se capturó como arista no aparecerá. Por eso la calidad
del grafo extraído es donde hay que poner el esfuerzo.

## Las comprobaciones de integridad

Un corpus se vuelve inconsistente con el tiempo. Cada regla de consistencia es una
**consulta sobre el grafo** y produce hallazgos tipados:

- **dangling_reference:** una arista cuyo destino no existe en el corpus (p. ej.
  DECREE-5 referencia MISSING-9).
- **depends_on_repealed:** una norma vigente que referencia/implementa una norma
  derogada (p. ej. ART-6 → ART-8-OLD).
- **repealed_still_in_force:** una norma a la que apunta una arista `repeals` pero
  que sigue marcada como vigente (una incoherencia de estado).
- **amendment_cycle:** un ciclo en el subgrafo de `amends` (se detecta con
  NetworkX `simple_cycles`).
- **orphan:** una norma con grado cero, sin ninguna relación (p. ej. NOTE-1).

Cada hallazgo lleva su tipo (`kind`), la norma implicada y un detalle legible.

### Por qué son estructurales

Estas comprobaciones encuentran inconsistencias **estructurales** (en el grafo
registrado), no errores de **fondo legal** (una referencia que existe pero apunta a
la norma equivocada en sentido jurídico). La integridad estructural es la base
necesaria, y mantener las comprobaciones puramente estructurales las hace
objetivas y sin falsos positivos.

El corpus de ejemplo incluye tres defectos a propósito (dangling, depends_on_repealed
y orphan) para que la comprobación tenga algo que encontrar en la demo.

## Para fijar la idea

- Impacto = alcanzabilidad inversa por aristas de dependencia (references,
  implements). Definición precisa, no "relacionado".
- Solo cuentan las aristas que son dependencias reales; amends/repeals alimentan
  otras consultas.
- Integridad = un conjunto de consultas de grafo que sacan a la luz defectos
  estructurales, cada uno como un hallazgo tipado.
