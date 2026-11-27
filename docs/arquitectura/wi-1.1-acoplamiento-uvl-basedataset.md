# WI-1.1: acoplamiento a UVL y diseño de `BaseDataset`

- **Issue:** #8 (sub-issue de #1, WI-newdataset). Código en la planificación: WI178-1.
- **Rama:** `feat/8-arquitectura-basedataset`
- **Autor:** Pedro José Payán Aguilera (@ThePayan)
- **Fecha:** 26 de noviembre de 2026

## Objetivo

uvlhub da por hecho que todo dataset es un conjunto de modelos de características en UVL. Para convertirlo en Esports-hub, cuyos datasets son partidas de Valorant en CSV (DEC-001 del diario del equipo), sin romper lo que ya funciona, esta issue hace dos cosas:

1. Deja por escrito **dónde está atado el código a UVL** y qué parte es común a cualquier dataset.
2. Introduce la clase **`BaseDataset`** con lo común, de la que hereda **`UVLDataset`**, sin cambiar el esquema de la base de datos ni el comportamiento.

El resto del WI-1 se reparte en las issues #9 a #13. Este documento indica a cuál le toca cada punto acoplado, para que nadie lo haga dos veces.

## 1. Inventario de puntos acoplados a UVL

Leyenda de la columna **Tipo**: *común* = sirve para cualquier dataset; *UVL* = solo tiene sentido para modelos de características; *mixto* = mezcla las dos cosas y habrá que separarlas.

### Modelo de datos

| Dónde | Qué hay | Tipo | Quién lo trata |
| --- | --- | --- | --- |
| `dataset/models.py` · `DSMetaData` | Título, descripción, tipo de publicación, DOI de publicación y del dataset, `deposition_id`, tags y autores | común | Se queda como está (lo usa `BaseDataset`) |
| `dataset/models.py` · `Author` | Autores. Tiene dos claves ajenas: `ds_meta_data_id` (común) y `fm_meta_data_id` (UVL) | mixto | #10 si hace falta autoría por fichero CSV |
| `dataset/models.py` · `DSMetrics` | `number_of_models` y `number_of_features`, enlazado desde `DSMetaData.ds_metrics_id` | UVL | #9 define las métricas de Valorant (partidas, jugadores, eventos…); #10 decide en la migración si se generalizan |
| `dataset/models.py` · `DataSet` | Propietario, fecha, metadatos y la relación `feature_models` | mixto | **#8 (esta issue): separado en `BaseDataset` + `UVLDataset`** |
| `dataset/models.py` · `DSDownloadRecord`, `DSViewRecord`, `DOIMapping` | Descargas, visitas y redirección de DOI, con clave ajena a `data_set.id` | común | Sin cambios |
| `featuremodel/models.py` · `FeatureModel`, `FMMetaData`, `FMMetrics` | Un modelo UVL dentro del dataset, con `uvl_filename`, `uvl_version` y métricas del solver | UVL | Sin cambios: pertenece a `UVLDataset` |
| `hubfile/models.py` · `Hubfile` | Fichero subido. Su clave ajena obligatoria es `feature_model_id`: un fichero solo puede colgar de un modelo UVL | mixto | #9/#10: el CSV necesita colgar sus ficheros de su propio tipo |
| `auth/models.py` · `User.data_sets` | Relación con los datasets del usuario | común | **#8: apunta ahora a `UVLDataset`**; #10 la pasa a `BaseDataset` cuando sea polimórfica |

### Servicios y repositorios

