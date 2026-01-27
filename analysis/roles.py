ROLES = {
    "viewer": ["read"],
    "analyst": ["read", "analyze"],
    "lead": ["read", "analyze", "export"]
}

def check_permission(role, action):
    return action in ROLES.get(role, [])
