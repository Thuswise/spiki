"""An example plugin style for Pygments."""

try:
    from pygments.style import Style
    from pygments.token import Keyword
except ModuleNotFoundError:
    Style = object
    Keyword = "keyword"


class SpeechMarkStyle(Style):
    styles = {
        # This style merely highlights keywords in red.
        Keyword: "#f00",
    }
