# textual-theme-editor

A theme editor for [Textual](https://github.com/Textualize/textual).

![screenshot](https://raw.githubusercontent.com/TomJGooding/textual-theme-editor/main/assets/screenshot.png)

## Installation

Install textual-theme-editor using pip:

```
pip install textual-theme-editor
```

## Usage

Run the theme editor app to quickly create and preview a theme:

```
python -m textual_theme_editor
```

You can easily add the `ThemeEditor` widget in your own Textual apps:

```python
from textual.app import App, ComposeResult

from textual_theme_editor import ThemeEditor


class ExampleApp(App):
    def compose(self) -> ComposeResult:
        yield ThemeEditor()
```

## Contributing

I created this theme editor as a learning exercise to better understand
Textual and it is still a work in progress.

I'd really appreciate any feedback or suggestions, but I'm afraid I probably
won't be accepting any PRs at the moment.

## License

Licensed under the [GNU General Public License v3.0](LICENSE).
