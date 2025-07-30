"""List instance attributes

Use this as a mix-in class to equip other classes with a representation of all instance attributes
(set via a constructor or otherwise).
"""

class LsAttr:

    def __lsattr(self):
        return ', '.join(f'{attr}={self.__dict__[attr]!r}' for attr in sorted(self.__dict__))

    def __repr__(self):
        return f'{self.__class__.__name__}({self.__lsattr()})'
