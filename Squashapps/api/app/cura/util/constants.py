def constant(f):

    def fset(self, value):
        raise TypeError

    def fget(self):
        return f()
    return property(fget, fset)


class _Const(object):
    @constant
    def INVALID_USER():
        return 1111

    @constant
    def INVAILD_ROLE():
        return 1112


class _ErrorCode(object):
    @constant
    def SUCESS():
        return 9999


CONST = _Const()