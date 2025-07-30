import logging
import re
from functools import wraps
from types import FunctionType
from typing import List

import requests

from confluence_cli.cli.types import Page, Space, Comment, BlogPost, StaticMethodType, ClassMethodType, NavigableDict, \
    User, Attachment

logger = logging.getLogger("confluence_log")


def type_wrap(content):
    """ Wrap content in a type

    :param content:   The content to wrap    
    :return:          The wrapped content    
    """
    if content is None:
        return None

    types = {
        "page": Page,
        "global": Space,
        "blogpost": BlogPost,
        "attachment": Attachment,
        "comment": Comment,
        "workflowName": NavigableDict,
        "userKey": User,
    }
    content_type = content.get("type")
    if content_type in types:
        return types[content_type](content, default_box=True, default_box_attr=None, box_dots=True)
    else:
        return content


def secure_call_func(f):
    # static call
    if type(f) == StaticMethodType:
        return f.__func__
    else:
        return f


def type_wrap_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = type_wrap(secure_call_func(func)(*args, **kwargs))
        return result

    return wrapper


def requests_error_handling(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return secure_call_func(func)(*args, **kwargs)
        except requests.exceptions.ConnectionError as e:
            logger.critical(f"Connection Error: {e.args[0].args[0]}")
        except requests.exceptions.Timeout as e:
            logger.critical(f"Time Out: {e.args[0].args[0]}")

    return wrapper


def base_methods_decorator(deco, regex: str, base_class=None):
    """Class decorator that copies and decorates all matching methods of the base_class in the decorated class"""

    def f(c: type):
        nonlocal base_class
        ## decorated class is the defautl base_class
        if not base_class:
            base_class = c
        avoid_functions: List[str] = ["__init__"]

        def lmd(i):
            return i[0] not in avoid_functions and re.fullmatch(regex, i[0])

        funcs = list(filter(lmd, base_class.__dict__.items()))
        for func in funcs:
            if type(func[1]) == FunctionType:
                setattr(c, func[0], deco(func[1]))
            elif type(func[1]) == StaticMethodType:
                setattr(c, func[0], staticmethod(deco(func[1])))
            elif type(func[1]) == ClassMethodType:
                setattr(c, func[0], classmethod(deco(func[1])))
        return c

    return f
