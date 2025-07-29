# ----------------------------------------------------------------------------------------
# Python-Backpack - Pattern Utilities
# Maximiliano Rocamora / maxirocamora@gmail.com
# https://github.com/MaxRocamora/python-backpack
# ----------------------------------------------------------------------------------------


class Singleton:
    """Python Singleton BaseClass.

    Usage:

        class MyClass(Singleton, otherClass):
            pass

        obj = MyClass() # any new object will be taken from the same instance

    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton __new__ method."""
        if not isinstance(cls._instance, cls):
            # print(f'Initializing {cls.__name__}')
            cls._instance = object.__new__(cls)
        # print(f'Restoring {class_.__name__}')
        return cls._instance
