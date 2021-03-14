
########################################################################
class Dict2Obj(object):
    """
    Turns a dictionary into a class
    """

    # ----------------------------------------------------------------------
    def __init__(self, dictionary):
        """Constructor"""
        for key in dictionary:
            setattr(self, key, dictionary[key])

    # ----------------------------------------------------------------------
    def __repr__(self):
        """"""
        attrs = str([x for x in self.__dict__])
        return "<dict2obj: %s="">" % attrs