# WI-5.1: servicio y algoritmo de puntuación de recomendaciones de datasets

- **Issue:** #24 (sub-issue de #5, WI-recommendations / issue #209 original). Código en la planificación: WI209-1.
- **Rama:** `feat/24-algoritmo-recomendaciones`
- **Autores:** Raúl Jiménez Pérez (@RaulJimPer), Rocío Morato Aguilar (@Rma816)
- **Fecha:** 28 de noviembre de 2026

## Objetivo

Permitir que, al consultar un dataset en el hub, el sistema sugiera hasta $N$ datasets publicados relacionados combinando similitud de contenido (**tags** y **autores** compartidos), popularidad (**descargas** registradas en `DSDownloadRecord`) y **recencia** (`created_at`).

Esta primera sub-issue (`#24`) cubre las consultas de repositorio, el algoritmo de puntuación en `DataSetService` y la batería de pruebas con datos sembrados conocidos. La integración visual del bloque *"Related datasets"* en la vista del dataset corresponde a la siguiente sub-issue del `WI-5`.

---

## 1. Fórmula de puntuación

Para un dataset objetivo $d$ y un dataset candidato publicado $c$ ($c \neq d$), la puntuación total se define como:

$$\text{score}(d, c) = W_{\text{tag}} \cdot |\text{tags}(d) \cap \text{tags}(c)| + W_{\text{author}} \cdot |\text{authors}(d) \cap \text{authors}(c)| + W_{\text{download}} \cdot \ln(1 + \text{downloads}(c)) + W_{\text{recency}} \cdot \frac{1}{1 + \text{días}(c) / H}$$

### Pesos y parámetros configurados en `DataSetService`

| Constante | Valor | Descripción |
| --- | --- | --- |
| `RECOMMENDATION_TAG_WEIGHT` ($W_{\text{tag}}$) | `3.0` | Peso por cada etiqueta (`tag`) normalizada en común |
| `RECOMMENDATION_AUTHOR_WEIGHT` ($W_{\text{author}}$) | `2.0` | Peso por cada autor compartido (por nombre normalizado u ORCID) |
| `RECOMMENDATION_DOWNLOAD_WEIGHT` ($W_{\text{download}}$) | `1.0` | Peso aplicado al logaritmo natural de las descargas $\ln(1 + \text{downloads})$ |
| `RECOMMENDATION_RECENCY_WEIGHT` ($W_{\text{recency}}$) | `1.0` | Peso aplicado al factor de recencia en el intervalo $(0, 1]$ |
| `RECOMMENDATION_RECENCY_HALF_LIFE_DAYS` ($H$) | `30.0` | Semivida en días del factor de recencia (a los 30 días aporta `0.5`) |
| `DEFAULT_RECOMMENDATIONS_LIMIT` ($N$) | `5` | Número máximo de datasets recomendados devueltos por defecto |

---

## 2. Decisiones de diseño

1. **Prioridad de la similitud sobre la popularidad y recencia:**
   - Un solo tag compartido (`+3.0`) o un autor compartido (`+2.0`) aporta más peso base que la recencia máxima (`+1.0`).
   - El número de descargas se amortigua con $\ln(1 + \text{downloads})$ (`math.log1p`) para que la popularidad desempate e impulse datasets relevantes sin que un dataset muy descargado pero sin relación temática supere a los que sí comparten tags y autores.
2. **Todos los datasets publicados son candidatos (*fallback* sin coincidencias):**
   - Si un dataset tiene pocos o ningún tag/autor en común con el resto del catálogo, los datasets publicados con $0$ coincidencias siguen siendo candidatos válidos con menor prioridad, ordenándose entre sí por descargas y recencia. De esta forma el bloque de recomendaciones no queda vacío innecesariamente cuando el catálogo tiene datasets publicados.
3. **Filtrado estricto de elegibilidad:**
   - **Solo publicados:** únicamente se consideran datasets con `DSMetaData.dataset_doi IS NOT NULL`. Los borradores locales no sincronizados nunca se recomiendan.
   - **Exclusión del actual:** `DataSet.id != dataset.id` garantiza que un dataset nunca se recomiende a sí mismo.
4. **Normalización de tags y autores:**
   - **Tags:** se separan por comas, se recortan espacios (`strip()`) y se pasan a minúsculas (`lower()`), ignorando entradas vacías.
   - **Autores:** se consideran coincidentes si comparten el mismo nombre normalizado en minúsculas o el mismo identificador `ORCID` no vacío.
5. **Eficiencia en base de datos (sin problema $N+1$):**
   - `DataSetRepository.get_synchronized_excluding(exclude_dataset_id)` obtiene los candidatos publicados en una consulta.
   - `DSDownloadRecordRepository.count_downloads_by_dataset_ids(dataset_ids)` agrupa los conteos con `GROUP BY dataset_id` en una única consulta SQL.
6. **Desempate determinista:**
   - Los candidatos se ordenan por `(score, created_at_timestamp, id)` en orden descendente.

---

## 3. Contrato en `DataSetService`

- `calculate_recommendation_score(target_dataset, candidate_dataset, downloads_count=0, now=None) -> float`: función pura de cálculo del score, desacoplada de la base de datos para facilitar pruebas unitarias deterministas.
- `get_recommendations(dataset, limit=5, now=None) -> list[DataSet]`: devuelve la lista ordenada con como máximo `limit` datasets publicados recomendados para `dataset`.
