# Pygments Nushell Lexer

This project implements a Nushell lexer for the Pygments library.

To use in your project, add the following to your pyproject.toml:

```toml
[project.entry-points."pygments.lexers"]
pygments_kakoune = "pygments_nushell:NuLexer"
```

## License

This project is licensed under the 0BSD license.
