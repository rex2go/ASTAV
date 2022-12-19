cache = {
    "context": {},
    "fns": {}
}


def load_context(context):
    cache["context"] = context


def load_fns(fns):
    cache["fns"] = fns


def resolve(ref):
    if ref[0] == "~":
        ref = cache["context"][ref[1:]]

    return ref
