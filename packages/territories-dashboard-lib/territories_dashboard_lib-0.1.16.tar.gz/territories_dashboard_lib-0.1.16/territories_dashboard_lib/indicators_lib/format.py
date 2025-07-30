def _get_precision(value, force_integer):
    return f"{value:.0f}" if force_integer else f"{value:.1f}"


def _remove_useless_0(value):
    if "." in value:
        value = value.rstrip("0").rstrip(".")
    return value


def format_indicator_value(value, force_integer=False):
    if value is None:
        return "-"

    abs_value = abs(value)

    if abs_value > 999999:
        nb = _remove_useless_0(_get_precision((value / 1_000_000), force_integer)) + "M"
    elif abs_value > 999:
        nb = _remove_useless_0(_get_precision((value / 1_000), force_integer)) + "k"

    else:
        nb = _remove_useless_0(_get_precision(value, force_integer))
    return nb.replace(".", ",")


def _format_value(k, v):
    if k.lower().startswith("valeur"):
        v = format_indicator_value(v)
    return v


def format_data(data):
    return {k: _format_value(k, v) for k, v in data.items()}
