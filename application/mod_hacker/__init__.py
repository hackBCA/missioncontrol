from flask import Blueprint

hacker_module = Blueprint(
    "hacker",
    __name__,
    url_prefix = "",
    template_folder = "templates",
    static_folder = "static"
)

from . import views
