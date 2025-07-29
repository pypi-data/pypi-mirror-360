"""Provides a set of color palettes and functions to generate colors.

The colors are primarily designed for use in matplotlib plots
for Australian states and territories and major political parties.

It also provides Australian state names and their abbreviations.
"""

# --- Imports
from collections.abc import Iterable


# --- Functions
def get_party_palette(party_text: str) -> str:
    """Return a matplotlib color-map name based on party_text.

    Works for Australian major political parties.

    Args:
        party_text: str - the party label or name.

    """
    # Note: light to dark maps work best
    match party_text.lower():
        case "alp" | "labor":
            return "Reds"
        case "l/np" | "coalition":
            return "Blues"
        case "grn" | "green" | "greens":
            return "Greens"
        case "oth" | "other":
            return "YlOrBr"
        case "onp" | "one nation":
            return "YlGnBu"
    return "Purples"


def get_color(s: str) -> str:
    """Return a matplotlib color for a party label or an Australian state/territory.

    Args:
        s: str - the party label or Australian state/territory name.

    Returns a color string that can be used in matplotlib plots.

    """
    color_map = {
        # --- Australian states and territories
        ("wa", "western australia"): "gold",
        ("sa", "south australia"): "red",
        ("nt", "northern territory"): "#CC7722",  # ochre
        ("nsw", "new south wales"): "deepskyblue",
        ("act", "australian capital territory"): "blue",
        ("vic", "victoria"): "navy",
        ("tas", "tasmania"): "seagreen",  # bottle green #006A4E?
        ("qld", "queensland"): "#c32148",  # a lighter maroon
        ("australia", "aus"): "grey",
        # --- political parties
        ("dissatisfied",): "darkorange",  # must be before satisfied
        ("satisfied",): "mediumblue",
        (
            "lnp",
            "l/np",
            "liberal",
            "liberals",
            "coalition",
            "dutton",
            "ley",
            "liberal and/or nationals",
        ): "royalblue",
        (
            "nat",
            "nats",
            "national",
            "nationals",
        ): "forestgreen",
        (
            "alp",
            "labor",
            "albanese",
        ): "#dd0000",
        (
            "grn",
            "green",
            "greens",
        ): "limegreen",
        (
            "other",
            "oth",
        ): "darkorange",
    }

    for find_me, return_me in color_map.items():
        if any(x == s.lower() for x in find_me):
            return return_me

    return "darkgrey"


def colorise_list(party_list: Iterable) -> list[str]:
    """Return a list of party/state colors for a party_list."""
    return [get_color(x) for x in party_list]


def contrast(orig_color: str) -> str:
    """Provide a constrasting color to any party color."""
    new_color = "black"
    match orig_color:
        case "royalblue":
            new_color = "indianred"
        case "indianred":
            new_color = "mediumblue"

        case "darkorange":
            new_color = "mediumblue"
        case "mediumblue":
            new_color = "darkorange"

        case "mediumseagreen":
            new_color = "darkblue"

        case "darkgrey":
            new_color = "hotpink"

    return new_color


# --- Australian state names
_state_names: dict[str, str] = {
    "New South Wales": "NSW",
    "Victoria": "Vic",
    "Queensland": "Qld",
    "South Australia": "SA",
    "Western Australia": "WA",
    "Tasmania": "Tas",
    "Northern Territory": "NT",
    "Australian Capital Territory": "ACT",
}

# a tuple of standard state names
state_names = tuple(_state_names.keys())

# a tuple of standard state abbreviations
state_abbrs = tuple(_state_names.values())

# a map of state name to their abbreviation
# including upper and lower case mappings
_state_names_multi: dict[str, str] = {}
for k, v in _state_names.items():
    # allow for fast different case matches
    _state_names_multi[k.lower()] = v
    _state_names_multi[k.lower()] = v
    _state_names_multi[v.lower()] = v


def abbreviate_state(state: str) -> str:
    """Abbreviate long-form state names.

    Args:
        state: str - the long-form state name.

    Return the abbreviation for a state name.

    """
    return _state_names_multi.get(state.lower(), state)
