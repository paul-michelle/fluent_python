import abc


class Validator(abc.ABC):

    def __set_name__(self, owner, name):
        self.storage_name = name

    def __set__(self, instance, value):
        value = self.validate(self.storage_name, value)
        instance.__dict__[self.storage_name] = value

    @abc.abstractmethod
    def validate(self, name, value):
        pass


class Quantity(Validator):

    def validate(self, name, value):
        if value <= 0:
            raise ValueError(f'{name} must be > 0')
        return value


class NonBlank(Validator):

    def validate(self, name, value):
        value = value.strip()
        if not len(value):
            raise ValueError(f'{name} cannot be blank')
        return value

