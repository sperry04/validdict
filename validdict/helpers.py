## Logging/Formatting Helpers

from __future__ import annotations

def format_sequence(seq:tuple|list, separator:str=", ", quote:str="'", prefix:str="", suffix:str="") -> str:
    """
    formats a sequence (list or tuple) for printing as a delimited string with prefix/suffix when there are multiple items
    """
    if isinstance(seq, (tuple, list)):
        if len(seq) == 1:
            rval = format_sequence(seq[0], separator, quote)
        else:
            rval = (prefix + separator.join(format_sequence(i, separator, quote) for i in seq) + suffix)
    elif isinstance(seq, str):
        rval = quote + seq + quote
    elif hasattr(seq, "__name__"):
        rval = quote + seq.__name__ + quote
    else:
        rval = quote + repr(seq).strip(quote) + quote
    return rval


def path_padding(path, padding:str="  ", offset:int=0) -> str:
    """
    returns a padding string for indenting based on the number of items in a path list
    """
    return "" if (path is None or padding is None) else padding * (len(path) + offset)


def format_path(path:list[str]=None, prefix:str="", suffix:str="", padding:str="  ", padding_offset:int=0) -> str:
    """
    formats a result path for printing as a dot-delimited string
    """
    if isinstance(path, list) and len(path) > 0:
        return path_padding(path, padding, padding_offset) + prefix + ".".join(path) + suffix
    return ""


def extend_path(path:list[str]=None, key:str=None) -> list[str]:
    """
    adds key to the end of path, handling Nones
    """
    if path is None and key is None:
        return None
    if path is None:
        return [key]
    rval = path.copy()
    if key is None:
        return rval
    rval.append(key)
    return rval
