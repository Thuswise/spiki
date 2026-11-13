"""An example plugin lexer for Pygments."""

try:
    from pygments.lexer import RegexLexer
    from pygments.token import Keyword
    from pygments.token import Text
except ModuleNotFoundError:
    RegexLexer = object
    Keyword = object
    Text = object


class SpeechMarkLexer(RegexLexer):
    name = "SpeechMark"
    aliases = ["speechmark"]
    filenames = ["*.smk"]
    mimetypes = ["text/speechmark"]

    # This lexer highlights lines that read "foo".
    tokens = {
        "root": [
            (r"foo\n", Keyword),
            (r".*\n", Text),
        ]
    }
