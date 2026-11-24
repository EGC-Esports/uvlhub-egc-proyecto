# DEC-001: Dominio del hub, partidas de Valorant en CSV

- **Fecha:** 2 de noviembre de 2026
- **Estado:** aceptada por el equipo, pendiente de aprobación del tutor
- **Participantes:** Pedro, David, Raúl y Rocío
- **Relacionado con:** WI-newdataset (#178), [acta del 2 de noviembre](../actas/2026-11-02-reunion-fundacional.md)

## Contexto

El WI-newdataset pide adaptar UVLHub para que gestione un tipo de datos distinto de UVL. El equipo quería trabajar con datasets de partidas de esports en formato CSV.

Para que el hub aporte algo frente a un repositorio genérico, tiene que poder validar los ficheros que se suben, igual que flamapy valida un `.uvl`. Para eso, todos los CSV deben seguir un formato común.

## Opciones consideradas

1. **Varios juegos (LoL y Valorant), con un parser por juego elegido mediante un factory.** Es la opción más completa, pero cada juego mide cosas distintas, habría que definir y mantener varios formatos, y el esfuerzo no compensa para lo que vale el proyecto.
2. **Solo League of Legends.** Hay muchos datos disponibles (datasets de Kaggle con datos desde 2014 y fuentes oficiales de Riot).
3. **Solo Valorant.** Hay un dataset bastante completo: historial de partidas con los jugadores, el agente elegido, las kills y el resto de estadísticas, el equipo ganador y los eventos con la versión del juego y la fecha. Tiene menos años de historia (desde 2020 aproximadamente).

## Decisión

Elegimos la opción 3: el hub gestionará datasets de partidas de Valorant en CSV. La mayoría del equipo conoce mejor Valorant que LoL, y el dataset encontrado tiene la información que necesitamos. El formato del CSV se definirá a partir de ese dataset.

## Consecuencias

- Con un único formato, la validación es más sencilla: columnas fijas y tipos conocidos.
- Si el volumen de datos se queda corto, se podrá ampliar a League of Legends más adelante. Ese cambio tendrá que aprobarse en una reunión, registrarse en el diario y consultarse con el tutor.
- Intentaremos que la validación permita añadir otro juego más adelante sin rehacerla, aprovechando la idea del factory.
- Pendiente: definir las columnas obligatorias del CSV y obtener la aprobación del tutor.
