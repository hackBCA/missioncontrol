from flask import Blueprint

web_module = Blueprint(
    "web",
    __name__,
    url_prefix = "",
    template_folder = "templates",
    static_folder = "static"
)

from . import views
