from ._base import SarvModule
from ._mixins import UrlMixin

class AosContracts(SarvModule, UrlMixin):
    _module_name = 'AOS_Contracts'
    _label_en = 'Sales Contract'
    _label_pr = 'قراردادهای فروش'