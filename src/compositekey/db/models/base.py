__author__ = 'aldaran'

def wrap_init_model(original_init):
    if hasattr(original_init, "_sign"):
        return original_init

    def __init__(obj, *args, **kwargs):
        if len(args)<len(obj._meta.fields):
            for value, f in zip(args, [f for f in obj._meta.fields if not getattr(f, "not_in_db", False)]):
                kwargs.update({f.attname:value})
            args = []

        original_init(obj, *args, **kwargs)

        # setup pk cache
        obj.pk
    __init__._sign = "composite"
    return __init__
