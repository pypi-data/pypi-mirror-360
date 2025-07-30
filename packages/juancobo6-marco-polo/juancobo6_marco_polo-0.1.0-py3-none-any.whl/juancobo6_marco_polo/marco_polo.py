"""Marco Polo game."""

import pandas as pd


def marco_polo(name: str) -> str | None:
    """Returns "Polo" if the name is "Marco", otherwise returns None.

    Args:
        name (str): The name to check.

    Returns:
        str | None: "Polo" if the name is "Marco", otherwise None.
    """
    _ = pd.DataFrame()

    if name == "Marco":
        return "Polo"
    return None
