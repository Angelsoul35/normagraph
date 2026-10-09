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

## Validación con una regulación real: el RGPD (GDPR)

El corpus de ejemplo es pequeño y hecho a mano (ideal para pruebas deterministas). La
prueba de fuego es una regulación **real** y muy interconectada: el **RGPD** (Reglamento
UE 2016/679), sus 99 artículos, que se citan entre sí constantemente ("...a que se
refiere el artículo 6", "de conformidad con el artículo 9, apartado 2"). Está vendoreado
en `datasets/gdpr.jsonl` y se construye con `normagraph.real_data.build_gdpr_graph`: cada
artículo es un `Norm`, y cada cita "Article N" en su texto se convierte en una arista
`REFERENCES`.

Con `python -m normagraph.real_benchmark`:

```
artículos (nodos)   : 99
referencias cruzadas: 311   (resolución 100% — toda cita apunta a un artículo real)
conectados / huérfanos: 83 / 16
más citados         : Art. 63 (12), Art. 9 (11), Art. 46 (11), Art. 6 (10)
impacto del Art. 5  : 70 de 99 artículos dependen de él (transitivo)
control (texto barajado): 6 aristas (vs 311 reales)
```

### Por qué esto es la demostración, no un número de exactitud

NormaGraph es **determinista** (construye un grafo y lo consulta; no entrena un modelo),
así que aquí no hay over/underfitting. La pregunta es otra: *¿recupera la estructura
real?* Y la respuesta se comprueba en tres cosas:

1. **Corrección anclada.** El artículo 6(4) cita los artículos **9, 10 y 23** (verificado
   a mano). El test `test_graph_recovers_real_cross_references` lo fija: si el extractor
   se rompe, falla.
2. **Resolución 100%.** Las 311 citas extraídas apuntan a un artículo que existe (1–99);
   ninguna queda colgando. Mide que el parseo es fiel, no inventado.
3. **Consultas con sentido real.** `impact_of("Article 5")` = 70/99: cambiar los
   principios de tratamiento del artículo 5 afecta a casi toda la norma — su "radio de
   explosión". Eso es exactamente lo que un equipo legal necesita saber.

### El control que descarta el azar

Si se **barajan las palabras** de cada artículo, las adyacencias "Article N" se destruyen
y el grafo cae de **311 a 6** aristas. Esto demuestra que las aristas provienen de las
citas reales del texto, no de coincidencias. Es el equivalente, para un motor
determinista, al control de etiquetas barajadas de un clasificador.

## Para fijar la idea

- Un almacén plano no captura relaciones; un grafo sí.
- Nodos = normas (con estado); aristas = relaciones tipadas y dirigidas.
- Toda operación útil es una consulta de grafo: citas, cadena de modificaciones,
  impacto, vecinos.
- "Datos reales" aquí = construir el grafo del **RGPD real** y comprobar que la
  estructura recuperada (citas, impacto, huérfanos) coincide con la regulación, con
  corrección anclada y un control que descarta el azar.
