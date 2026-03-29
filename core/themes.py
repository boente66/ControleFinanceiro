# =========================================================
# SISTEMA DE TEMAS PROFISSIONAL — VERSÃO FINAL CORRIGIDA
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
# TOKENS GLOBAIS
# =========================================================
V = {
    "bg_light": "#f4f6f9",
    "bg_dark": "#0f1720",

    "panel_light": "#ffffff",
    "panel_dark": "#121214",

    "card_light": "#fbfdff",
    "card_dark": "#151515",

    "sidebar_light": "#111827",
    "sidebar_dark": "#1f2330",

    "border_light": "#e6e9ee",
    "border_dark": "#2a2f3a",

    "text_light": "#111827",
    "text_dark": "#e6eef8",
    "muted_light": "#6b7280",
    "muted_dark": "#9aa4b2",

    "primary_light": "#2563eb",
    "primary_dark": "#3aa0ff",
    "accent_green": "#16a34a",
    "accent_orange": "#f59e0b",

    "success_light": "#16a34a",
    "success_dark": "#22c55e",
    "danger_light": "#dc2626",
    "danger_dark": "#ef4444",
    "warning_light": "#d97706",
    "warning_dark": "#f59e0b",

    "highlight_light": "#f3f4f6",
    "highlight_dark": "#222831",

    "menu_active_light": "#10b981",
    "menu_active_dark": "#0ea5e9",
}

# =========================================================
# HELPERS
# =========================================================
def _common_table_styles(tokens):
    return f"""
QTableWidget, QTreeView {{
    background-color: {tokens['card']};
    gridline-color: {tokens['border']};
    color: {tokens['text']};
    border-radius: 8px;
}}

QHeaderView::section {{
    background-color: {tokens['highlight']};
    color: {tokens['text']};
    padding: 6px;
    border: 1px solid {tokens['border']};
}}

QTableWidget::item:selected, QTreeView::item:selected {{
    background-color: {tokens['primary']};
    color: #fff;
}}
"""

# =========================================================
# TEMAS
# =========================================================

ORGANIZZE_LIGHT = BASE + f"""
QWidget {{
    background-color: {V['bg_light']};
    color: {V['text_light']};
}}

QWidget#sidebar {{
    background-color: {V['sidebar_light']};
    border-right: 3px solid {V['accent_green']};
}}

QPushButton {{
    background-color: {V['primary_light']};
    color: #fff;
    padding: 8px 12px;
    border-radius: 8px;
    border: 1px solid rgba(0,0,0,0.06);
}}

QPushButton:hover {{ background-color: #1d4ed8; }}

QPushButton:disabled {{
    background-color: #cbd5e1;
    color: #93a3be;
}}

QPushButton#danger {{ background-color: {V['danger_light']}; }}

QLineEdit, QComboBox, QDateEdit {{
    background-color: {V['panel_light']};
    border: 1px solid {V['border_light']};
    border-radius: 8px;
    padding: 8px;
    color: {V['text_light']};
}}

QLineEdit:focus {{ border: 1px solid {V['primary_light']}; }}

QProgressBar {{
    background-color: {V['highlight_light']};
    border-radius: 8px;
    height: 12px;
}}

QProgressBar::chunk {{ background-color: {V['accent_green']}; }}

QMenu {{
    background-color: {V['panel_light']};
    border: 1px solid {V['border_light']};
}}

QTabBar::tab {{
    background: transparent;
    padding: 8px 12px;
    border-radius: 6px;
}}

QTabBar::tab:selected {{
    background: {V['highlight_light']};
    font-weight: 600;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
}}

QScrollBar::handle:vertical {{
    background: {V['border_light']};
    border-radius: 5px;
}}

{_common_table_styles({'card': V['card_light'], 'border': V['border_light'], 'highlight': V['highlight_light'], 'primary': V['primary_light'], 'text': V['text_light']})}

QLabel#positivo {{ color: {V['success_light']}; font-weight: bold; }}
QLabel#negativo {{ color: {V['danger_light']}; font-weight: bold; }}
QLabel#muted {{ color: {V['muted_light']}; }}
"""

