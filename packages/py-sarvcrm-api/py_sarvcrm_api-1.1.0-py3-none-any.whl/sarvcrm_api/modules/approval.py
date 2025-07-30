from ._base import SarvModule
from ._mixins import UrlMixin

class Approval(SarvModule, UrlMixin):
    _module_name = 'Approval'
    _label_en = 'Approval'
    _label_pr = 'تاییدیه'