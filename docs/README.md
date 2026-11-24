# Documentación del proyecto — Esports-hub

Guía central de trabajo, normativa de configuración, entorno de desarrollo, dataset y diario del equipo **Esports-hub** (`EGC-Esports/uvlhub-egc-proyecto`).

## Índice

1. [Mapa de `docs/`](#1-mapa-de-docs)
2. [Identificación del equipo y proyecto](#2-identificación-del-equipo-y-proyecto)
3. [Work Items asignados](#3-work-items-asignados)
4. [Roles y responsabilidades](#4-roles-y-responsabilidades)
5. [Política de gestión de ramas (EGCFlow)](#5-política-de-gestión-de-ramas-egcflow)
6. [Política de commits (Conventional Commits)](#6-política-de-commits-conventional-commits)
7. [Configuración y uso de Git hooks](#7-configuración-y-uso-de-git-hooks)
8. [Acuerdos de comunicación y calendario](#8-acuerdos-de-comunicación-y-calendario)
9. [Gestión de incidencias, estrategia de pruebas y CI/CD](#9-gestión-de-incidencias-estrategia-de-pruebas-y-cicd)
10. [Régimen interno y tabla de sanciones](#10-régimen-interno-y-tabla-de-sanciones)

---

## 1. Mapa de `docs/`

| Ruta | Propósito y nomenclatura |
| --- | --- |
| [`docs/README.md`](README.md) | Guía principal del repositorio y normativa de trabajo del equipo |
| [`docs/devcontainer.md`](devcontainer.md) | Configuración, arranque y uso diario del entorno de desarrollo en Dev Container |
| [`docs/dataset-valorant.md`](dataset-valorant.md) | Origen, esquema de 25 columnas y generación del dataset CSV de Valorant |
| [`docs/diario/`](diario/README.md) | Diario del equipo: índice en `README.md`, actas en `actas/` (`AAAA-MM-DD-tema.md` y `acta-fundacional.md`) y decisiones en `decisiones/` (`DEC-XXX-titulo.md`) |
| [`docs/plantillas/`](plantillas/) | Plantillas reutilizables ([`acta.md`](plantillas/acta.md), [`decision.md`](plantillas/decision.md) e [`issue.md`](plantillas/issue.md)) para nuevas entradas del diario e issues |

---

## 2. Identificación del equipo y proyecto

Según el [Acta Fundacional](diario/actas/acta-fundacional.md) (9 de noviembre de 2026):

- **Equipo:** Esports-hub
- **Asignatura:** Evolución y Gestión de la Configuración (Curso 2026/2027), Grado en Ingeniería Informática – Ingeniería del Software, ETSII, Universidad de Sevilla
- **Tutor:** Jesús Moreno León
- **Repositorio:** `EGC-Esports/uvlhub-egc-proyecto` *(en el Acta Fundacional firmada figuraba inicialmente como `Repositorio-EGC`)*
- **Tipo de hub:** Partidos de Esports en CSV procedentes principalmente de Kaggle (centrado inicialmente en partidas profesionales de Valorant según [DEC-001](diario/decisiones/DEC-001-dominio-valorant.md) y detallado en [dataset-valorant.md](dataset-valorant.md)).

### Miembros del equipo

| Nombre y apellidos | UVUS | Correo electrónico | Usuario de GitHub | Rol |
| --- | --- | --- | --- | --- |
| Pedro José Payán Aguilera | `NBD5780` | `ppayan@us.es` | `@ThePayan` | Project Manager y Responsable de calidad |
| David Lozano Acosta | `FBN5868` | `davlozaco@alum.us.es` | `@dlozaco` | DevOps |
| Raúl Jiménez Pérez | `LSW6941` | `raujimper@alum.us.es` | `@RaulJimPer` | Desarrollador |
| Rocío Morato Aguilar | `XTR5967` | `rocmoragu@alum.us.es` | `@Rma816` | Desarrolladora |
| Rubén López Expósito | `CRP8717` | `rublopexp@alum.us.es` | `@RuLop816` | Desarrollador |

---

## 3. Work Items asignados

| Work Item | Issue original | Dificultad / Tipo | Responsables (Acta Fundacional) |
| --- | --- | --- | --- |
| WI-newdataset | `#178` | Común | Todo el equipo *(coordinación planificada: Pedro José Payán Aguilera)* |
| WI-fakenodo | `#177` | Común | Todo el equipo *(coordinación planificada: David Lozano Acosta)* |
| Two-factor authentication (2FA) | `#200` | Alta | Pedro José Payán Aguilera, Rocío Morato Aguilar, David Lozano Acosta |
| Active session management | `#202` | Alta | Raúl Jiménez Pérez, Rubén López Expósito, David Lozano Acosta |
| Automatic dataset recommendations | `#209` | Media | Raúl Jiménez Pérez, Rocío Morato Aguilar |
| Download own dataset | `#184` | Media | Rubén López Expósito, Pedro José Payán Aguilera |
| Trending datasets | `#211` | Baja | Rocío Morato Aguilar |

> **Nota de planificación:** En el Acta Fundacional firmada el 9 de noviembre el campo de coordinador de `#178` y `#177` figuraba pendiente de definir; los coordinadores indicados proceden de la planificación en `Planificacion_WIs_Issues_Esports_Hub`.

---

## 4. Roles y responsabilidades

- **Project Manager (Pedro José Payán Aguilera):** organiza y convoca las reuniones, mantiene actualizado el tablero de tareas, redacta las actas y es el contacto principal con el tutor.
- **DevOps (David Lozano Acosta):** se encarga de los workflows de GitHub Actions, los contenedores Docker y los despliegues, y crea las releases en `main`.
- **Responsable de calidad (Pedro José Payán Aguilera):** comprueba que cada tarea tenga sus pruebas, controla la cobertura y verifica las issues antes de cerrarlas.
- **Desarrollador/a (Rocío Morato Aguilar, Raúl Jiménez Pérez, Rubén López Expósito):** implementan los Work Items asignados y resuelven las incidencias que vayan surgiendo. Todos los miembros desarrollan al menos un WI con sus pruebas y conocen el funcionamiento general del proyecto.

**Regla de sustitución:** si alguien no puede asumir su rol, se nombrará un sustituto en la siguiente reunión y quedará reflejado en el diario del equipo (`docs/diario/`).

---

## 5. Política de gestión de ramas (EGCFlow)

### Ramas permanentes

- **`main`:** solo contiene versiones entregadas, cada una marcada con su tag y release con versionado semántico (`v0.1.0`, `v0.2.0`..., `v1.0.0` para la entrega final), creadas por el responsable de DevOps antes de cada seguimiento.
- **`trunk`:** rama de integración donde se mezcla el trabajo terminado.

### Ramas de tarea

- **Nomenclatura obligatoria:** `tipo/número-de-issue-descripción` (ej. `feat/12-fakenodo`, `fix/15-validacion`).
  - Expresión regular validada en `scripts/ci/check_branch_name.py`: `^(feat|fix|docs|test|ci|refactor|chore)/\d+-[a-z0-9-]+$`.
  - **Prohibido** crear ramas por persona.
- Se crean **siempre desde `trunk`**.
- Mientras estén activas, se actualizan con `trunk` al menos cada **2 días de trabajo** (`git merge trunk`).
- Solo se integran en `trunk` cuando cumplen los criterios de aceptación, tienen pruebas y la CI pasa en verde.
- La integración en `trunk` se hace en local mediante `git merge --no-ff`, **sin Pull Requests dentro del equipo** (las PR se reservan para proponer cambios a otros equipos).
- Se eliminan en local y en remoto tras integrarse en `trunk` (en remoto lo automatiza `.github/workflows/cleanup-branches.yml`).

### Prohibiciones explícitas

- **Prohibido** hacer commits directos sobre `main`.
- **Prohibido** usar `git push --force` sobre `main` o `trunk`.

### Ciclo diario paso a paso

```bash
# 1. Crear rama de tarea desde trunk actualizada
git switch trunk
git pull origin trunk
git switch -c feat/12-fakenodo

# 2. Sincronizar con trunk al menos cada 2 días de trabajo
git fetch origin
git merge origin/trunk

# 3. Integrar en trunk en local cuando la tarea esté lista y la CI en verde
git switch trunk
git pull origin trunk
git merge --no-ff feat/12-fakenodo
git push origin trunk

# 4. Eliminar la rama local (la remota la limpia cleanup-branches.yml al hacer merge --no-ff)
git branch -d feat/12-fakenodo
```

---

## 6. Política de commits (Conventional Commits)

- **Formato obligatorio:** `tipo(alcance): descripción (#issue)`
- **Expresión regular (implementada en `scripts/ci/check_commit_msg.py`):**
  ```regex
  ^(feat|fix|docs|test|ci|refactor|chore|build|perf|style|revert)(\([a-z0-9-]+\))?!?: .+ \(#\d+\)$
  ```
  *(Se permiten automáticamente los mensajes generados por Git que comienzan por `Merge ` o `Revert `).*

| Tipo | Uso principal |
| --- | --- |
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de un error |
| `docs` | Cambios en documentación |
| `test` | Añadir o corregir pruebas |
| `ci` | Workflows de CI/CD y scripts de automatización |
| `refactor` | Reestructuración de código sin cambiar comportamiento |
| `chore` | Tareas de mantenimiento, dependencias o configuración |
| `build` | Cambios en sistema de construcción o empaquetado |
| `perf` | Mejoras de rendimiento |
| `style` | Formato de código sin impacto lógico |
| `revert` | Reversión de un commit anterior |

**Ejemplos válidos en español:**
- `feat(fakenodo): simular publicación de depósito (#12)`
- `fix(dataset): validar columnas obligatorias del CSV (#15)`

### Reglas obligatorias

1. Commits **atómicos** y redactados en **español**.
2. Configurar `git config user.name` y `git config user.email` con exactamente el mismo nombre y correo que la cuenta de GitHub de cada miembro.
3. Usar `(#N)` para referenciar la issue y **NO** usar palabras clave de autocierre (`closes #N`, `fixes #N`), ya que las issues debe cerrarlas una persona distinta de quien las implementó.

---

## 7. Configuración y uso de Git hooks

### Configuración actual en el repositorio

El repositorio utiliza el framework **`pre-commit`** definido en [`.pre-commit-config.yaml`](../.pre-commit-config.yaml) (con `default_install_hook_types: [pre-commit, commit-msg, pre-push]`).

**Instalación (una sola vez por persona en local):**

```bash
pip install pre-commit
pre-commit install
```

**Ejecución manual:**

```bash
pre-commit run --files <ficheros>
pre-commit run unit-tests --hook-stage manual
```

*(Evitar `pre-commit run --all-files` para no reescribir ficheros heredados de UVLHub sin tocar).*

### Qué valida cada hook

- **`commit-msg` (`commit-msg-format`):** ejecuta `python scripts/ci/check_commit_msg.py` para validar Conventional Commits en español y la referencia `(#N)`.
- **`pre-commit`:**
  - Higiene: `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-toml`, `check-added-large-files` (`--maxkb=1024`), `check-merge-conflict`, `detect-private-key`.
  - Seguridad: `forbid-env-files` bloquea ficheros `.env` reales (permitiendo `.env.*.example` y `.env.selenium`).
  - Lint y formato sobre `app/`, `rosemary/`, `scripts/` y `tests/`: `flake8` (`7.5.0` + `flake8-pyproject==1.2.4`), `black` (`26.10.1`) e `isort` (`9.0.2`), sincronizados con `requirements-lint.in` y `pyproject.toml`.
- **`pre-push` (`branch-name`):** ejecuta `python scripts/ci/check_branch_name.py --pre-push` para validar el nombre de la rama y bloquear `push` directo a `main` (salvo `ALLOW_PUSH_TO_MAIN=1` usado por DevOps en releases).

### Política sobre `--no-verify` y estado respecto a DEC-005

- **Prohibido usar `--no-verify`** para saltarse controles de calidad o formato: los workflows de CI en GitHub Actions (`commits.yml`, `branch-name.yml`, `lint.yml`) repiten exactamente las mismas comprobaciones en remoto.
- **Alineación con [DEC-005](diario/decisiones/DEC-005-hooks-workflows-metodologia.md):** los tres hooks (`commit-msg`, `pre-commit`, `pre-push`) ya están implementados y operativos en `.pre-commit-config.yaml`.

---

## 8. Acuerdos de comunicación y calendario

- **Microsoft Teams:** canal principal del día a día (avisos, dudas rápidas, convocatorias de reuniones y resumen semanal de avance de cada miembro).
- **GitHub Issues:** tareas, incidencias y decisiones técnicas.
- **Correo de la Universidad:** comunicación oficial con el tutor.
- **Reuniones:** idealmente una vez por semana según disponibilidad, levantando acta breve en `docs/diario/actas/`. Compromiso de respuesta en el grupo en un máximo de **24 horas**.

| Fecha | Hito |
| --- | --- |
| 9 de noviembre de 2026 | Entrega del Acta Fundacional y 1.er seguimiento |
| 23 de noviembre de 2026 | 2.º seguimiento (gestión del código fuente e incidencias) |
| 30 de noviembre de 2026 | 3.er seguimiento (pruebas automatizadas y CI/CD) |
| 14 y/o 16 de diciembre de 2026 | Defensa del proyecto |

---

## 9. Gestión de incidencias, estrategia de pruebas y CI/CD

### Formato oficial de Issues

Todas las nuevas issues del repositorio siguen los modelos definidos en [`docs/plantillas/issue.md`](plantillas/issue.md):

1. **Nomenclatura de títulos:** `[WI-<bloque>.<subtarea>] <Descripción breve>` según los bloques de Work Items del repositorio:

   | Bloque | Work Item / Ámbito | Issue asociada |
   | --- | --- | --- |
   | `WI-1.x` | `WI-newdataset` — adaptación a Esports CSV | `#178` |
   | `WI-2.x` | `WI-fakenodo` — servicio simulado de Zenodo | `#177` |
   | `WI-3.x` | `Two-factor authentication (2FA)` | `#200` |
   | `WI-4.x` | `Active session management` | `#202` |
   | `WI-5.x` | `Automatic dataset recommendations` | `#209` |
   | `WI-6.x` | `Download own dataset` | `#184` |
   | `WI-7.x` | `Trending datasets` | `#211` |
   | `WI-8.x` | Tareas transversales del proyecto (infraestructura, seguridad, DevContainer, CI y documentación) | — |

2. **Sistema de etiquetas exacto en GitHub (sin espacios tras los dos puntos):**
   - **Tipo:** `feature`, `bug`, `test`, `ci`, `docs`
   - **Prioridad:** `priority:high`, `priority:medium`, `priority:low`
   - **Dificultad:** `difficulty:high`, `difficulty:medium`, `difficulty:low`

   > Todas las issues nuevas deben usar exactamente estas etiquetas normalizadas (evitando etiquetas o campos sueltos como `Low` o `Medium` para mantener filtros consistentes).

3. **Estructura del cuerpo y cierre:**
   - **Cuerpo:** descripción clara, lista de tareas/requisitos y `Criterios de aceptación` verificables (en *bugs*, además, pasos para reproducir, resultado esperado, resultado obtenido y prueba automatizada de regresión).
   - **Planificación y flujo:** asignar `Assignees`, `Milestone` (`v0.1.0`, `v0.2.0` o `v1.0.0`) y añadir al tablero de **GitHub Projects** (`Pendiente` → `En progreso` → `En revisión` → `Hecho`).
   - **Cierre:** cierra la issue una persona distinta de quien la implementó tras verificar los criterios de aceptación.

- **Tablero:** GitHub Projects con las columnas *Pendiente*, *En progreso*, *En revisión* y *Hecho*.
- **Incidencias:** cada issue lleva persona asignada, descripción, criterios de aceptación y etiquetas de tipo (`feature`, `bug`, `test`, `ci`, `docs`), prioridad y dificultad. Los *bugs* incluyen pasos para reproducir, resultado esperado y resultado obtenido. Cierra la issue una persona distinta de quien la implementó tras verificarla.
- **Estrategia de pruebas:**
  - Unitarias e integración con `pytest` (`pyproject.toml` define los marcadores `unit`, `repository`, `service`, `integration`, `e2e` y `load`).
  - Interfaz con `Selenium` y carga con `Locust` en partes críticas.
  - Prueba de regresión por cada bug corregido.
  - Análisis de calidad y cobertura con `SonarCloud` (`sonar-project.properties`).
- **CI/CD en el repositorio (`.github/workflows/`):**
  - Actualmente están configurados: `branch-name.yml`, `commits.yml`, `lint.yml`, `tests.yml` (en `trunk` y ramas de tarea, exigiendo un mínimo de cobertura del 60 % mediante `COVERAGE_MIN: 60`), `selenium.yml` (`trunk` y manual), `locust.yml` (manual), `sonar.yml` (tras `Tests` en `trunk`), `deploy-preprod.yml` (tras `Tests` en `trunk`), `deploy-prod.yml` (`main`, que ejecuta `tests.yml` y `locust.yml` antes de desplegar en producción), `release.yml` (tags `vX.Y.Z`) y `cleanup-branches.yml` (`trunk`).
  - **Pendiente respecto a DEC-005:** crear las plantillas de issues en `.github/ISSUE_TEMPLATE/`.
- **Entornos y secretos:** despliegue de `trunk` en preproducción y releases de `main` en producción; credenciales únicamente en **GitHub Secrets**; entorno común de desarrollo documentado en [devcontainer.md](devcontainer.md).

---

## 10. Régimen interno y tabla de sanciones

### Normas de obligado cumplimiento (Acta Fundacional §9)

1. Asistir a las reuniones acordadas o avisar con al menos **12 horas** de antelación.
2. Cumplir los plazos de las tareas asignadas y avisar con tiempo si no se van a poder cumplir.
3. Dejar todo el trabajo reflejado en el repositorio y enlazado a su issue correspondiente.
4. Entender y saber explicar el código que cada uno sube al repositorio.
5. Tomar las decisiones por consenso y, si no es posible, por mayoría; en caso de empate, decidirá el Project Manager.

### Tabla de incumplimientos y sanciones

| Incumplimiento | Primera vez | Segunda vez | Tercera vez |
| --- | --- | --- | --- |
| Faltar a una reunión sin avisar | Se anota en el acta | Aviso formal del equipo | Se comunica al tutor/a |
| No responder en el plazo acordado | Recordatorio en el grupo | Se anota en el diario | Aviso formal del equipo |
| No entregar una tarea a tiempo sin avisar | Se fija un nuevo plazo | Se reasigna la tarea | Se comunica al tutor/a |
| Una semana sin participar ni dar explicaciones | Reunión con la persona | Se comunica al coordinador | - |

Consulta el texto íntegro en [docs/diario/actas/acta-fundacional.md](diario/actas/acta-fundacional.md).
