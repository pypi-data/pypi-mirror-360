from ._base import SarvModule
from ._mixins import UrlMixin

class ScContract(SarvModule, UrlMixin):
    _module_name = 'sc_Contract'
    _label_en = 'Support Contracts'
    _label_pr = 'قراردادهای پشتیبانی'