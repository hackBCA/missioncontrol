from flask import Blueprint

stats_module = Blueprint(
    "stats",
    __name__,
    url_prefix = "",
    template_folder = "templates",
    static_folder = "static"
)

from . import views
