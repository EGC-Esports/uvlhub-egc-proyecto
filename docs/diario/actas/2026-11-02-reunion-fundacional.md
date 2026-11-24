# Acta de reunión: reunión fundacional

- **Fecha:** 2 de noviembre de 2026, 11:05
- **Duración:** 43 minutos aproximadamente
- **Lugar:** Microsoft Teams (canal General), con grabación y transcripción
- **Asistentes:** Pedro José Payán Aguilera, David Lozano Acosta, Raúl Jiménez Pérez y Rocío Morato Aguilar
- **Ausentes:** Rubén López Expósito (facilitó sus datos a través de David)
- **Redacta:** Pedro José Payán Aguilera

## Orden del día

1. Entrega del acta fundacional y evaluación del proyecto
2. Datos del equipo y repositorio
3. Dominio del hub
4. Work Items
5. Roles
6. Comunicación y reuniones
7. Ramas, commits, tareas, pruebas y CI/CD
8. Régimen interno y firmas

## Desarrollo

### 1. Entrega del acta fundacional y evaluación

Pedro recuerda que el acta fundacional se entrega el 9 de noviembre y que la asistencia a las tres sesiones de seguimiento es obligatoria: cada falta resta 0,25 puntos sobre los 2,5 del proyecto. También recuerda que en la evaluación pesa más la metodología que el código, aunque el código también cuenta. Nuestro tutor es el coordinador de la asignatura.

### 2. Datos del equipo y repositorio

Se recogen el nombre, UVUS, correo y usuario de GitHub de los asistentes para completar el acta. Rubén los envió a través de David. Faltan los datos de Hugo.

Pedro ya tiene hecho el fork de UVLHub y, al final de la reunión, envía las invitaciones al repositorio.

### 3. Dominio del hub

Se confirma que el hub trabajará con datasets en CSV de partidas de esports. Se discute si abarcar varios juegos o limitarse a uno:

- Raúl señala que League of Legends y Valorant miden cosas muy distintas, por lo que sería difícil tener un formato común.
- Pedro propone admitir varios juegos con un parser distinto para cada uno, elegido mediante un patrón factory. Raúl lo ve viable, pero cree que el esfuerzo no compensa para lo que vale el proyecto.
- David insiste en que, para poder validar los ficheros, todos los CSV tienen que seguir un formato homogéneo que habrá que definir.

Se revisan varias fuentes de datos: datasets de Kaggle (algunos de LoL con datos desde 2014 y otros solo de 2026), fuentes oficiales de Riot y páginas específicas de Valorant. Raúl encuentra un dataset de Valorant bastante completo, con el historial de partidas, los jugadores, el agente elegido, las kills y el resto de estadísticas, el equipo ganador y los eventos con la versión del juego y la fecha. Como alternativas, Rocío propone generar nuestros propios datos y David plantea obtenerlos mediante scraping.

David advierte de que Valorant tiene menos años de datos (desde 2020 aproximadamente) y que podrían quedarse cortos. Rocío propone empezar con Valorant y ampliar a LoL más adelante si hiciera falta, modificando el acta en una reunión y consultándolo con el tutor en un seguimiento.

Se acuerda que el hub será de partidas de Valorant en formato CSV ([DEC-001](../decisiones/DEC-001-dominio-valorant.md)).

### 4. Work Items

Con cinco integrantes nos corresponden los dos WI comunes (WI-newdataset y WI-fakenodo) más dos de dificultad alta, dos de dificultad media y uno de dificultad baja. Si se incorpora un sexto miembro, se añadiría otro de dificultad baja. Cada persona será responsable de uno de ellos.

No está claro si los WI los asigna el profesorado o los elige el equipo. Pedro preguntará al coordinador. Si los elegimos nosotros, escogeremos los que parezcan más asumibles. Pedro revisará la sección de Work Items del acta en función de la respuesta.

### 5. Roles

Pedro será el Project Manager y David, el DevOps del equipo. David no tiene inconveniente en asumir él solo el rol de DevOps; Raúl propone que se centre en esas tareas y tenga algo menos de carga de desarrollo. El resto de roles queda pendiente ([DEC-002](../decisiones/DEC-002-roles.md)).

