class Helpers:
    @staticmethod
    def maybe(func, obj):
        return None if obj is None else func(obj)
