from difflib import SequenceMatcher


def similar(a: str, b: str) -> float:
    """:cvar
    A function that returns a float from 0 to 1 that represents how similar 2 strings are
    """
    return SequenceMatcher(None, a, b).ratio()