### 6. Comunicación y reuniones

Para el día a día y para convocar reuniones se usará el grupo del equipo. Con el tutor nos comunicaremos por el correo de la Universidad.

Fijar una reunión semanal en un día concreto (David propuso los domingos) se considera demasiado rígido. Se acuerda reunirse idealmente una vez por semana, según la disponibilidad de cada momento. Además, Rocío propone que cada miembro publique cada semana en el grupo lo que ha hecho, y se acepta ([DEC-003](../decisiones/DEC-003-comunicacion-y-reuniones.md)).

### 7. Ramas, commits, tareas, pruebas y CI/CD

- **Ramas:** se mantiene EGCFlow tal como se explicó en teoría: `main`, `trunk` y ramas de tarea que se borran tras integrarlas. No se usarán pull requests dentro del equipo, así que los conflictos se resolverán con merges en local.
- **Commits:** se usará Conventional Commits. El repositorio ya incluye un workflow que lo comprueba. Se comenta que David, como DevOps, podría preparar un hook de pre-commit para detectar los errores antes de hacer push.
- **Tareas:** se usará un tablero de GitHub Projects. Se descartan Jira y otras herramientas externas para tenerlo todo en GitHub.
- **Pruebas:** pruebas unitarias y de integración con pytest, pruebas de interfaz con Selenium y pruebas de carga con Locust, como en las prácticas.
- **CI/CD:** los workflows se ejecutarán sobre `trunk` y sobre las ramas de tarea. Habrá dos despliegues: `trunk` en preproducción y las releases de `main` en producción. También se añadirá un workflow que ejecute las pruebas en cada commit y que impida integrar en `main` si fallan, reutilizando lo hecho en las prácticas.

Ver [DEC-004](../decisiones/DEC-004-tareas-y-ci.md).

### 8. Régimen interno y firmas

Se revisan las normas y la tabla de consecuencias del acta fundacional y se aceptan. David propone reducir de 12 a 6 horas el aviso previo para faltar a una reunión; queda pendiente de decidir.

El acta fundacional se fechará el 9 de noviembre. Pedro compartirá un PDF para firmarla. Como alternativas, David enviará una foto de su firma y Rocío ofrece su tablet para firmar en clase. Pedro sube el acta a Teams para que todos puedan editarla.

## Acuerdos

1. El hub será de partidas de Valorant en CSV, con la posibilidad de ampliarlo a League of Legends más adelante (DEC-001).
2. Pedro será el Project Manager y David, el DevOps (DEC-002).
3. Nos reuniremos idealmente una vez por semana según disponibilidad, y cada miembro publicará semanalmente en el grupo lo que ha hecho (DEC-003).
4. Usaremos GitHub Projects, EGCFlow y Conventional Commits. Los workflows se ejecutarán en `trunk` y en las ramas de tarea, con despliegue de `trunk` en preproducción y de `main` en producción, y se bloqueará la integración en `main` si fallan las pruebas (DEC-004).
5. Se aceptan las normas del régimen interno. El plazo de aviso para faltar a una reunión queda pendiente.

## Tareas

| Tarea | Responsable | Issue |
| --- | --- | --- |
| Preguntar al coordinador si los WI los asigna el profesorado o los elige el equipo | Pedro | |
| Adaptar el acta fundacional con lo acordado en esta reunión | Pedro | |
| Compartir el acta fundacional en PDF para firmarla | Pedro | |
| Aceptar la invitación al repositorio de GitHub | Todos | |
| Conseguir los datos de Hugo | Por asignar | |
| Definir el formato del CSV (columnas obligatorias) a partir del dataset de Valorant | Por asignar | |
| Preparar un hook de pre-commit para Conventional Commits | David | |
| Consultar en el seguimiento del 9 de noviembre si el acta puede modificarse más adelante | Pedro | |

## Próxima reunión

- **Fecha:** por determinar, según disponibilidad.
- **Temas:** asignación de los Work Items y definición de la forma de trabajar una vez conocidos.
