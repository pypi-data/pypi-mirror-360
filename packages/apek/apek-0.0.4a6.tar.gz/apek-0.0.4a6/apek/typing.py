# -*- coding: utf-8 -*-
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring



import time as _time



class BuiltIn(object):
    NoneType = type(None)
    NotImplementedType = type(NotImplemented)
    builtin_function_or_method = type(print)
    function = type(lambda: None)



class ApekRoot(object):
    def __init__(self, *_0, **_1):
        self._createdTime = str(round(_time.time(), 4))
        self._classNameOfSelf = f"{__name__}.{type(self).__name__}"
    
    def __repr__(self):
        return f"<class {self._classNameOfSelf} created at {self._createdTime}>"
    
    def __bool__(self):
        return True



class Object(ApekRoot):
    pass

class Number(ApekRoot):
    pass



class Null(Object):
    def __repr__(self):
        return f"<class {self._classNameOfSelf}>"
    
    def __bool__(self):
        return False
