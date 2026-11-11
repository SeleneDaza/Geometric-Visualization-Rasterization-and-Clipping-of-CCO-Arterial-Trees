from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication


THEME_COLORS = {
    False: {
        "window": "#f1f4f8",
        "sidebar": "#ffffff",
        "surface": "#ffffff",
        "card": "#f7f9fc",
        "header": "#f5f8fc",
        "control": "#ffffff",
        "control_hover": "#edf4fb",
        "border": "#d5deea",
        "divider": "#dce3ed",
        "text": "#23344d",
        "muted": "#687386",
        "accent": "#1769aa",
        "selection": "#dcecf8",
        "selection_text": "#173b63",
        "scrollbar": "#f1f4f8",
        "scrollbar_handle": "#c3cedb",
        "grid": "#dce3ed",
    },
    True: {
        "window": "#161d27",
        "sidebar": "#1d2733",
        "surface": "#202b36",
        "card": "#263442",
        "header": "#202b36",
        "control": "#2d3b49",
        "control_hover": "#3b5262",
        "border": "#435565",
        "divider": "#344452",
        "text": "#e6edf3",
        "muted": "#b8c7d3",
        "accent": "#65c8c0",
        "selection": "#245d70",
        "selection_text": "#ffffff",
        "scrollbar": "#202b36",
        "scrollbar_handle": "#526575",
        "grid": "#435565",
    },
}


def system_uses_dark_theme(application=None):
    application = application or QApplication.instance()
    if application is None:
        return False

    color_scheme = application.styleHints().colorScheme()
    if color_scheme == Qt.ColorScheme.Dark:
        return True
    if color_scheme == Qt.ColorScheme.Light:
        return False

    return application.palette().color(
        application.palette().ColorRole.Window
    ).lightness() < 128
