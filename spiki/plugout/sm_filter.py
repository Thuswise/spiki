"""An example filter for Pygments."""

try:
    from pygments.filters import Filter
    from pygments.token import Token
except ModuleNotFoundError:
    Filter = object


class SpeechMarkFilter(Filter):
    # This filter replaces all tabs with "<tab>".
    def filter(self, lexer, stream):
        for ttype, value in stream:
            parts = value.split("\t")
            yield ttype, "<tab>".join(parts)
