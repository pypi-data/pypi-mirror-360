from typing import Any

import wtforms
from flask_babel import lazy_gettext

import hawat.forms


class SimplePivotSearchForm(hawat.forms.EventSearchFormBase):
    """
    Class representing simple event pivot search form.
    """

    row_agg_column = wtforms.SelectField(
        lazy_gettext("Row aggregation:"),
        validators=[wtforms.validators.DataRequired()],
        description=lazy_gettext("The category by which the events will be grouped in the rows of the pivot table."),
    )
    col_agg_column = wtforms.SelectField(
        lazy_gettext("Column aggregation:"),
        validators=[wtforms.validators.DataRequired()],
        description=lazy_gettext("The category by which the events will be grouped in the columns of the pivot table."),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.row_agg_column.choices = [("", lazy_gettext("Nothing selected"))] + kwargs["choices_agg_columns"]
        self.col_agg_column.choices = [("", lazy_gettext("Nothing selected"))] + kwargs["choices_agg_columns"]
