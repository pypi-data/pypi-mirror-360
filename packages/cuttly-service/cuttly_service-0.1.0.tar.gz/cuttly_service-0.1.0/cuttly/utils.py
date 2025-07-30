from enum import Enum


class SetMobileRedirectEnum(str, Enum):
    android = "android"
    ios = "ios"
    windows_mobile = "windowsMobile"
    redirect = "redirect"