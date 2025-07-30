from __future__ import annotations

import re

from rich.pretty import pretty_repr
from textual import events, on
from textual.app import ComposeResult
from textual.color import Color
from textual.containers import HorizontalGroup, VerticalGroup, VerticalScroll
from textual.reactive import var
from textual.screen import ModalScreen
from textual.theme import BUILTIN_THEMES, Theme
from textual.validation import Length
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Rule, TextArea
from textual_colorpicker import ColorPicker

_THEME_COLOR_NAMES = [
    "primary",
    "secondary",
    "foreground",
    "background",
    "surface",
    "panel",
    "warning",
    "error",
    "success",
    "accent",
]


class ThemeColorButton(Button):
    DEFAULT_CSS = """
    ThemeColorButton {
        &.-primary {
            color: auto;
            background: $primary;
            border-top: tall $primary-lighten-2;
            border-bottom: tall $primary-darken-3;

            &:hover {
                background: $primary-darken-1;
                border-top: tall $primary;
            }

            &.-active {
                background: $primary;
                border-bottom: tall $primary-lighten-2;
                border-top: tall $primary-darken-2;
            }
        }

        &.-secondary {
            color: auto;
            background: $secondary;
            border-top: tall $secondary-lighten-2;
            border-bottom: tall $secondary-darken-3;

            &:hover {
                background: $secondary-darken-1;
                border-top: tall $secondary;
            }

            &.-active {
                background: $secondary;
                border-bottom: tall $secondary-lighten-2;
                border-top: tall $secondary-darken-2;
            }
        }

        &.-foreground {
            color: auto;
            background: $foreground;
            border-top: tall $foreground-lighten-2;
            border-bottom: tall $foreground-darken-3;

            &:hover {
                background: $foreground-darken-1;
                border-top: tall $foreground;
            }

            &.-active {
                background: $foreground;
                border-bottom: tall $foreground-lighten-2;
                border-top: tall $foreground-darken-2;
            }
        }

        &.-background {
            color: auto;
            background: $background;
            border-top: tall $background-lighten-2;
            border-bottom: tall $background-darken-3;

            &:hover {
                background: $background-darken-1;
                border-top: tall $background;
            }

            &.-active {
                background: $background;
                border-bottom: tall $background-lighten-2;
                border-top: tall $background-darken-2;
            }
        }

        &.-surface {
            color: auto;
            background: $surface;
            border-top: tall $surface-lighten-2;
            border-bottom: tall $surface-darken-3;

            &:hover {
                background: $surface-darken-1;
                border-top: tall $surface;
            }

            &.-active {
                background: $surface;
                border-bottom: tall $surface-lighten-2;
                border-top: tall $surface-darken-2;
            }
        }

        &.-panel {
            color: auto;
            background: $panel;
            border-top: tall $panel-lighten-2;
            border-bottom: tall $panel-darken-3;

            &:hover {
                background: $panel-darken-1;
                border-top: tall $panel;
            }

            &.-active {
                background: $panel;
                border-bottom: tall $panel-lighten-2;
                border-top: tall $panel-darken-2;
            }
        }

        &.-warning {
            color: auto;
            background: $warning;
            border-top: tall $warning-lighten-2;
            border-bottom: tall $warning-darken-3;

            &:hover {
                background: $warning-darken-1;
                border-top: tall $warning;
            }

            &.-active {
                background: $warning;
                border-bottom: tall $warning-lighten-2;
                border-top: tall $warning-darken-2;
            }
        }

        &.-error {
            color: auto;
            background: $error;
            border-top: tall $error-lighten-2;
            border-bottom: tall $error-darken-3;

            &:hover {
                background: $error-darken-1;
                border-top: tall $error;
            }

            &.-active {
                background: $error;
                border-bottom: tall $error-lighten-2;
                border-top: tall $error-darken-2;
            }
        }

        &.-success {
            color: auto;
            background: $success;
            border-top: tall $success-lighten-2;
            border-bottom: tall $success-darken-3;

            &:hover {
                background: $success-darken-1;
                border-top: tall $success;
            }

            &.-active {
                background: $success;
                border-bottom: tall $success-lighten-2;
                border-top: tall $success-darken-2;
            }
        }

        &.-accent {
            color: auto;
            background: $accent;
            border-top: tall $accent-lighten-2;
            border-bottom: tall $accent-darken-3;

            &:hover {
                background: $accent-darken-1;
                border-top: tall $accent;
            }

            &.-active {
                background: $accent;
                border-bottom: tall $accent-lighten-2;
                border-top: tall $accent-darken-2;
            }
        }
    }
    """

    def __init__(
        self,
        label: str,
        color_name: str,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        super().__init__(
            label,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.color_name = color_name
        self.add_class(f"-{color_name}")


class ThemeColorPickerModal(ModalScreen):
    BINDINGS = [("escape", "close")]

    CSS = """
    ThemeColorPickerModal {
        align: center middle;

        & > VerticalGroup {
            width: auto;
            padding: 1 2;
            border: panel $panel;
            border-title-color: $foreground;
        }
    }
    """

    def __init__(
        self,
        theme_editor: ThemeEditor,
        color_name: str,
    ) -> None:
        super().__init__()
        self.theme_editor = theme_editor
        self.color_name = color_name

    def compose(self) -> ComposeResult:
        css_color = self.theme_editor._color_mapping[self.color_name]
        with VerticalGroup() as dialog:
            dialog.border_title = f"Change {self.color_name} color"
            yield ColorPicker(Color.parse(css_color))

    def on_color_picker_changed(self, event: ColorPicker.Changed) -> None:
        event.stop()
        css_color = event.color.hex
        setattr(self.theme_editor._theme, self.color_name, css_color)
        self.theme_editor.mutate_reactive(ThemeEditor._theme)

    def action_close(self) -> None:
        self.dismiss()

    def on_click(self, event: events.Click) -> None:
        clicked, _ = self.get_widget_at(event.screen_x, event.screen_y)
        if clicked is self:
            self.dismiss()


class ExportThemeModal(ModalScreen):
    BINDINGS = [("escape", "close")]

    CSS = """
    ExportThemeModal {
        align: center middle;

        & > VerticalGroup {
            width: 60%;
            height: 80%;
            padding: 1 2;
            border: panel $panel;
            border-title-color: $foreground;

            & > HorizontalGroup {
                margin-bottom: 1;

                & > Label {
                    padding: 1;
                }
                
                & > Input {
                    width: 1fr;
                }
            }
        }
    }
    """

    def __init__(self, theme: Theme) -> None:
        super().__init__()
        self.theme = theme

    def compose(self) -> ComposeResult:
        edited_theme_name = f"{self.theme.name}-edited"

        with VerticalGroup() as dialog:
            dialog.border_title = "Export theme"
            with HorizontalGroup():
                yield Label("Name:")
                yield Input(
                    edited_theme_name,
                    validators=Length(minimum=1),
                    validate_on=["changed"],
                )

            theme_code = self.get_theme_code(edited_theme_name)
            code_display = TextArea(
                theme_code,
                language="python",
                read_only=True,
            )
            code_display.cursor_blink = False
            yield code_display

    def get_theme_code(self, theme_name: str) -> str:
        theme_code = pretty_repr(self.theme)
        updated_theme_code = re.sub(
            r"name='.*?'", f"name='{theme_name}'", theme_code, count=1
        )
        return updated_theme_code

    def on_input_changed(self, event: Input.Changed) -> None:
        event.stop()
        assert event.validation_result is not None
        if event.validation_result.is_valid:
            theme_name = event.input.value
            theme_code = self.get_theme_code(theme_name)
            self.query_one(TextArea).load_text(theme_code)

    def action_close(self) -> None:
        self.dismiss()

    def on_click(self, event: events.Click) -> None:
        clicked, _ = self.get_widget_at(event.screen_x, event.screen_y)
        if clicked is self:
            self.dismiss()


class ThemeEditor(Widget):
    """A theme editor widget."""

    DEFAULT_CSS = """
    ThemeEditor {
        dock: left;
        width: 38;
        min-width: 38;
        padding: 1 1 2 1;
        border-right: vkey $foreground 30%;

        & > VerticalScroll {
            layout: grid;
            grid-size: 2;
            grid-columns: auto;
            grid-rows: 3;
            grid-gutter: 1;

            & > Label {
                width: 1fr;
                padding: 1;
                text-align: right;
                text-style: bold;
            }
        }

        & > Rule {
            color: $foreground 30%;
        }

        & > HorizontalGroup {
            & > Button {
                margin: 0 1;
            }
        }
    }
    """

    _theme: var[Theme] = var(BUILTIN_THEMES["textual-dark"], init=False)

    def __init__(
        self,
        show_export_button: bool = True,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Create a theme editor widget.

        Args:
            show_export_button: Show a button to export the theme.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes of the widget.
            disabled: Whether the widget is disabled or not.
        """
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self._show_export_button = show_export_button

    def compose(self) -> ComposeResult:
        with VerticalScroll(can_focus=False):
            for color_name in _THEME_COLOR_NAMES:
                css_color = self._color_mapping[color_name]
                yield Label(color_name)
                yield ThemeColorButton(css_color, color_name)

        if self._show_export_button:
            yield Rule()
            with HorizontalGroup():
                yield Button("Export theme", classes="--export-button")

    def on_mount(self) -> None:
        self.watch(self.app, "theme", self._on_app_theme_change)

    @property
    def _color_mapping(self) -> dict[str, str]:
        color_system = self._theme.to_color_system()
        color_mapping = color_system.generate()
        return color_mapping

    def _on_app_theme_change(self, theme_name: str) -> None:
        theme = self.app.get_theme(theme_name)
        assert theme is not None
        self._theme = theme

    def _watch__theme(self) -> None:
        for color_name in _THEME_COLOR_NAMES:
            css_color = self._color_mapping[color_name]
            button = self.query_one(f".-{color_name}", ThemeColorButton)
            button.label = css_color

        self.app._invalidate_css()
        self.app.call_next(self.app.refresh_css)

    @on(ThemeColorButton.Pressed, "ThemeColorButton")
    def _on_theme_color_button_pressed(
        self,
        event: ThemeColorButton.Pressed,
    ) -> None:
        event.stop()
        assert isinstance(event.button, ThemeColorButton)
        self.app.push_screen(
            ThemeColorPickerModal(self, event.button.color_name),
        )

    @on(Button.Pressed, ".--export-button")
    def _on_export_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        self.app.push_screen(ExportThemeModal(self._theme))