| Dónde | Qué hay | Tipo | Quién lo trata |
| --- | --- | --- | --- |
| `dataset/services.py` · `save_temp_uvl` | Solo acepta ficheros que terminen en `.uvl` | UVL | #11 |
| `dataset/services.py` · `create_from_form` | Crea `FMMetaData`, `FeatureModel` y `Hubfile` por cada fichero del formulario | mixto | #11 |
| `dataset/services.py` · `move_feature_models` | Mueve los ficheros a `uploads/` usando `fm_meta_data.uvl_filename` | UVL | #11/#13 |
| `dataset/services.py` · `upload_dataset` | Sube a Zenodo un fichero por `FeatureModel` | mixto | #13 |
| `dataset/services.py` · `build_download_archive` | Comprime la carpeta `uploads/user_X/dataset_Y` | común | Sin cambios (#13 lo comprueba con CSV) |
| `dataset/services.py` · `get_uvlhub_doi` | URL del DOI dentro del hub. El nombre dice "uvlhub" pero la lógica es común | común | Renombrarlo tocaría plantillas de cuatro features: se deja |
| `explore/repositories.py` · `filter` | Busca por `FMMetaData.uvl_filename` y hace `join` obligatorio con `feature_models`: un dataset sin modelos UVL no aparecería nunca | mixto | #12 |
| `hubfile/repositories.py` | Llega al dataset y al usuario a través de `FeatureModel` | mixto | #9/#10 |
| `zenodo/services.py` · `upload_file` | Recibe un `FeatureModel` y usa `uvl_filename` | UVL | #13 |
| `zenodo/services.py` · `create_new_deposition` | Añade siempre la palabra clave `uvlhub` | mixto | #13 |
| `featuremodel/services.py`, `public/routes.py` | Contadores de modelos, vistas y descargas de feature models en la portada | UVL | #12 si se quiere un contador por tipo |
| `flamapy/` (feature completa) | Validación sintáctica, SAT y exportación a Glencoe, CNF y SPLOT | UVL | Sin cambios: solo aplica a `UVLDataset` |

### Formularios, plantillas y JavaScript

| Dónde | Qué hay | Tipo | Quién lo trata |
| --- | --- | --- | --- |
| `dataset/forms.py` · `FeatureModelForm` | Campos `uvl_filename` y `uvl_version` | UVL | #11 |
| `dataset/forms.py` · `DataSetForm` | Metadatos comunes y una lista de `feature_models` | mixto | #11 |
| `dataset/templates/dataset/upload_dataset.html` | Dropzone con `acceptedFiles: '.uvl'`, comprobación de extensión y formulario por modelo UVL | UVL | #11 |
| `dataset/assets/js/scripts.js` | Botón `add_author_to_uvl` y prefijo `feature_models-` | UVL | #11 |
| `dataset/templates/dataset/view_dataset.html` | Bloque "UVL models", menú de flamapy y validación en el navegador con Pyodide | UVL | #12 |
| `explore/templates/explore/index.html` | Texto de ayuda "UVL files" | UVL | #12 |
| `public/templates/public/index.html`, `team/`, páginas de error | Textos y logotipo de uvlhub | común (marca) | Fuera del WI-1.1 |

### Datos de ejemplo

| Dónde | Qué hay | Tipo | Quién lo trata |
| --- | --- | --- | --- |
| `dataset/seeders.py` | Crea `DSMetrics`, `FMMetaData`, `FeatureModel` y copia `uvl_examples/*.uvl` | UVL | #10 añade los seeders de Valorant; los de UVL siguen |
| `dataset/uvl_examples/` | Doce ficheros `.uvl` de ejemplo | UVL | Sin cambios |

## 2. Qué es común y qué es específico

**Común a cualquier dataset** (va en `BaseDataset` o en las tablas que ya comparte):

- Propietario (`user_id`), fecha de creación y metadatos (`DSMetaData`: título, descripción, autores, DOIs, tags y tipo de publicación).
- Descargas (`DSDownloadRecord`), visitas (`DSViewRecord`) y redirección de DOIs (`DOIMapping`).
- Comportamiento: nombre, borrado, tipo de publicación legible, URL de Zenodo y del DOI, número de ficheros, tamaño total y `to_dict()`.

**Específico de UVL** (se queda en `UVLDataset` y en la feature `featuremodel`):

- `FeatureModel`, `FMMetaData`, `FMMetrics` y `DSMetrics`.
- Validación y transformaciones con flamapy.
- Dropzone `.uvl`, `save_temp_uvl` y el bloque "UVL models" de la vista.

**Específico de Valorant CSV** (lo definen #9 y #11): las columnas del formato que fije el equipo a partir del dataset de Valorant elegido (partida, equipos, mapa, rondas, ganador, jugadores con su agente y sus estadísticas, evento, versión del juego y fecha), la validación de cabeceras y tipos, y la vista previa en tabla. Como solo hay un juego, no hace falta una columna "juego" para distinguirlo.

Dos cosas del dominio que afectan al diseño:

- **Un dataset puede tener varios CSV** (por ejemplo, partidas, jugadores por partida y eventos). `files()` devuelve una lista, así que `BaseDataset` ya lo admite sin cambios.
- **Ampliar a League of Legends más adelante** (posibilidad que recoge DEC-001) sería otra subclase de `BaseDataset` o un validador más dentro del tipo de Valorant. En ninguno de los dos casos hay que tocar `BaseDataset`.

## 3. Diseño implementado

```
BaseDataset  (abstracta, sin tabla)
│   id, user_id, ds_meta_data_id, created_at
│   ds_meta_data  →  DSMetaData (título, autores, DOI, tags…)
│   files()            ← cada tipo lo implementa
│   name(), delete(), get_files_count(), get_file_total_size(),
│   get_file_total_size_for_human(), get_cleaned_publication_type(),
│   get_zenodo_url(), get_uvlhub_doi(), to_dict()
│
└── UVLDataset  (tabla data_set, la de siempre)
        feature_models  →  FeatureModel → Hubfile
        files(), get_files_count(), get_file_total_size()

DataSet = UVLDataset   (alias para el código que ya existía)
```

Decisiones:

- **`BaseDataset` es abstracta (`__abstract__ = True`).** No crea tabla ni columna nueva, así que no hace falta migración y la base de datos de preproducción y producción no se toca. La migración para la jerarquía polimórfica es el alcance de #10 y no se adelanta aquí.
- **`UVLDataset` usa la tabla `data_set`.** Las claves ajenas que apuntan a `data_set.id` (descargas, visitas, `feature_model`) siguen valiendo.
- **Se mantiene el alias `DataSet = UVLDataset`.** `DataSet` se importa en 25 ficheros de ocho features (código y pruebas) y aparece unas 90 veces. Renombrarlas todas en esta issue habría tocado ficheros en los que están trabajando otras ramas. El código nuevo debe importar `BaseDataset` o `UVLDataset`.
- **El contrato de un tipo de dataset es `files()`**: devolver la lista de `Hubfile` del dataset. Con eso, `get_files_count`, `get_file_total_size`, `to_dict` y la API (`/api/v1/datasets`) funcionan sin más código. `UVLDataset` mantiene su propia versión de los contadores, que recorre los modelos directamente como antes.
- **`User.data_sets` apunta a `"UVLDataset"`.** SQLAlchemy resuelve las relaciones por el nombre de la clase y `DataSet` ahora es solo un alias.

Comportamiento sin cambios: mismo esquema, mismas rutas, mismas plantillas y mismo JSON en la API.

## 4. Notas para las siguientes issues del WI-1

No son tareas de esta issue: son lo que hay que tener en cuenta al usar `BaseDataset`.

- **#9 (modelo `EsportsDataset`):** heredar de `BaseDataset` e implementar `files()`, que debe devolver todos los CSV del dataset si son varios. Ojo con la relación `ds_meta_data`: crea en `DSMetaData` la referencia inversa `data_set`, y dos clases concretas con tablas distintas no pueden crear la misma. Lo más sencillo es acordar con #10 la estrategia de herencia antes de crear la tabla.
- **#10 (migración):** la opción que menos cambia es la *herencia en una sola tabla*: quitar `__abstract__` de `BaseDataset`, darle `__tablename__ = "data_set"`, añadir una columna discriminadora (por ejemplo `dataset_type`, con valor `uvl` para las filas que ya existen) y declarar `polymorphic_identity` en cada subclase. Así la relación inversa `data_set` se define una sola vez y `User.data_sets` puede pasar a `"BaseDataset"`. `Hubfile.feature_model_id` es obligatorio y solo admite ficheros de UVL: un CSV necesitará otro camino hasta el dataset.
- **#11 (subida CSV):** `save_temp_uvl`, `create_from_form`, `FeatureModelForm` y la Dropzone son las piezas acopladas.
- **#12 (vista y explorador):** el `join` con `feature_models` del explorador deja fuera cualquier dataset que no sea UVL.
- **#13 (descarga y Zenodo):** `ZenodoService.upload_file` recibe un `FeatureModel`; habrá que pasarle los ficheros del dataset (`dataset.files()`).

## 5. Cómo se ha comprobado

- Pruebas nuevas en `app/features/dataset/tests/test_unit.py` para el contrato de `BaseDataset`: es abstracta, `UVLDataset` usa la tabla `data_set` y el alias apunta a `UVLDataset`.
- Toda la batería existente (`pytest -m "not e2e and not load"`) pasa contra MariaDB.
- El `CREATE TABLE data_set` que genera SQLAlchemy tiene las mismas columnas, tipos, nulos y claves ajenas que `migrations/versions/001.py`; solo cambia el orden de las columnas, que no afecta a la base de datos existente.
- La API mantiene sus mensajes: `GET /api/v1/datasets/<id>` inexistente sigue respondiendo `DataSet not found`.