ORGANIZZE_DARK = BASE + f"""
QWidget {{
    background-color: {V['bg_dark']};
    color: {V['text_dark']};
}}

QWidget#sidebar {{
    background-color: {V['sidebar_dark']};
    border-right: 2px solid {V['menu_active_dark']};
}}

QPushButton {{
    background-color: {V['primary_dark']};
    color: #fff;
    padding: 8px 12px;
    border-radius: 8px;
}}

QPushButton:hover {{ background-color: #2a6ef6; }}

QPushButton:disabled {{
    background-color: #3b4250;
    color: #7b8492;
}}

QLineEdit, QComboBox, QDateEdit {{
    background-color: {V['panel_dark']};
    border: 1px solid {V['border_dark']};
    border-radius: 8px;
    padding: 8px;
    color: {V['text_dark']};
}}

QLineEdit:focus {{ border: 1px solid {V['primary_dark']}; }}

QProgressBar {{
    background-color: {V['highlight_dark']};
    border-radius: 8px;
    height: 12px;
}}

QProgressBar::chunk {{ background-color: {V['menu_active_dark']}; }}

QMenu {{
    background-color: {V['panel_dark']};
    border: 1px solid {V['border_dark']};
}}

QTabBar::tab {{
    background: transparent;
    padding: 8px 12px;
    border-radius: 6px;
}}

QTabBar::tab:selected {{
    background: {V['highlight_dark']};
    font-weight: 600;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
}}

QScrollBar::handle:vertical {{
    background: {V['border_dark']};
    border-radius: 5px;
}}

{_common_table_styles({'card': V['card_dark'], 'border': V['border_dark'], 'highlight': V['highlight_dark'], 'primary': V['primary_dark'], 'text': V['text_dark']})}

QLabel#positivo {{ color: {V['success_dark']}; font-weight: bold; }}
QLabel#negativo {{ color: {V['danger_dark']}; font-weight: bold; }}
QLabel#muted {{ color: {V['muted_dark']}; }}
"""

VSCODE = BASE + f"""
QWidget {{
    background-color: #1e1e1e;
    color: #d4d4d4;
}}

QWidget#sidebar {{
    background-color: #252526;
    border-right: 1px solid #2a2d2f;
}}

QPushButton {{
    background-color: {V['primary_dark']};
    color: #fff;
    border-radius: 6px;
    padding: 6px 10px;
}}

QPushButton:hover {{ background-color: #006bdd; }}

QLineEdit, QComboBox, QDateEdit {{
    background-color: #1e1e1e;
    border: 1px solid #2a2a2a;
    border-radius: 6px;
    padding: 6px;
    color: #d4d4d4;
}}

{_common_table_styles({'card': '#1f2328', 'border': '#2a2d31', 'highlight': '#2a2d31', 'primary': '#007acc', 'text': '#d4d4d4'})}
"""

# =========================================================
# TEMAS + ALIASES
# =========================================================

THEMES = {
    "Organizze Claro": ORGANIZZE_LIGHT,
    "Organizze Escuro": ORGANIZZE_DARK,
    "VSCode": VSCODE,
}

ALIASES = {
    "Claro": "Organizze Claro",
    "Escuro": "Organizze Escuro",
    "Verde": "Organizze Claro",
}

# =========================================================
# FUNÇÕES PÚBLICAS
# =========================================================

def get_theme(nome: str) -> str:
    if not isinstance(nome, str):
        return ORGANIZZE_LIGHT

    nome = nome.strip()

    # 🔥 resolve alias
    nome = ALIASES.get(nome, nome)

    return THEMES.get(nome, ORGANIZZE_LIGHT)


def available_themes() -> list:
    """Somente temas reais (sem alias)."""
    return sorted(THEMES.keys())


def register_theme(nome: str, stylesheet: str) -> None:
    """Registra tema dinamicamente."""
    if not isinstance(nome, str) or not isinstance(stylesheet, str):
        return

    nome = nome.strip()
    if not nome:
        return

    THEMES[nome] = stylesheet
