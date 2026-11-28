from flask_wtf import FlaskForm
from wtforms import SubmitField


class EsportsForm(FlaskForm):
    submit = SubmitField("Save esports")
