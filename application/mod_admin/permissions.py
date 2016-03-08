from flask.ext.principal import Principal, Permission, RoleNeed

roles = [
"admin", 
"board", 
"review_apps",
"user_data",
"organizer", 
"volunteer"
]

class permissions:
  def __init__(self, roles):    
    for role in roles:
      setattr(self, role, Permission(RoleNeed(role)))

sentinel = permissions(roles)