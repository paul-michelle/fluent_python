class NonBlank:

    def __init__(self):
        self._storage_name = None

    def __set__(self, instance, value):
        if not isinstance(value, str):
            raise TypeError(f'{self._storage_name} should be of type <str>')
        if not len(value):
            raise ValueError(f'{self._storage_name} cannot be an empty string')
        instance.__dict__[self._storage_name] = value


def named_fields(kls):
    for key, attr in kls.__dict__.items():
        if isinstance(attr, NonBlank):
            attr._storage_name = key
    return kls
