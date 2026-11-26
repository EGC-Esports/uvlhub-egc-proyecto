# Plantilla oficial de Issue — `EGC-Esports/uvlhub-egc-proyecto`

Utiliza uno de los dos modelos siguientes al abrir una nueva issue en GitHub.

## Cabecera común de uso

- **Formato del título:** `[WI-<bloque>.<subtarea>] <Descripción breve>` (por ejemplo, `[WI-8.3] Crear estructura de documentación en docs/ y guía del proyecto`).
- **Etiquetas obligatorias (exactamente 3, sin espacios tras los dos puntos):**
  - **Tipo:** `feature` | `bug` | `test` | `ci` | `docs`
  - **Prioridad:** `priority:high` | `priority:medium` | `priority:low`
  - **Dificultad:** `difficulty:high` | `difficulty:medium` | `difficulty:low`
- **Campos obligatorios en GitHub:**
  - `Assignees`: persona o personas responsables de la tarea.
  - `Milestone`: `v0.1.0`, `v0.2.0` o `v1.0.0`.
  - `Projects`: añadir al tablero del proyecto (entra en la columna `Pendiente`).

---

## Modelo A — Feature / Docs / CI / Test

**Título:** `[WI-X.Y] Descripción breve de la tarea`

```markdown
## Descripción

[Contexto y alcance concreto de la tarea.]

## Tareas / Requisitos

- [Elemento o requisito 1 a implementar]
- [Elemento o requisito 2 a implementar]

## Criterios de aceptación

- [ ] [Criterio verificable 1 por el revisor]
- [ ] [Criterio verificable 2 por el revisor]

## Pruebas previstas

- [Pruebas unitarias, de integración o Selenium aplicables, si procede.]
```

---

## Modelo B — Bug (según Acta Fundacional §8)

**Título:** `[WI-X.Y] Descripción breve del error`

```markdown
## Descripción

[Contexto breve del error detectado y dónde se produce.]

## Entorno usado

- **Sistema operativo:** [ej. Windows 11, Ubuntu 24.04, macOS]
- **Entorno de ejecución:** [ej. Dev Container, Docker local, entorno nativo, preproducción o producción]
- **Navegador y versión** *(si aplica a interfaz)*: [ej. Chrome, Firefox, Edge]
- **Rama / commit o versión:** [ej. `trunk`, `v0.1.0`, hash del commit]

## Pasos para reproducir

1. [Paso 1]
2. [Paso 2]
3. [Paso 3]

## Resultado esperado

[Comportamiento correcto que debería producirse.]

## Resultado obtenido

[Comportamiento erróneo observado actualmente (incluye mensaje de error o captura si aplica).]

## Criterios de aceptación

- [ ] El error queda corregido según el resultado esperado.
- [ ] Se añade una prueba automatizada de regresión que cubra el error.
- [ ] La suite de pruebas y los checks de CI pasan en verde.
```
