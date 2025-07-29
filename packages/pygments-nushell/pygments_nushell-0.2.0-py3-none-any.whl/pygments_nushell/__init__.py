from pygments.lexer import (
    RegexLexer,
    bygroups,
    include,
)
from pygments.token import (
    Punctuation,
    Whitespace,
    Text,
    Comment,
    Operator,
    Keyword,
    Name,
    String,
    Number,
)
from pygments.util import shebang_matches


class NuLexer(RegexLexer):
    """
    Lexer for nu shell scripts.
    """

    name = "Nu"
    aliases = ["nu"]
    filenames = [
        "*.nu",
    ]
    mimetypes = ["text/plain"]
    url = "https://www.nushell.sh"

    tokens = {
        "root": [
            include("basic"),
            include("data"),
        ],
        "basic": [
            # Nushell has a metric buttload of commands, some of which consist of multiple words
            # (these were obtained by running help commands | get name | str join "|" in nushell)
            (
                r"\b(alias|all|ansi|ansi gradient|ansi link|ansi strip|any|append|ast|attr category|attr deprecated|"
                r"attr example|attr search-terms|banner|bits|bits and|bits not|bits or|bits rol|bits ror|bits shl|bits shr|"
                r"bits xor|break|bytes|bytes add|bytes at|bytes build|bytes collect|bytes ends-with|bytes index-of|bytes length|"
                r"bytes remove|bytes replace|bytes reverse|bytes split|bytes starts-with|cal|cd|char|chunk-by|chunks|clear|collect|"
                r"columns|commandline|commandline edit|commandline get-cursor|commandline set-cursor|compact|complete|config|config env|"
                r"config flatten|config nu|config reset|config use-colors|const|continue|cp|date|date format|date from-human|date humanize|"
                r"date list-timezone|date now|date to-timezone|debug|debug env|debug info|debug profile|decode|decode base32|decode base32hex|"
                r"decode base64|decode hex|def|default|describe|detect columns|do|drop|drop column|drop nth|du|each|each while|echo|encode|"
                r"encode base32|encode base32hex|encode base64|encode hex|enumerate|error make|every|exec|exit|explain|explore|export|"
                r"export alias|export const|export def|export extern|export module|export use|export-env|extern|fill|filter|find|first|flatten|"
                r"for|format|format bits|format date|format duration|format filesize|format number|format pattern|from|from csv|from json|"
                r"from msgpack|from msgpackz|from nuon|from ods|from ssv|from toml|from tsv|from url|from xlsx|from xml|from yaml|from yml|"
                r"generate|get|glob|grid|group-by|hash|hash md5|hash sha256|headers|help|help aliases|help commands|help escapes|help externs|"
                r"help modules|help operators|help pipe-and-redirect|hide|hide-env|histogram|history|history import|history session|http|"
                r"http delete|http get|http head|http options|http patch|http post|http put|if|ignore|input|input list|input listen|insert|inspect|"
                r"interleave|into|into binary|into bool|into cell-path|into datetime|into duration|into filesize|into float|into glob|into int|"
                r"into record|into sqlite|into string|into value|is-admin|is-empty|is-not-empty|is-terminal|items|job|job flush|job id|job kill|"
                r"job list|job recv|job send|job spawn|job tag|job unfreeze|join|keybindings|keybindings default|keybindings list|keybindings listen|"
                r"kill|last|length|let|let-env|lines|load-env|loop|ls|match|math|math abs|math arccos|math arccosh|math arcsin|math arcsinh|math arctan|"
                r"math arctanh|math avg|math ceil|math cos|math cosh|math exp|math floor|math ln|math log|math max|math median|math min|math mode|math product|"
                r"math round|math sin|math sinh|math sqrt|math stddev|math sum|math tan|math tanh|math variance|merge|merge deep|metadata|metadata access|"
                r"metadata set|mkdir|mktemp|module|move|mut|mv|nu-check|nu-highlight|open|overlay|overlay hide|overlay list|overlay new|overlay use|panic|"
                r"par-each|parse|path|path basename|path dirname|path exists|path expand|path join|path parse|path relative-to|path self|path split|"
                r"path type|plugin|plugin add|plugin list|plugin rm|plugin stop|plugin use|port|prepend|print|ps|pwd|query db|random|random binary|"
                r"random bool|random chars|random dice|random float|random int|random uuid|reduce|reject|rename|return|reverse|rm|roll|roll down|"
                r"roll left|roll right|roll up|rotate|run-external|save|schema|scope|scope aliases|scope commands|scope engine-stats|scope externs|"
                r"scope modules|scope variables|select|seq|seq char|seq date|shuffle|skip|skip until|skip while|sleep|slice|sort|sort-by|source|source-env|"
                r"split|split cell-path|split chars|split column|split list|split row|split words|start|stor|stor create|stor delete|stor export|stor import|"
                r"stor insert|stor open|stor reset|stor update|str|str camel-case|str capitalize|str contains|str distance|str downcase|str ends-with|"
                r"str expand|str index-of|str join|str kebab-case|str length|str pascal-case|str replace|str reverse|str screaming-snake-case|str snake-case|"
                r"str starts-with|str stats|str substring|str title-case|str trim|str upcase|sys|sys cpu|sys disks|sys host|sys mem|sys net|sys temp|sys users|"
                r"table|take|take until|take while|tee|term|term query|term size|timeit|to|to csv|to html|to json|to md|to msgpack|to msgpackz|to nuon|to text|"
                r"to toml|to tsv|to xml|to yaml|to yml|touch|transpose|try|tutor|ulimit|uname|uniq|uniq-by|update|update cells|upsert|url|url build-query|"
                r"url decode|url encode|url join|url parse|url split-query|use|values|version|version check|view|view blocks|view files|view ir|view source|"
                r"view span|watch|where|which|while|whoami|window|with-env|wrap|zip)(\s*)\b",
                bygroups(Keyword, Whitespace),
            ),
            (r"\A#!.+\n", Comment.Hashbang),
            (r"#.*\n", Comment.Single),
            (r"\\[\w\W]", String.Escape),
            (r"(\b\w+)(\s*)(\+?=)", bygroups(Name.Variable, Whitespace, Operator)),
            (r"[\[\]{}()=]", Operator),
            (r"<<<", Operator),  # here-string
            (r"<<-?\s*(\'?)\\?(\w+)[\w\W]+?\2", String),
            (r"&&|\|\|", Operator),
            (r"\$[a-zA-Z_]\w*", Name.Variable),  # user variable

        ],
        "data": [
            (r'(?s)\$?"(\\.|[^"\\$])*"', String.Double),
            (r'"', String.Double, "string"),
            (r"(?s)\$'(\\\\|\\[0-7]+|\\.|[^'\\])*'", String.Single),
            (r"(?s)'.*?'", String.Single),
            (r";", Punctuation),
            (r"&", Punctuation),
            (r"\|", Punctuation),
            (r"\s+", Whitespace),
            (r"\d+\b", Number),
            (r'[^=\s\[\]{}()$"\'`\\<&|;]+', Text),
            (r"<", Text),
        ],
        "string": [
            (r'"', String.Double, "#pop"),
            (r'(?s)(\\\\|\\[0-7]+|\\.|[^"\\$])+', String.Double),
        ],
        "curly": [
            (r"\}", String.Interpol, "#pop"),
            (r":-", Keyword),
            (r"\w+", Name.Variable),
            (r'[^}:"\'`$\\]+', Punctuation),
            (r":", Punctuation),
            include("root"),
        ],
        "paren": [
            (r"\)", Keyword, "#pop"),
            include("root"),
        ],
        "math": [
            (r"\)\)", Keyword, "#pop"),
            (r"\*\*|\|\||<<|>>|[-+*/%^|&<>]", Operator),
            (r"\d+#[\da-zA-Z]+", Number),
            (r"\d+#(?! )", Number),
            (r"0[xX][\da-fA-F]+", Number),
            (r"\d+", Number),
            (r"[a-zA-Z_]\w*", Name.Variable),  # user variable
            include("root"),
        ],
        "backticks": [
            (r"`", String.Backtick, "#pop"),
            include("root"),
        ],
    }

    def analyse_text(text):
        if shebang_matches(text, r"nu"):
            return 1
