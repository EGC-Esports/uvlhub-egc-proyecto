# DEC-004: Gestión de tareas, pruebas y CI/CD

- **Fecha:** 2 de noviembre de 2026
- **Estado:** aceptada
- **Participantes:** Pedro, David, Raúl y Rocío
- **Relacionado con:** [acta del 2 de noviembre](../actas/2026-11-02-reunion-fundacional.md)

## Contexto

Hay que decidir con qué herramienta se gestionan las tareas y cómo se integran las pruebas y los despliegues con el modelo de ramas EGCFlow. Según nos explicaron en clase, el equipo tiene libertad para elegir la herramienta de gestión de tareas.

## Opciones consideradas

- **Tablero:** GitHub Projects, Jira u otras herramientas externas.
- **CI:** dejar los workflows de UVLHub como están (las pruebas solo se ejecutan sobre `main`) o adaptarlos a EGCFlow.

## Decisión

- **Tablero:** GitHub Projects, para tenerlo todo en el mismo sitio que el código y las issues.
- **Ramas y commits:** EGCFlow tal como se explicó en teoría, sin pull requests dentro del equipo, y Conventional Commits, que ya comprueba el workflow del repositorio. David valorará añadir un hook de pre-commit para detectar los errores antes del push.
- **Pruebas:** pruebas unitarias y de integración con pytest, de interfaz con Selenium y de carga con Locust.
- **CI/CD:**
  - Los workflows se ejecutarán sobre `trunk` y sobre las ramas de tarea.
  - Habrá un workflow que ejecute las pruebas en cada commit e impida integrar en `main` si fallan.
  - Habrá dos despliegues: `trunk` en preproducción y las releases de `main` en producción.

## Consecuencias

- Hay que modificar los workflows actuales, porque ahora pytest solo se ejecuta sobre `main`. Se reutilizará lo hecho en las prácticas.
- Hay que preparar dos entornos de despliegue (preproducción y producción).
- Responsable: David, como DevOps.
