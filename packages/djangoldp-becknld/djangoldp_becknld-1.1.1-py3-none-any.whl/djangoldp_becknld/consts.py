from django.conf import settings

IS_BAP = getattr(settings, "BECKNLD_BAP̈_ENV", False)
IS_BPP = getattr(settings, "BECKNLD_BPP̈_ENV", False)

BAP_URI = (
    getattr(settings, "BASE_URL", None)
    if IS_BAP
    else getattr(settings, "BECKNLD_BAP_URI", None)
)
if BAP_URI and BAP_URI[-1] != "/":
    BAP_URI += "/"

BPP_URI = (
    getattr(settings, "BASE_URL", None)
    if IS_BPP
    else getattr(settings, "BECKNLD_BPP_URI", None)
)
if BPP_URI and BPP_URI[-1] != "/":
    BPP_URI += "/"
