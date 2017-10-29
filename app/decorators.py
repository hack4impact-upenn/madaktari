from functools import wraps

from flask import abort
from flask_login import current_user

from .models import Permission


def permission_required(permission):
    """Restrict a view to users with the given permission."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator

def role_required(role):
    """Restrict a view to users with the given role."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_role(role):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)

def applicant_required(f):
    return role_required('applicant')

def rejected_required(f):
    return role_required('rejected')

def pending_required(f):
    return role_required('pending')

def accepted_required(f):
    return role_required('accepted')
