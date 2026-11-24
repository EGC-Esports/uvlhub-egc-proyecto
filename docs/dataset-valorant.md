# Documentación técnica del dataset de Valorant — Esports-hub

Este documento describe el origen, la estructura original en SQLite, el esquema final en CSV, los criterios de selección y el proceso técnico de generación del dataset de partidas profesionales de **Valorant** utilizado como dominio inicial de **Esports-hub** (véase [DEC-001](diario/decisiones/DEC-001-dominio-valorant.md)).

## 1. Fuente de información

- **Origen:** Kaggle — [Valorant Pro Matches Full Data](https://www.kaggle.com/datasets/visualize25/valorant-pro-matches-full-data)
- **Formato de origen:** Base de datos SQLite (`valorant.sqlite`) compuesta por **4 tablas**:
  - `Matches` (7.818 registros, 12 columnas)
  - `Games` (15.888 registros, 36 columnas)
  - `Game_Rounds` (15.531 registros, 4 columnas) — **excluida**
  - `Game_Scoreboard` (157.939 registros, 28 columnas)

## 2. Tablas originales de SQLite

### 2.1. `Matches` (7.818 registros · 12 columnas)

| Columna | Descripción |
| --- | --- |
| `MatchID` | Identificador único del enfrentamiento |
| `Date` | Fecha del enfrentamiento |
| `Patch` | Versión/parche del juego *(excluida en el CSV)* |
| `EventID` | Identificador del torneo *(excluida en el CSV)* |
| `EventName` | Nombre del torneo o evento |
| `EventStage` | Fase del torneo |
| `Team1ID` | Identificador del equipo 1 *(excluida en el CSV)* |
| `Team2ID` | Identificador del equipo 2 *(excluida en el CSV)* |
| `Team1` | Nombre del equipo 1 |
| `Team2` | Nombre del equipo 2 |
| `Team1_MapScore` | Mapas ganados por el equipo 1 |
| `Team2_MapScore` | Mapas ganados por el equipo 2 |

### 2.2. `Games` (15.888 registros · 36 columnas)

Contiene la información de cada mapa jugado dentro de un enfrentamiento:

`GameID`, `MatchID`, `Map`, `Team1ID`, `Team2ID`, `Team1`, `Team2`, `Winner`, `Team1_TotalRounds`, `Team2_TotalRounds`, `Team1_SideFirstHalf`, `Team2_SideFirstHalf`, `Team1_RoundsFirstHalf`, `Team1_RoundsSecondtHalf`, `Team1_RoundsOT`, `Team2_RoundsFirstHalf`, `Team2_RoundsSecondtHalf`, `Team2_RoundsOT`, `Team1_PistolWon`, `Team1_Eco`, `Team1_EcoWon`, `Team1_SemiEco`, `Team1_SemiEcoWon`, `Team1_SemiBuy`, `Team1_SemiBuyWon`, `Team1_FullBuy`, `Team1_FullBuyWon`, `Team2_PistolWon`, `Team2_Eco`, `Team2_EcoWon`, `Team2_SemiEco`, `Team2_SemiEcoWon`, `Team2_SemiBuy`, `Team2_SemiBuyWon`, `Team2_FullBuy`, `Team2_FullBuyWon`.

### 2.3. `Game_Rounds` (15.531 registros · 4 columnas — excluida)

Columnas: `GameID`, `Team1ID`, `Team2ID`, `RoundHistory`. Se excluye del CSV final porque el nivel de granularidad elegido es por jugador y mapa, no ronda a ronda.

### 2.4. `Game_Scoreboard` (157.939 registros · 28 columnas)

`GameID`, `PlayerID`, `PlayerName`, `TeamAbbreviation`, `Agent`, `ACS`, `Kills`, `Deaths`, `Assists`, `PlusMinus`, `KAST_Percent`, `ADR`, `HS_Percent`, `FirstKills`, `FirstDeaths`, `FKFD_PlusMinus`, `Num_2Ks`, `Num_3Ks`, `Num_4Ks`, `Num_5Ks`, `OnevOne`, `OnevTwo`, `OnevThree`, `OnevFour`, `OnevFive`, `Econ`, `Plants`, `Defuses`.

## 3. Esquema final del CSV de Esports-hub

- **Granularidad:** una fila por **jugador y mapa**.
- **Dimensiones:** **157.939 filas** y **25 columnas** (`row_id` secuencial generado en la exportación + 24 campos procedentes de `Matches`, `Games` y `Game_Scoreboard`).

| # | Columna CSV | Tipo | Procedencia | Descripción |
| --- | --- | --- | --- | --- |
| 1 | `row_id` | Entero | Generada en exportación | Identificador secuencial único desde `1` |
| 2 | `match_date` | `TEXT` | `Matches.Date` | Fecha del enfrentamiento |
| 3 | `event_name` | Texto | `Matches.EventName` | Nombre del torneo o evento |
| 4 | `event_stage` | Texto | `Matches.EventStage` | Fase del evento |
| 5 | `team1` | Texto | `Matches.Team1` | Nombre del equipo 1 |
| 6 | `team2` | Texto | `Matches.Team2` | Nombre del equipo 2 |
| 7 | `team1_map_score` | Entero | `Matches.Team1_MapScore` | Mapas ganados por el equipo 1 |
| 8 | `team2_map_score` | Entero | `Matches.Team2_MapScore` | Mapas ganados por el equipo 2 |
| 9 | `map` | Texto | `Games.Map` | Nombre del mapa jugado |
| 10 | `winner` | Texto | `Games.Winner` | Equipo ganador del mapa |
| 11 | `team1_total_rounds` | Entero | `Games.Team1_TotalRounds` | Rondas totales del equipo 1 en el mapa |
| 12 | `team2_total_rounds` | Entero | `Games.Team2_TotalRounds` | Rondas totales del equipo 2 en el mapa |
| 13 | `player_name` | Texto | `Game_Scoreboard.PlayerName` | Nombre del jugador |
| 14 | `player_team` | Texto | `Game_Scoreboard.TeamAbbreviation` | Abreviatura del equipo del jugador |
| 15 | `agent` | Texto | `Game_Scoreboard.Agent` | Agente utilizado en el mapa |
| 16 | `acs` | `INTEGER` | `Game_Scoreboard.ACS` | *Average Combat Score* |
| 17 | `kills` | Entero | `Game_Scoreboard.Kills` | Eliminaciones realizadas |
| 18 | `deaths` | Entero | `Game_Scoreboard.Deaths` | Muertes sufridas |
| 19 | `assists` | Entero | `Game_Scoreboard.Assists` | Asistencias realizadas |
| 20 | `adr` | `INTEGER` | `Game_Scoreboard.ADR` | Daño medio por ronda |
| 21 | `hs_percent` | `REAL` | `Game_Scoreboard.HS_Percent` | Porcentaje de disparos a la cabeza |
| 22 | `first_kills` | Entero | `Game_Scoreboard.FirstKills` | Primeras bajas conseguidas |
| 23 | `first_deaths` | Entero | `Game_Scoreboard.FirstDeaths` | Primeras muertes sufridas |
| 24 | `plants` | Entero | `Game_Scoreboard.Plants` | Veces que plantó la *Spike* |
| 25 | `defuses` | Entero | `Game_Scoreboard.Defuses` | Veces que desactivó la *Spike* |

## 4. Criterios de selección y exclusión

- **Excluidas:**
  - Tabla `Game_Rounds` completa (detalle ronda a ronda).
  - `Patch` de `Matches`.
  - Columnas de economía y desglose por mitades/rondas de `Games` (`Team1_Eco`, `Team1_FullBuy`, `Team1_RoundsFirstHalf`, etc.) y `Econ` de `Game_Scoreboard`.
  - Estadísticas derivadas o de detalle granular: multi-kills (`Num_2Ks`..`Num_5Ks`), *clutches* (`OnevOne`..`OnevFive`), `KAST_Percent`, `PlusMinus` y `FKFD_PlusMinus`.
  - Identificadores internos originales (`PlayerID`, `EventID`, `Team1ID`, `Team2ID`, `MatchID` y `GameID` no se exportan al CSV; `MatchID` y `GameID` solo se utilizan para los `JOIN`).
- **Tratamiento de nulos y ordenación:**
  - Los valores nulos se conservan como **celdas vacías** (no se sustituyen automáticamente por `0`).
  - El dataset se ordena por **fecha descendente** (`Matches.Date DESC`).

## 5. Proceso técnico de generación del CSV (7 pasos)

1. **Preparación:** situar el fichero `valorant.sqlite` junto al script Python de exportación.
2. **Conexión y lectura:** abrir la base de datos SQLite con `sqlite3` y ejecutar la consulta mediante `pandas`.
3. **Unión de tablas (`INNER JOIN`):** combinar `Game_Scoreboard` con `Games` mediante `GameID`, y con `Matches` mediante `MatchID`.
4. **Selección y normalización:** proyectar las 24 columnas seleccionadas y renombrarlas a `snake_case` homogéneo.
5. **Generación de `row_id`:** asignar un identificador entero secuencial empezando en `1` tras la ordenación.
6. **Ordenación y exportación:** ordenar de forma descendente por fecha y exportar con `df.to_csv(..., index=False, encoding="utf-8-sig")`.
7. **Validación final:** comprobar que el CSV resultante tiene exactamente **25 columnas**, `row_id` único y conserva los **157.939 registros** sin pérdida ni duplicación.

## 6. Consulta SQL utilizada

```sql
SELECT
    m.Date AS match_date,
    m.EventName AS event_name,
    m.EventStage AS event_stage,
    m.Team1 AS team1,
    m.Team2 AS team2,
    m.Team1_MapScore AS team1_map_score,
    m.Team2_MapScore AS team2_map_score,
    g.Map AS map,
    g.Winner AS winner,
    g.Team1_TotalRounds AS team1_total_rounds,
    g.Team2_TotalRounds AS team2_total_rounds,
    s.PlayerName AS player_name,
    s.TeamAbbreviation AS player_team,
    s.Agent AS agent,
    s.ACS AS acs,
    s.Kills AS kills,
    s.Deaths AS deaths,
    s.Assists AS assists,
    s.ADR AS adr,
    s.HS_Percent AS hs_percent,
    s.FirstKills AS first_kills,
    s.FirstDeaths AS first_deaths,
    s.Plants AS plants,
    s.Defuses AS defuses
FROM Game_Scoreboard AS s
INNER JOIN Games AS g ON s.GameID = g.GameID
INNER JOIN Matches AS m ON g.MatchID = m.MatchID
ORDER BY m.Date DESC, m.MatchID, g.GameID, s.TeamAbbreviation, s.PlayerName;
```

## 7. Resultado y observaciones

- **Total de registros:** `157.939` filas.
- **Total de columnas:** `25` columnas (`row_id` + 24 campos de dominio).
- **Codificación:** `UTF-8` con BOM (`utf-8-sig`) para compatibilidad directa con herramientas de análisis y hojas de cálculo.
- **Integridad de nulos:** los valores ausentes en origen permanecen vacíos en el CSV y no se rellenan con ceros artificiales.
