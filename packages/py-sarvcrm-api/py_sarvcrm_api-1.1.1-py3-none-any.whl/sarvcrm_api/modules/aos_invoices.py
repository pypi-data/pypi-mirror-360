from ._base import SarvModule
from ._mixins import UrlMixin

class AosInvoices(SarvModule, UrlMixin):
    _module_name = 'AOS_Invoices'
    _label_en = 'Invoices'
    _label_pr = 'فاکتورها'