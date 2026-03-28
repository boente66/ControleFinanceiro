# =========================================================
# SISTEMA DE TEMAS PROFISSIONAL — FINAL
# =========================================================

BASE = """
QWidget {
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}

QToolTip {
    padding: 6px;
    border-radius: 6px;
}
"""

# =========================================================
# TOKENS
# =========================================================
V = {
    "bg_light": "#f4f6f9",
    "bg_dark": "#121212",

    "panel_light": "#ffffff",
    "panel_dark": "#1e1e1e",

    "sidebar_light": "#111827",  # melhor que preto puro
    "sidebar_dark": "#181818",

    "border_light": "#e5e7eb",
    "border_dark": "#2c2c2c",

    "text_light": "#1f2937",
    "text_dark": "#f3f4f6",

    "muted_light": "#6b7280",
    "muted_dark": "#9ca3af",

    "highlight_light": "#f3f4f6",
    "highlight_dark": "#2a2a2a",

    "primary_light": "#2563eb",
    "primary_dark": "#3b82f6",

    "success_light": "#16a34a",
    "success_dark": "#22c55e",

    "danger_light": "#dc2626",
    "danger_dark": "#ef4444",

    "warning_light": "#d97706",
    "warning_dark": "#f59e0b",

    "menu_active_light": "#16a34a",
    "menu_active_dark": "#3b82f6",
}

# =========================================================
# TEMA CLARO
# =========================================================
LIGHT = BASE + f"""

QWidget {{
    background-color: {V['panel_light']};
    color: {V['text_light']};
}}

QWidget#sidebar {{
    background-color: {V['sidebar_light']};
    border-right: 3px solid {V['success_light']};
}}

QPushButton#menuButton {{
    background-color: transparent;
    color: white;
    border: none;
    padding: 14px;
    text-align: left;
    border-radius: 10px;
}}

QPushButton#menuButton:hover {{
    background-color: #1f2937;
}}

QPushButton#menuButton[active="true"] {{
    background-color: {V['menu_active_light']};
    color: white;
    font-weight: bold;
}}

QPushButton {{
    background-color: {V['primary_light']};
    color: white;
    padding: 10px 16px;
    border-radius: 10px;
}}

QPushButton:hover {{
    background-color: #1d4ed8;
}}

QPushButton:pressed {{
    background-color: #1e40af;
}}

QPushButton:disabled {{
    background-color: #9ca3af;
    color: #e5e7eb;
}}

QPushButton#primaryButton {{
    background-color: {V['success_light']};
    font-weight: 600;
}}

QPushButton#deleteButton {{
    background-color: {V['danger_light']};
}}

QLineEdit, QComboBox, QDateEdit {{
    background-color: white;
    border: 2px solid {V['border_light']};
    border-radius: 10px;
    padding: 8px;
}}

QLineEdit:focus {{
    border: 2px solid {V['primary_light']};
}}

QTableWidget {{
    background-color: white;
}}

QProgressBar {{
    background-color: {V['highlight_light']};
    border-radius: 8px;
}}

QProgressBar::chunk {{
    background-color: {V['success_light']};
}}

QLabel#positivo {{ color: {V['success_light']}; font-weight: bold; }}
QLabel#negativo {{ color: {V['danger_light']}; font-weight: bold; }}
QLabel#warning {{ color: {V['warning_light']}; font-weight: bold; }}
QLabel#muted {{ color: {V['muted_light']}; }}
"""

# =========================================================
# TEMA ESCURO
# =========================================================
DARK = BASE + f"""

QWidget {{
    background-color: {V['bg_dark']};
    color: {V['text_dark']};
}}

QWidget#sidebar {{
    background-color: {V['sidebar_dark']};
    border-right: 2px solid {V['primary_dark']};
}}

QPushButton#menuButton {{
    background-color: transparent;
    border: none;
    padding: 14px;
    border-radius: 10px;
}}

QPushButton#menuButton:hover {{
    background-color: {V['highlight_dark']};
}}

QPushButton#menuButton[active="true"] {{
    background-color: {V['menu_active_dark']};
    color: white;
}}

QPushButton {{
    background-color: {V['primary_dark']};
    color: white;
}}

QPushButton:hover {{
    background-color: #2563eb;
}}

QPushButton:pressed {{
    background-color: #1e40af;
}}

QPushButton:disabled {{
    background-color: #555;
    color: #aaa;
}}

QPushButton#deleteButton {{
    background-color: {V['danger_dark']};
}}

QLineEdit, QComboBox {{
    background-color: {V['panel_dark']};
    border: 2px solid {V['border_dark']};
    border-radius: 10px;
    padding: 8px;
}}

QLineEdit:focus {{
    border: 2px solid {V['primary_dark']};
}}

QProgressBar {{
    background-color: {V['highlight_dark']};
}}

QProgressBar::chunk {{
    background-color: {V['primary_dark']};
}}

QLabel#positivo {{ color: {V['success_dark']}; }}
QLabel#negativo {{ color: {V['danger_dark']}; }}
QLabel#warning {{ color: {V['warning_dark']}; }}
QLabel#muted {{ color: {V['muted_dark']}; }}
"""

# =========================================================
# TEMA VERDE (IDENTIDADE)
# =========================================================
GREEN = BASE + """
QWidget {
    background-color: #022c22;
    color: #d1fae5;
}

QPushButton {
    background-color: #16a34a;
    color: white;
}

QPushButton:hover {
    background-color: #15803d;
}

#sidebar {
    background-color: #011a13;
}
"""

# =========================================================
# MAPA
# =========================================================
THEMES = {
    "Claro": LIGHT,
    "Escuro": DARK,
    "Verde": GREEN,
}

# =========================================================
# FUNÇÃO
# =========================================================
def get_theme(nome: str) -> str:
    tema = THEMES.get(nome)
    if not isinstance(tema, str) or not tema.strip():
        return LIGHT
    return tema
