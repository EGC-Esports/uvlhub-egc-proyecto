# Diario del equipo — Esports-hub

Este directorio recoge la memoria de trabajo del equipo **Esports-hub** durante el desarrollo del proyecto en la asignatura *Evolución y Gestión de la Configuración* (Curso 2026/2027). Sirve como evidencia trazable de las reuniones celebradas, los acuerdos alcanzados, las decisiones técnicas y organizativas, el seguimiento semanal y las incidencias de régimen interno.

## Índice de actas

| Fecha | Documento | Descripción |
| --- | --- | --- |
| 2 de noviembre de 2026 | [2026-11-02-reunion-fundacional.md](actas/2026-11-02-reunion-fundacional.md) | Acta de la reunión fundacional (elección de dominio, roles iniciales, comunicación y CI/CD) |
| 9 de noviembre de 2026 | [acta-fundacional.md](actas/acta-fundacional.md) | Acta Fundacional del equipo Esports-hub (normativa completa y compromisos firmados) |

## Índice de decisiones

| ID | Documento | Estado | Resumen |
| --- | --- | --- | --- |
| DEC-001 | [DEC-001-dominio-valorant.md](decisiones/DEC-001-dominio-valorant.md) | Aceptada por el equipo (pendiente de aprobación del tutor) | Elección de partidos de Valorant en CSV como dominio inicial del hub |
| DEC-002 | [DEC-002-roles.md](decisiones/DEC-002-roles.md) | Aceptada (completada en el Acta Fundacional) | Asignación inicial de Project Manager (Pedro) y DevOps (David) |
| DEC-003 | [DEC-003-comunicacion-y-reuniones.md](decisiones/DEC-003-comunicacion-y-reuniones.md) | Aceptada | Canales de comunicación, cadencia de reuniones y resumen semanal |
| DEC-004 | [DEC-004-tareas-y-ci.md](decisiones/DEC-004-tareas-y-ci.md) | Aceptada | Gestión de tareas en GitHub Projects, EGCFlow, pruebas y CI/CD |
| DEC-005 | [DEC-005-hooks-workflows-metodologia.md](decisiones/DEC-005-hooks-workflows-metodologia.md) | Aceptada | Definición operativa de hooks locales, workflows de GitHub Actions y metodología de trabajo |

## Cómo añadir una nueva entrada

### Nueva acta de reunión

1. Copia la plantilla [docs/plantillas/acta.md](../plantillas/acta.md) dentro de `docs/diario/actas/` con el formato `AAAA-MM-DD-tema-breve.md` (por ejemplo, `2026-11-16-seguimiento-semanal.md`).
2. Rellena los metadatos, el orden del día, el desarrollo, los acuerdos (enlazando las decisiones `DEC-XXX` si procede), la tabla de tareas y la próxima reunión.
3. Añade la fila correspondiente en la tabla **Índice de actas** de este archivo.

### Nueva decisión (`DEC-XXX`)

1. Copia la plantilla [docs/plantillas/decision.md](../plantillas/decision.md) dentro de `docs/diario/decisiones/` con el formato `DEC-XXX-titulo-breve.md`, usando el siguiente número correlativo.
2. Documenta el contexto, las opciones consideradas, la decisión adoptada y sus consecuencias.
3. Añade la fila correspondiente en la tabla **Índice de decisiones** de este archivo y enlázala desde el acta de la reunión en la que se aprobó.

## Seguimiento semanal

Según lo acordado en [DEC-003](decisiones/DEC-003-comunicacion-y-reuniones.md), cada miembro comparte un resumen semanal breve de su avance (qué ha hecho, qué hará y si tiene bloqueos) en el grupo de Microsoft Teams y se consolida en las actas semanales del diario.

| Semana | Resumen / Enlace al acta | Observaciones |
| --- | --- | --- |
| Semana 1 (02/11/2026 – 08/11/2026) | [2026-11-02-reunion-fundacional.md](actas/2026-11-02-reunion-fundacional.md) | Arranque del equipo, definición de dominio y roles iniciales |
| Semana 2 (09/11/2026 – 15/11/2026) | [acta-fundacional.md](actas/acta-fundacional.md) | Firma del Acta Fundacional y 1.er seguimiento (9 de noviembre) |

## Registro de incumplimientos y sanciones

Registro conforme al apartado 9 del [Acta Fundacional](actas/acta-fundacional.md) y a [DEC-005](decisiones/DEC-005-hooks-workflows-metodologia.md).

| Fecha | Miembro | Incumplimiento | Medida aplicada | Referencia |
| --- | --- | --- | --- | --- |
| — | — | Sin incidencias registradas | — | — |
