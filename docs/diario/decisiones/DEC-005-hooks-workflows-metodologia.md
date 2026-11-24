# Propuesta: hooks, workflows y metodología de trabajo

- **Fecha:** 20 de noviembre de 2026
- **Estado:** propuesta, pendiente de aprobar en reunión. Una vez aceptada se registrará en el diario como DEC-005.
- **Redacta:** Pedro José Payán Aguilera (Project Manager)
- **Relacionado con:** [acta fundacional](../actas/acta-fundacional.md) (§7 y §8), [DEC-003](./DEC-003-comunicacion-y-reuniones.md), [DEC-004](./DEC-004-tareas-y-ci.md)

## Objetivo

El acta fundacional ya fija cómo queremos trabajar: EGCFlow, Conventional Commits con número de issue, ramas por tarea, issues con criterios de aceptación y CI en `trunk` y en las ramas de tarea. Esta propuesta busca dos cosas:

1. Que esas normas **se comprueben de forma automática** y no dependan de que cada uno se acuerde.
2. Que todo el trabajo **deje evidencia** en el repositorio, porque en la evaluación pesa más el proceso que el código.

Fechas que condicionan el orden de trabajo:

| Fecha | Seguimiento | Qué tiene que estar listo |
| --- | --- | --- |
| 23 de noviembre | Gestión del código fuente e incidencias | Issues, etiquetas, tablero, milestones, reglas de ramas, hook de commits, release v0.1.0 |
| 30 de noviembre | Pruebas automatizadas y CI/CD | Workflows en todas las ramas, cobertura, despliegues de preproducción y producción, release v0.2.0 |
| 14 y 16 de diciembre | Defensa | Release v1.0.0 y diario completo |

## 1. Hooks locales (git)

