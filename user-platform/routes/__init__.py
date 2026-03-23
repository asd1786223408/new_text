# 路由层
from .auth import auth_bp
from .users import users_bp
from .departments import departments_bp
from .roles import roles_bp
from .permissions import permissions_bp
from .resumes import resumes_bp
from .positions import positions_bp
from .demands import demands_bp

__all__ = ['auth_bp', 'users_bp', 'departments_bp', 'roles_bp', 'permissions_bp', 'resumes_bp', 'positions_bp', 'demands_bp']
