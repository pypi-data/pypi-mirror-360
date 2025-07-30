import unicodedata
from .config import load_config

def canonical_name(first, last):
    def norm(s):
        return unicodedata.normalize("NFKC", s.strip().lower())
    return f"{norm(last)} {norm(first)}"


def is_excluded(name, exclude_list):
    return name.strip() in exclude_list


def sortable_name(fullname):
    parts = fullname.split()
    if len(parts) > 1 and parts[0].lower() in {"de", "von", "van", "di", "la", "le"}:
        return " ".join(parts[1:]).lower()
    return fullname.lower()


def overwrite_module(reason,module,config):
    special_modules=config.get("special_modules", {})
    praktikum_modules=config.get("praktikum_modules", {})
    if reason in special_modules.keys():
        return special_modules[reason]['module'],special_modules[reason]['reason']
    elif reason == praktikum_modules['basename']:
        if module in praktikum_modules['as_is']:
            return module,""
        else:
            return reason,""
    else:
        return module,""
