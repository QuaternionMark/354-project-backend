from functools import wraps, update_wrapper
from flask import g, session, make_response
from flaskr.models.User import User
from flaskr.db import session_scope

def not_login(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            return {
                'code': 400,
                'message': 'Forbidden Access'
            }, 400
        return func(*args, **kwargs)
    return decorated_function

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            with session_scope() as db_session:
                # Not the most efficient way if the demand is there we could always include a redis/memcache server.
                query = db_session.query(User).filter_by(id=session.get('user_id'))
                if query.count() == 1:
                    g.user = query.one()
                else:
                    session.pop('user_id')
                    return {
                        'code': 400,
                        'message': 'Unauthorized Access'
                    }, 400
        else:
            return {
                'code': 400,
                'message': 'Unauthorized Access'
            }, 400

        return func(*args, **kwargs)
    return decorated_function

def cross_origin(origin="*", methods=["GET", "PUT", "POST", "DELETE"], headers=["Origin", "X-Requested-With", "Content-Type", "Accept"]):
    def _cross_origin_factory(func):
        def _cross_origin(*args, **kwargs):
            response = make_response(func(*args, **kwargs))
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Headers"] = ", ".join(headers)
            response.headers["Access-Control-Allow-Methods"] = ", ".join(methods)

            return response
        return update_wrapper(_cross_origin, func)
    return _cross_origin_factory