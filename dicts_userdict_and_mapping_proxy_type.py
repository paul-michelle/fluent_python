"""Benefiting from all the dict methods plus classical mapping.
'Freezing' the dict with MappingProxyType.


__missing__ will be called by the getitem dunder method.
Here is its implementation in UserDict

def __getitem__(self, key):
    if key in self.data:
        return self.data[key]
    if hasattr(self.__class__, "__missing__"):
        return self.__class__.__missing__(self, key)
    raise KeyError(key)


This way the customized dict will hold all keys as str, as
well as treat int keys and str.
"""

from collections import UserDict
from types import MappingProxyType
from dis import dis


class StrKeyDict(UserDict):

    def __contains__(self, key):
        return self[str(key)] in self.data

    def __missing__(self, key):
        if isinstance(key, str):
            raise KeyError(key)
        return self[str(key)]

    def __setitem__(self, key, value):
        self.data[str(key)] = value


if __name__ == '__main__':

    new_dict = StrKeyDict()
    new_dict['1'] = 'stand'
    new_dict['2'] = 'alone'
    print(new_dict[1], end=' ')
    print(new_dict[2])

    frozen_new_dict = MappingProxyType(new_dict)
    print(
        new_dict[1] == frozen_new_dict[1] and new_dict[2] == frozen_new_dict[2]
    )

    try:
        frozen_new_dict['3'] = '... all alone'
    except TypeError as e:
        print(str(e) == "'mappingproxy' object does not support item assignment")

    new_dict['3'] = '... the dict itself still can be changed'
    if frozen_new_dict[3] == new_dict[3]:
        print('And the frozen dict will dynamically adjust to the initial dict ...')

    print(
        dis(
        "new_dict['3'] = '... the dict itself still can be changed'"
        )
    )
