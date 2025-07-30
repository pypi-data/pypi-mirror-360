from ._base import SarvModule
from ._mixins import UrlMixin

class AosProducts(SarvModule, UrlMixin):
    _module_name = 'AOS_Products'
    _label_en = 'Products'
    _label_pr = 'محصولات'