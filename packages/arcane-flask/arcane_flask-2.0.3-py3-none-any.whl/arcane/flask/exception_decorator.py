import functools
from typing import Callable
from flask import request

from .authentication import get_user_email
from flask_log_request_id import current_request_id

def catch_exceptions_service(service: str, auth_enabled=True) -> Callable:
    """ Catch if an exception is raised after an endpoint call and alert it with arguments or parameters (pubsub case)
        passed to this endpoint
    """
    def catch_exceptions(job_func: Callable) -> Callable:
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except Exception as e:
                message = f"Error while executing method {job_func.__name__} in service {service} "
                try:
                    message += f' for user {get_user_email(auth_enabled=auth_enabled)} '
                except ValueError:
                    pass

                request_id = None
                try:
                    request_id = current_request_id()
                except KeyError:
                    pass
                message += f"with request id {request_id}."

                message += f"Args : {str(args)} / kwargs : {str(kwargs)} / headers : {request.environ.get('HTTP_ORIGIN')}"

                print(message)
                raise e
        return wrapper
    return catch_exceptions


def add_id_to_exceptions() -> Callable:
    """ Catch if an exception is raised after an endpoint call and add the request id
    """
    def catch_exceptions(job_func: Callable) -> Callable:
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except Exception as e:
                request_id = None
                import sys
                try:
                    request_id = current_request_id()
                except KeyError:
                    pass
                raise Exception(f"[{request_id}]: {str(e)}").with_traceback(sys.exc_info()[2]) from e
        return wrapper
    return catch_exceptions
