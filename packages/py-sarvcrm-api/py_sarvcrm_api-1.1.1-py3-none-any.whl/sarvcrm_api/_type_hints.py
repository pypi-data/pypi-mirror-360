from typing import Literal, TypeAlias

TimeOutput: TypeAlias = Literal['date', 'datetime', 'time']
RequestMethod: TypeAlias = Literal['GET','POST','PUT','DELETE']
SarvLanguageType: TypeAlias = Literal['fa_IR','en_US']
SarvGetMethods: TypeAlias = Literal[
    'Login',
    'Save',
    'Retrieve',
    'GetModuleFields',
    'GetRelationship',
    'SaveRelationships',
    'SearchByNumber',
]

__all__ = [
    'TimeOutput',
    'RequestMethod',
    'SarvLanguageType',
    'SarvGetMethods',
]