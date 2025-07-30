from typing import Any

from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Footer,
    Input,
    Label,
    OptionList,
    RadioButton,
    Switch,
)

from textual_theme_editor import ThemeEditor

_TABLE_ROWS = [
    ("lane", "swimmer", "country", "time"),
    (4, "Joseph Schooling", "Singapore", 50.39),
    (2, "Michael Phelps", "United States", 51.14),
    (5, "Chad le Clos", "South Africa", 51.14),
    (6, "László Cseh", "Hungary", 51.14),
    (3, "Li Zhuhao", "China", 51.26),
    (8, "Mehdy Metella", "France", 51.58),
    (7, "Tom Shields", "United States", 51.73),
    (1, "Aleksandr Sadovnikov", "Russia", 51.84),
    (10, "Darren Burns", "Scotland", 51.84),
]


class ThemeEditorApp(App):
    CSS = """
    #widgets-list > * {
        margin: 1 2;
    }

    #buttons > Button {
        margin-right: 1;
    }

    #switch > Label {
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield ThemeEditor()

        with VerticalScroll(can_focus=False, id="widgets-list"):
            with HorizontalGroup(id="buttons"):
                yield Button("Default")
                yield Button("Primary", variant="primary")
                yield Button("Success", variant="success")
                yield Button("Warning", variant="warning")
                yield Button("Error", variant="error")

            with HorizontalGroup(id="toggle-buttons"):
                yield Checkbox("Checkbox", value=True)
                yield RadioButton("Radio button")
                with HorizontalGroup(id="switch"):
                    yield Switch(value=True)
                    yield Label("Switch")

            table = DataTable[Any]()
            table.add_columns(*_TABLE_ROWS[0])  # type: ignore[arg-type]
            table.add_rows(_TABLE_ROWS[1:])
            table.cursor_type = "row"
            table.fixed_columns = 1
            table.zebra_stripes = True
            yield table

            yield Input(placeholder="Type anything here")

            yield OptionList(
                "Aerilon",
                "Aquaria",
                "Canceron",
                "Caprica",
                "Gemenon",
                "Leonis",
                "Libran",
                "Picon",
                "Sagittaron",
                "Scorpia",
                "Tauron",
                "Virgon",
            )

        yield Footer()


if __name__ == "__main__":
    app = ThemeEditorApp()
    app.run()
