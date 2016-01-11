from flask import Blueprint

user_module = Blueprint(
    "user",
    __name__,
    url_prefix = "",
    template_folder = "templates",
    static_folder = "static"
)

from . import views
