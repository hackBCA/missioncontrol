from flask import Blueprint

admin_module = Blueprint(
<<<<<<< a4e6595f733ca0d93b9697f5eb03117982533f41
    "admin",
    __name__,
    url_prefix = "",
    template_folder = "templates",
    static_folder = "static"
)

from . import views
=======
	"admin",
	__name__,
	url_prefix = "",
	template_folder = "templates",
	static_folder = "static"
)

from . import views
>>>>>>> Adding, editing, and deleting a staff member from the database are all implemented.
