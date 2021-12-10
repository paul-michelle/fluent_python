from typing import Union


def cls_name(inst_or_cls: Union[object, type]) -> str:
    cls = type(inst_or_cls) if type(inst_or_cls) is not type else inst_or_cls
    return cls.__name__


def display(obj: Union[object, type]):
    cls = type(obj)
    if cls is type:
        return f'<class {obj.__name__}>'
    if cls in (type(None), int):
        return repr(obj)
    return f'<{cls_name(obj)} object>'


def print_args(name, *args):
    pseudo_args = ', '.join(display(arg) for arg in args)
    print(f'-->> cls_name: {cls_name(args[0])};  name: {name};  pseudo_args:{pseudo_args}')


class Overriding:
    """a.k.a. data descriptor or enforced descriptor"""

    def __get__(self, instance, owner):
        print_args('dunder get', self, instance, owner)

    def __set__(self, instance, value):
        print_args('dunder set', self, instance, value)


class OverridingWithoutGet:

    def __set__(self, instance, value):
        print_args('dunder set', self, instance, value)


class NonOverriding:
    """a.k.a. non-data descriptor or shadowable descriptor"""

    def __get__(self, instance, owner):
        print_args('dunder get', self, instance, owner)


class SomeManagedClass:

    over = Overriding()
    over_no_get = OverridingWithoutGet()
    non_over = NonOverriding()

    def spam(self):
        print(f'-->> Managed.spam({display(self)})')
