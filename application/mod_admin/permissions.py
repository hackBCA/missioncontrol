from flask.ext.principal import Principal, Permission, RoleNeed

roles = [
    "admin", 
    "director",
    "board", 
    "review_apps",
    "read_data", 
    "staff",
    "sms_blast",
    "check_in",
    "paths"
]

class permissions:
  def __init__(self, roles):    
    for role in roles:
        setattr(self, role, Permission(RoleNeed(role)))

sentinel = permissions(roles)