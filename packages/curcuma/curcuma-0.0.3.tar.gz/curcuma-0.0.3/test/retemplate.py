t = {"a": {"b": 1}, "c": ["z", "x", "y"]}

params = {"name": "test", "a.b": 23, "c.2": "bla"}


def quote_if_string(value):
    return value if isinstance(value, int) or value.isdigit() else f"'{value}'"


for param in params:
    exec(
        f"t[{"][".join(quote_if_string(p) for p in param.split("."))}] = {quote_if_string(params[param])}"
    )

print(t)
