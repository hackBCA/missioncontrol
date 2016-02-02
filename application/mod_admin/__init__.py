from flask import Blueprint

admin_module = Blueprint(
	"admin",
	__name__,
	url_prefix = "",
	template_folder = "templates",
	static_folder = "static"
)

from . import views