class NonBlankField:

    def __init__(self):
        self._storage_name = None

    def __set__(self, instance, value):
        if not isinstance(value, str):
            raise TypeError(f'{self._storage_name} should be of type <str>')
        if not len(value):
            raise ValueError(f'{self._storage_name} cannot be an empty string')
        instance.__dict__[self._storage_name] = value


class ModelMeta(type):

    def __init__(cls, name, bases, dict_):
        super().__init__(name, bases, dict_)

        for key, attr in dict_.items():
            if isinstance(attr, NonBlankField):
                attr._storage_name = key