Usaremos el framework [pre-commit](https://pre-commit.com/), que es Python como el proyecto, con un fichero `.pre-commit-config.yaml` en la raíz del repositorio. Cada miembro lo instala una sola vez:

```bash
pip install pre-commit
pre-commit install --hook-type pre-commit --hook-type commit-msg --hook-type pre-push
```

| Hook | Qué comprueba | Norma del acta |
| --- | --- | --- |
| `commit-msg` | Formato Conventional Commits con el número de issue al final | §7.5 |
| `pre-commit` | Lint y formato del código, espacios al final de línea, ficheros grandes, YAML válido y que no se suban `.env` ni claves | §8 (credenciales fuera del repositorio) |
| `pre-push` | Nombre de la rama, que nadie empuje directamente a `main` y, opcionalmente, que pasen las pruebas unitarias rápidas | §7.1 y §7.6 |

### Formato de los commits

Expresión regular que debe cumplir la primera línea del mensaje:

```
^(feat|fix|docs|test|ci|refactor|chore|build|perf|style|revert)(\([a-z0-9-]+\))?!?: .+ \(#\d+\)$
```

Ejemplos válidos:

```
feat(fakenodo): simular publicación de depósito (#12)
fix(dataset): validar columnas obligatorias del CSV (#15)
docs(diario): añadir acta de la reunión del 23 de noviembre (#30)
```

Se dejan pasar sin comprobar los mensajes que empiezan por `Merge ` y `Revert `, porque los genera git al integrar o revertir.

### Nombre de las ramas

```
^(feat|fix|docs|test|ci|refactor|chore)/\d+-[a-z0-9-]+$
```

Además de `main` y `trunk`. Ejemplos: `feat/12-fakenodo`, `fix/15-validacion`.

### Por qué también hace falta la CI

Un hook se puede saltar con `git commit --no-verify` y solo funciona si cada uno lo ha instalado. Por eso **los workflows repiten las mismas comprobaciones**: el hook sirve para enterarse antes de hacer push y la CI es la que decide. Las herramientas de lint del hook deben ser las mismas, y con la misma versión, que las del workflow de lint, para que no den resultados distintos.

## 2. Workflows de GitHub Actions

Antes de crear nada, se revisarán los workflows que ya trae el fork de UVLHub para adaptarlos en lugar de duplicarlos. Responsable: David (DevOps).

| Workflow | Se ejecuta en | Qué hace |
| --- | --- | --- |
| `commits.yml` | push a cualquier rama | Comprueba el formato de los commits y la referencia `(#N)` |
| `branch-name.yml` | push a cualquier rama | Valida el nombre de la rama |
| `lint.yml` | push a cualquier rama | El mismo lint que el hook `pre-commit` |
| `tests.yml` | push a `trunk`, a las ramas de tarea y a `main` | pytest con MariaDB como servicio, cobertura con un mínimo (`--cov-fail-under`) e informe de cobertura como artefacto |
| `selenium.yml` | push a `trunk` y ejecución manual (`workflow_dispatch`) | Pruebas de interfaz. Son lentas, por eso no se lanzan en cada rama |
| `locust.yml` | ejecución manual y antes de cada release | Pruebas de carga de las partes críticas |
| `sonar.yml` | push a `trunk` | Análisis de calidad con SonarCloud |
| `deploy-preprod.yml` | push a `trunk`, solo si `tests.yml` termina bien (`workflow_run`) | Despliegue en preproducción |
| `release.yml` | push de un tag `v*.*.*` | Ejecuta las pruebas, construye la imagen Docker, crea la GitHub Release con notas generadas a partir de los commits y despliega en producción |

Las credenciales de los despliegues (Docker Hub, Render, SonarCloud…) se guardan como **secretos de GitHub**. En el repositorio solo habrá un `.env.example` sin valores reales.

### Protección de ramas (Settings → Rules → Rulesets)

**`main`**

- Sin push forzado y sin borrado.
- Solo David puede actualizarla (en la lista de bypass del ruleset).
- "Require status checks to pass" con `tests.yml`. Como no usamos pull requests, esta regla exige que el commit haya pasado los checks antes en otra rama. Encaja con nuestro flujo porque `main` solo avanza desde `trunk` con `git merge --ff-only trunk`. Así se cumple lo acordado en DEC-004: no se integra en `main` si fallan las pruebas.

**`trunk`**

- Sin push forzado y sin borrado.
- Se sigue integrando con `git merge --no-ff`, como indica EGCFlow, para que se vea cada tarea en el historial.
- Si la CI de `trunk` falla, arreglarla pasa a ser la prioridad del equipo. Mientras esté en rojo no se despliega en preproducción.

## 3. Gestión de incidencias

### Plantillas de issues

En `.github/ISSUE_TEMPLATE/`:

- **Feature / WI:** descripción, criterios de aceptación y pruebas previstas.
- **Bug:** pasos para reproducirlo, resultado esperado y resultado obtenido, como exige el acta.
- **Tarea:** descripción y criterio de terminado, para trabajo que no es ni feature ni bug (CI, documentación…).

### Etiquetas

| Grupo | Etiquetas |
| --- | --- |
| Tipo | `feature`, `bug`, `test`, `ci`, `docs` |
| Prioridad | `prioridad: alta`, `prioridad: media`, `prioridad: baja` |
| Dificultad | `dificultad: H`, `dificultad: M`, `dificultad: L` |
| Work Item | `WI-newdataset`, `WI-fakenodo`, `WI-2fa`, `WI-sessions`, `WI-recommendations`, `WI-download`, `WI-trending` |

### Milestones

Un milestone por seguimiento, que coincide con la release correspondiente:

| Milestone | Fecha |
| --- | --- |
| v0.1.0 | 23 de noviembre de 2026 |
| v0.2.0 | 30 de noviembre de 2026 |
| v1.0.0 | 14 de diciembre de 2026 |

### Tablero de GitHub Projects

Columnas: **Pendiente → En progreso → En revisión → Hecho**. Se activarán las automatizaciones propias de Projects: una issue nueva entra en *Pendiente* y una issue cerrada pasa a *Hecho*.

## 4. Ciclo de una tarea

1. Se crea la issue con su plantilla, etiquetas, milestone y persona asignada. Pasa a *En progreso*.
2. Se crea la rama desde `trunk`: `git switch trunk && git pull && git switch -c feat/N-descripcion`.
3. Commits atómicos, en español, con `(#N)` al final.
4. Al menos cada dos días de trabajo se actualiza la rama con `trunk` (`git merge trunk`).
5. Push de la rama y CI en verde. La issue pasa a *En revisión* y se pide revisión a otro miembro.
6. El revisor lee el código y deja sus comentarios en la issue.
7. Se integra en `trunk`: `git switch trunk && git pull && git merge --no-ff feat/N-descripcion && git push`.
8. Se despliega en preproducción. El revisor lo prueba allí y **cierra la issue**.
9. Se borra la rama, en local y en remoto.

En los commits se usa `(#N)` para enlazar la issue y **no** palabras como `closes #N` o `fixes #N`, porque cerrarían la issue automáticamente y el acta dice que la cierra una persona distinta de quien la ha implementado.

### Definition of Done

Una tarea está terminada cuando:

- [ ] Cumple todos sus criterios de aceptación.
- [ ] Tiene pruebas (y, si es un bug, una prueba que lo cubre).
- [ ] La CI está en verde en su rama y en `trunk`.
- [ ] La cobertura no baja.
- [ ] La ha revisado otro miembro del equipo.
- [ ] Está integrada en `trunk` y funciona en preproducción.
- [ ] Ha cerrado la issue alguien distinto de quien la implementó.

## 5. Releases

Antes de cada seguimiento, David:

1. Comprueba que la CI de `trunk` está en verde.
2. Actualiza `main`: `git switch main && git pull && git merge --ff-only trunk`.
3. Crea y sube el tag: `git tag -a v0.1.0 -m "v0.1.0" && git push origin main --tags`.
4. `release.yml` publica la release y despliega en producción.
5. Cierra el milestone correspondiente.

## 6. Diario del equipo

- Un acta por reunión en `docs/diario/actas/`, enlazando las issues de las tareas que se repartan.
- Cada decisión técnica o de organización como un `DEC-00X` nuevo.
- El resumen semanal de cada miembro (DEC-003), a ser posible con enlaces a sus commits e issues.
- Las faltas y sanciones en el registro de incumplimientos del README del diario.

## 7. Pendientes detectados en la documentación

Conviene resolverlos antes del seguimiento del 23 de noviembre:

- El acta fundacional dice "Partidos de Esports en CSV", pero DEC-001 dice Valorant y sigue pendiente de aprobación del tutor.
- WI-newdataset y WI-fakenodo no tienen coordinador en el acta.
- El reparto de WIs está descompensado: hay WIs con tres responsables, Rocío aparece en tres WIs y Rubén en dos.
- Sigue sin decidirse si el aviso para faltar a una reunión es de 12 o de 6 horas.
- En el acta del 2 de noviembre aún aparece Hugo, que no figura en el acta fundacional.

## 8. Reparto de tareas propuesto

| Tarea | Responsable | Antes de |
| --- | --- | --- |
| Crear etiquetas, milestones, plantillas de issues y tablero | Pedro | 23 de noviembre |
| Crear una issue por cada WI y sus subtareas | Pedro y responsables de cada WI | 23 de noviembre |
| Configurar los rulesets de `main` y `trunk` | David | 23 de noviembre |
| `.pre-commit-config.yaml` con los hooks de commits, lint y ramas | David | 23 de noviembre |
| Instalar los hooks en local | Todos | 23 de noviembre |
| Release v0.1.0 | David | 23 de noviembre |
| Adaptar los workflows a todas las ramas y añadir cobertura | David | 30 de noviembre |
| Despliegues de preproducción y producción | David | 30 de noviembre |
| Selenium, Locust y SonarCloud en la CI | David y Pedro (calidad) | 30 de noviembre |
| Registrar esta propuesta como DEC-005 una vez aprobada | Pedro | Próxima reunión |

---

> **Nota de estado en el repositorio:** Todos los workflows propuestos en `.github/workflows/` (`commits.yml`, `branch-name.yml`, `lint.yml`, `tests.yml`, `selenium.yml`, `locust.yml`, `sonar.yml`, `deploy-preprod.yml` y `release.yml`, además de `deploy-prod.yml` y `cleanup-branches.yml`) y los hooks en `.pre-commit-config.yaml` ya están implementados en el repositorio; quedan pendientes las plantillas en `.github/ISSUE_TEMPLATE/`.
