# 01 — El grafo de normas

## El problema con un almacén plano

Un corpus de regulación suele guardarse como documentos o una lista de artículos.
Eso responde "¿qué dice el Artículo 7?", pero no responde lo que de verdad
importa: ¿de qué depende este artículo?, ¿qué depende de él?, ¿qué lo modifica?,
¿qué se ha derogado? Esas preguntas son sobre las **relaciones** entre normas, y
una lista plana no las captura.

## La idea: un grafo dirigido con tipos

Modelamos el corpus como un **grafo dirigido con aristas tipadas**:

- **Nodos:** las normas (artículos, decretos, leyes). Cada una tiene un estado:
  `in_force` (vigente), `repealed` (derogada) o `draft` (borrador).
- **Aristas:** una relación dirigida `origen --tipo--> destino`, con tipo
  `references` (cita), `amends` (modifica), `repeals` (deroga) o `implements`
  (implementa).

Se construye con NetworkX, como `MultiDiGraph` (multi: dos normas pueden estar
unidas por más de un tipo de relación a la vez).

Lo interesante está en las **aristas**, no en el texto. Por eso toda operación
útil es una consulta sobre el grafo.

## Las consultas

- **`references_of(norma)`:** qué cita esa norma (aristas salientes de tipo
  `references`).
- **`referenced_by(norma)`:** qué la cita a ella (aristas entrantes de tipo
  `references`).
- **`amendment_chain(norma)`:** sigue hacia delante las aristas `amends`: el
  linaje de modificaciones.
- **`impact_of(norma)`:** la consulta estrella (ver guía 02): todo lo que depende
  de ella, transitivamente.
- **`neighbors(norma, hops)`:** vecinos a cierta distancia, sin mirar dirección ni
  tipo (se usa para expandir la recuperación).

## Un ejemplo del corpus

```
 ART-4 (Consentimiento) --references--> ART-2 (Definiciones)
 ART-4 (Consentimiento) --references--> ART-3 (Base lícita)
 ART-5 (Derechos)       --references--> ART-4
 REG-2019               --implements--> LAW-2018
```

Así, `referenced_by("ART-2")` incluye ART-3, ART-4, ART-7, ART-8 (todos la citan),
y `impact_of("ART-2")` incluye además ART-5, ART-6 y REG-2019 por transitividad.

## ¿Por qué MultiDiGraph?

Porque dos normas pueden tener varias relaciones entre sí (por ejemplo, una norma
podría a la vez referenciar y modificar a otra). Un grafo simple perdería una de
las aristas; el multigrafo las conserva todas, cada una con su tipo.

## Para fijar la idea

- Un almacén plano no captura relaciones; un grafo sí.
- Nodos = normas (con estado); aristas = relaciones tipadas y dirigidas.
- Toda operación útil es una consulta de grafo: citas, cadena de modificaciones,
  impacto, vecinos.
