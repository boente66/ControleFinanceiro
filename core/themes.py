# =========================================================
# SISTEMA DE TEMAS PROFISSIONAL (COMPLETO FINAL)
# =========================================================

from core.session import Session

# =========================================================
# BASE
# =========================================================
BASE = """
QWidget {
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}

QToolTip {
    padding: 6px;
    border-radius: 6px;
    color: #fff;
    background-color: rgba(0,0,0,0.75);
}
"""

# =========================================================
# TOKENS
# =========================================================
V = {
    "bg_light": "#f4f6f9",
    "bg_dark": "#0f1720",

    "panel_light": "#ffffff",
    "panel_dark": "#121214",

    "card_light": "#ffffff",
    "card_dark": "#1a1a1a",

    "sidebar_dark": "#111827",
    "sidebar_dark_green": "#14532d",

    "border_light": "#e6e9ee",
    "border_dark": "#2a2f3a",

    "text_light": "#111827",
    "text_dark": "#e6eef8",

    "primary_blue": "#2563eb",
    "primary_dark": "#3aa0ff",

    "green": "#16a34a",
    "green_hover": "#15803d",

    "success": "#22c55e",
    "danger": "#ef4444",
    "warning": "#f59e0b",

    "highlight_light": "#f3f4f6",
    "highlight_dark": "#222831",
}

# =========================================================
# COMPONENTES
# =========================================================
def _sidebar(tokens):
    return f"""
QWidget#sidebar {{
    background-color: {tokens['sidebar']};
}}

QPushButton#menuButton {{
    background: transparent;
    color: white;
    text-align: left;
    padding: 10px 15px;
    border: none;
}}

QPushButton#menuButton:hover {{
    background-color: rgba(255,255,255,0.08);
}}

QPushButton#menuButton[active="true"] {{
    background-color: rgba(255,255,255,0.15);
    border-left: 4px solid {tokens['primary']};
}}

QLabel#sidebarUser {{
    color: #cbd5e1;
    font-weight: bold;
}}
"""


def _buttons(primary, hover):
    return f"""
QPushButton {{
    background-color: {primary};
    color: white;
    padding: 8px;
    border-radius: 8px;
}}

QPushButton:hover {{
    background-color: {hover};
}}
"""


def _inputs(bg, border):
    return f"""
QLineEdit, QComboBox {{
    background: {bg};
    border: 1px solid {border};
    padding: 6px;
    border-radius: 6px;
}}

QComboBox QAbstractItemView {{
    background-color: {bg};
    selection-background-color: {border};
}}
"""


def _cards(tokens):
    return f"""
QFrame#card {{
    background-color: {tokens['card']};
    border-radius: 12px;
    padding: 12px;
    border: 1px solid {tokens['border']};
}}

QLabel#cardTitle {{
    font-size: 12px;
    color: {tokens['text']};
    opacity: 0.7;
}}

QLabel#cardValue {{
    font-size: 20px;
    font-weight: bold;
    color: {tokens['primary']};
}}
"""


def _groupbox(tokens):
    return f"""
QGroupBox {{
    border: 1px solid {tokens['border']};
    border-radius: 8px;
    margin-top: 10px;
    padding: 10px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px;
}}
"""


def _table(tokens):
    return f"""
QTableWidget {{
    background-color: {tokens['card']};
    color: {tokens['text']};
    border-radius: 10px;
    gridline-color: {tokens['highlight']};
}}

QHeaderView::section {{
    background-color: {tokens['highlight']};
    padding: 8px;
    border: none;
}}

QTableWidget::item:selected {{
    background-color: {tokens['primary']};
    color: white;
}}
"""


def _progress(color):
    return f"""
QProgressBar {{
    border-radius: 6px;
    background-color: rgba(0,0,0,0.1);
}}

QProgressBar::chunk {{
    background-color: {color};
    border-radius: 6px;
}}
"""


def _labels(tokens):
    return f"""
QLabel#positivo {{ color: {tokens['success']}; font-weight: bold; }}
QLabel#negativo {{ color: {tokens['danger']}; font-weight: bold; }}
QLabel#warning {{ color: {tokens['warning']}; font-weight: bold; }}

QLabel#pageTitle {{
    font-size: 18px;
    font-weight: bold;
}}
"""


# =========================================================
# 🎨 TEMA CLARO
# =========================================================
def tema_claro():
    return BASE + f"""
QWidget {{
    background-color: {V['bg_light']};
    color: {V['text_light']};
}}

{_sidebar({
    "sidebar": V['sidebar_dark'],
    "primary": V['primary_blue']
})}

{_buttons(V['primary_blue'], "#1d4ed8")}
{_inputs(V['panel_light'], V['border_light'])}
{_progress(V['green'])}

{_cards({
    "card": V['card_light'],
    "text": V['text_light'],
    "primary": V['primary_blue'],
    "border": V['border_light']
})}

{_groupbox({
    "border": V['border_light']
})}

{_table({
    "card": V['card_light'],
    "text": V['text_light'],
    "highlight": V['highlight_light'],
    "primary": V['primary_blue']
})}

{_labels(V)}
"""


# =========================================================
# 🌙 TEMA ESCURO
# =========================================================
def tema_escuro():
    return BASE + f"""
QWidget {{
    background-color: {V['bg_dark']};
    color: {V['text_dark']};
}}

{_sidebar({
    "sidebar": "#1f2330",
    "primary": V['primary_dark']
})}

{_buttons(V['primary_dark'], "#2a6ef6")}
{_inputs(V['panel_dark'], V['border_dark'])}
{_progress("#0ea5e9")}

{_cards({
    "card": V['card_dark'],
    "text": V['text_dark'],
    "primary": V['primary_dark'],
    "border": V['border_dark']
})}

{_groupbox({
    "border": V['border_dark']
})}

{_table({
    "card": V['card_dark'],
    "text": V['text_dark'],
    "highlight": V['highlight_dark'],
    "primary": V['primary_dark']
})}

{_labels(V)}
"""


# =========================================================
# 💚 TEMA VERDE
# =========================================================
def tema_verde():
    return BASE + f"""
QWidget {{
    background-color: {V['bg_light']};
    color: {V['text_light']};
}}

{_sidebar({
    "sidebar": V['sidebar_dark_green'],
    "primary": V['green']
})}

{_buttons(V['green'], V['green_hover'])}
{_inputs("white", V['green'])}
{_progress(V['green'])}

{_cards({
    "card": V['card_light'],
    "text": V['text_light'],
    "primary": V['green'],
    "border": V['border_light']
})}

{_groupbox({
    "border": V['border_light']
})}

{_table({
    "card": V['card_light'],
    "text": V['text_light'],
    "highlight": V['highlight_light'],
    "primary": V['green']
})}

{_labels(V)}
"""


# =========================================================
# REGISTRO
# =========================================================
THEMES = {
    "Claro": tema_claro,
    "Escuro": tema_escuro,
    "Verde": tema_verde,
}

DEFAULT_THEME = "Claro"

# =========================================================
# CORE
# =========================================================
def get_theme(nome: str = None) -> str:
    nome = nome or Session.get_config("tema", DEFAULT_THEME)
    return THEMES.get(nome, tema_claro)()


def apply_theme(app, nome: str = None):
    nome = nome or DEFAULT_THEME
    Session.set_config("tema", nome)
    app.setStyleSheet(get_theme(nome))


def current_theme():
    return Session.get_config("tema", DEFAULT_THEME)


def available_themes():
    return list(THEMES.keys())


def register_theme(nome: str, builder):
    if nome and callable(builder):
        THEMES[nome] = builder
