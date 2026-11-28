from sqlalchemy.orm import declared_attr

from app import db
from app.features.dataset.models import BaseDataset

CSV_DELIMITER = ";"

CSV_COLUMNS = (
    "row_id",
    "match_date",
    "event_name",
    "event_stage",
    "team1",
    "team2",
    "team1_map_score",
    "team2_map_score",
    "map",
    "winner",
    "team1_total_rounds",
    "team2_total_rounds",
    "player_name",
    "player_team",
    "agent",
    "acs",
    "kills",
    "deaths",
    "assists",
    "adr",
    "hs_percent",
    "first_kills",
    "first_deaths",
    "plants",
    "defuses",
)

_INTEGER_COLUMNS = frozenset(
    {
        "row_id",
        "team1_map_score",
        "team2_map_score",
        "team1_total_rounds",
        "team2_total_rounds",
        "acs",
        "kills",
        "deaths",
        "assists",
        "adr",
        "first_kills",
        "first_deaths",
        "plants",
        "defuses",
    }
)

_FLOAT_COLUMNS = frozenset({"hs_percent"})


class EsportsDataset(BaseDataset):
    """Dataset de partidos de Esports en formato CSV (dominio Valorant, DEC-001).

    Hereda de ``BaseDataset`` y recoge las 25 columnas del esquema CSV definido
    en ``docs/dataset-valorant.md``, además del juego (``Valorant`` por defecto).
    """

    __tablename__ = "esports_dataset"

    @declared_attr
    def ds_meta_data(cls):
        return db.relationship("DSMetaData", backref=db.backref("esports_dataset", uselist=False))

    game = db.Column(db.String(64), nullable=False, default="Valorant")

    # ── Columnas del CSV de partidos (docs/dataset-valorant.md) ─────────
    row_id = db.Column(db.Integer, nullable=True)
    match_date = db.Column(db.String(64), nullable=True)
    event_name = db.Column(db.String(255), nullable=True)
    event_stage = db.Column(db.String(255), nullable=True)
    team1 = db.Column(db.String(120), nullable=True)
    team2 = db.Column(db.String(120), nullable=True)
    team1_map_score = db.Column(db.Integer, nullable=True)
    team2_map_score = db.Column(db.Integer, nullable=True)
    map = db.Column(db.String(120), nullable=True)
    winner = db.Column(db.String(120), nullable=True)
    team1_total_rounds = db.Column(db.Integer, nullable=True)
    team2_total_rounds = db.Column(db.Integer, nullable=True)
    player_name = db.Column(db.String(120), nullable=True)
    player_team = db.Column(db.String(64), nullable=True)
    agent = db.Column(db.String(64), nullable=True)
    acs = db.Column(db.Integer, nullable=True)
    kills = db.Column(db.Integer, nullable=True)
    deaths = db.Column(db.Integer, nullable=True)
    assists = db.Column(db.Integer, nullable=True)
    adr = db.Column(db.Integer, nullable=True)
    hs_percent = db.Column(db.Float, nullable=True)
    first_kills = db.Column(db.Integer, nullable=True)
    first_deaths = db.Column(db.Integer, nullable=True)
    plants = db.Column(db.Integer, nullable=True)
    defuses = db.Column(db.Integer, nullable=True)

    def __init__(self, **kwargs):
        csv_files = kwargs.pop("csv_files", None)
        kwargs.setdefault("game", "Valorant")
        super().__init__(**kwargs)
        self.csv_files = list(csv_files) if csv_files is not None else []

    def files(self):
        """Ficheros CSV asociados al dataset."""
        return list(getattr(self, "csv_files", None) or [])

    @classmethod
    def parse_csv_row(cls, row: dict) -> dict:
        """Convierte una fila leída de un CSV a los tipos del modelo.

        Las celdas vacías se conservan como ``None`` (sin sustituirlas por ``0``),
        tal como especifica ``docs/dataset-valorant.md``.
        """
        parsed = {}
        for column in CSV_COLUMNS:
            raw_value = row.get(column)
            if raw_value is None or (isinstance(raw_value, str) and raw_value.strip() == ""):
                parsed[column] = None
            elif column in _INTEGER_COLUMNS:
                parsed[column] = int(raw_value)
            elif column in _FLOAT_COLUMNS:
                parsed[column] = float(raw_value)
            else:
                parsed[column] = str(raw_value).strip()
        return parsed

    @classmethod
    def from_csv_row(cls, row: dict, **kwargs) -> "EsportsDataset":
        """Construye una instancia de ``EsportsDataset`` a partir de una fila del CSV."""
        data = cls.parse_csv_row(row)
        data.update(kwargs)
        return cls(**data)

    def csv_fields_to_dict(self) -> dict:
        """Devuelve un diccionario con los 25 campos del CSV de partidos."""
        return {column: getattr(self, column) for column in CSV_COLUMNS}

    def __repr__(self):
        return f"EsportsDataset<{self.id}>"


Esports = EsportsDataset
