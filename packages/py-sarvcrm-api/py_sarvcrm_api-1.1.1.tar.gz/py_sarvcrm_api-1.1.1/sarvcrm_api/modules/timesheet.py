from ._base import SarvModule
from ._mixins import UrlMixin

class Timesheet(SarvModule, UrlMixin):
    _module_name = 'Timesheet'
    _label_en = 'Timesheet'
    _label_pr = 'تایم شیت'