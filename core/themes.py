# =========================================================
# SISTEMA DE TEMAS PROFISSIONAL — CONTROLE FINANCEIRO
# =========================================================

# ---------------------------------------------------------
# BASE GLOBAL
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# TOKENS VISUAIS
# ---------------------------------------------------------
V = {
    # Base
    "bg_light": "#f4f6f9",
    "bg_dark": "#121212",

    "panel_light": "#ffffff",
    "panel_dark": "#1e1e1e",

    "sidebar_light": "#000000",
    "sidebar_dark": "#181818",

    "border_light": "#e5e7eb",
    "border_dark": "#2c2c2c",

    "text_light": "#1f2937",
    "text_dark": "#f3f4f6",

    "muted_light": "#6b7280",
    "muted_dark": "#9ca3af",

    "highlight_light": "#f3f4f6",
    "highlight_dark": "#2a2a2a",

    # Ações
    "primary_light": "#2563eb",
    "primary_dark": "#3b82f6",

    "success_light": "#16a34a",
    "success_dark": "#22c55e",

    "danger_light": "#dc2626",
    "danger_dark": "#ef4444",

    "warning_light": "#d97706",
    "warning_dark": "#f59e0b",

    # Menu
    "menu_active_light": "#16a34a",
    "menu_active_dark": "#3b82f6",
}

# =========================================================
# TEMA CLARO
# =========================================================
LIGHT = BASE + f"""

/* ===================================================== */
/* FUNDO PRINCIPAL                                       */
/* ===================================================== */

QWidget {{
    background-color: {V['panel_light']};
    color: #000000;
}}

/* ===================================================== */
/* SIDEBAR                                               */
/* ===================================================== */

QWidget#sidebar {{
    background-color: {V['sidebar_light']};
    border-right: 3px solid {V['success_light']};
}}

QPushButton#menuButton {{
    background-color: #111111;
    color: #ffffff;
    border: none;
    padding: 14px;
    text-align: left;
    border-radius: 10px;
}}

QPushButton#menuButton:hover {{
    background-color: #1f1f1f;
}}

QPushButton#menuButton[active="true"] {{
    background-color: {V['menu_active_light']};
    color: #ffffff;
    font-weight: bold;
}}

/* ===================================================== */
/* TÍTULO                                                */
/* ===================================================== */

QLabel#pageTitle {{
    font-size: 22px;
    font-weight: bold;
    padding: 12px 0;
}}

/* ===================================================== */
/* CONTAINERS (CARD)                                     */
/* ===================================================== */

QGroupBox {{
    background-color: {V['panel_light']};
    border: 2px solid {V['border_light']};
    border-radius: 16px;
    margin-top: 18px;
    padding: 20px;
}}

QGroupBox::title {{
    padding: 6px;
    font-weight: bold;
}}

/* ===================================================== */
/* INPUTS                                                */
/* ===================================================== */

QLineEdit, QComboBox, QDateEdit, QSpinBox {{
    background-color: #ffffff;
    border: 2px solid #d1d5db;
    border-radius: 12px;
    padding: 10px;
    min-height: 36px;
}}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
    border: 2px solid {V['success_light']};
}}

/* ===================================================== */
/* BOTÕES                                                */
/* ===================================================== */

QPushButton {{
    background-color: #000000;
    color: #ffffff;
    padding: 10px 16px;
    border-radius: 10px;
}}

QPushButton:hover {{
    background-color: #333333;
}}

QPushButton#primaryButton {{
    background-color: {V['success_light']};
    border-radius: 18px;
    padding: 12px;
    font-weight: 600;
    min-height: 40px;
}}

QPushButton#primaryButton:hover {{
    background-color: #15803d;
}}

QPushButton#addButton {{
    background-color: {V['success_light']};
}}

QPushButton#deleteButton {{
    background-color: {V['danger_light']};
}}

QPushButton#secondaryButton {{
    background-color: {V['highlight_light']};
    color: #000000;
}}

/* ===================================================== */
/* TABELAS                                               */
/* ===================================================== */

QTableWidget {{
    background-color: #ffffff;
    gridline-color: #e0e0e0;
}}

QHeaderView::section {{
    background-color: #f5f5f5;
    border: 1px solid #dddddd;
    padding: 6px;
}}

/* ===================================================== */
/* PROGRESS                                              */
/* ===================================================== */

QProgressBar {{
    border: 1px solid #c0c0c0;
    border-radius: 8px;
    background-color: #eeeeee;
    height: 16px;
}}

QProgressBar::chunk {{
    background-color: {V['success_light']};
}}

/* ===================================================== */
/* CORES FINANCEIRAS                                     */
/* ===================================================== */

QLabel#positivo {{
    color: {V['success_light']};
    font-weight: bold;
}}

QLabel#negativo {{
    color: {V['danger_light']};
    font-weight: bold;
}}

QLabel#warning {{
    color: {V['warning_light']};
    font-weight: bold;
}}

QLabel#muted {{
    color: {V['muted_light']};
}}
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
    text-align: left;
    border-radius: 10px;
}}

QPushButton#menuButton:hover {{
    background-color: {V['highlight_dark']};
}}

QPushButton#menuButton[active="true"] {{
    background-color: {V['menu_active_dark']};
    color: black;
    font-weight: 600;
}}

QLabel#pageTitle {{
    font-size: 24px;
    font-weight: 700;
    margin: 14px 0;
}}

QGroupBox {{
    background-color: {V['panel_dark']};
    border: 2px solid {V['border_dark']};
    border-radius: 18px;
    margin-top: 20px;
    padding: 20px;
}}

QLineEdit, QComboBox, QDateEdit, QSpinBox {{
    background-color: {V['panel_dark']};
    border: 2px solid {V['border_dark']};
    border-radius: 12px;
    padding: 10px;
    min-height: 36px;
}}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
    border: 2px solid {V['primary_dark']};
}}

QPushButton {{
    background-color: {V['primary_dark']};
    color: black;
    border-radius: 12px;
    padding: 10px 16px;
}}

QPushButton:hover {{
    background-color: #2563eb;
}}

QPushButton#primaryButton {{
    background-color: {V['success_dark']};
    border-radius: 20px;
    padding: 12px;
    font-weight: 600;
    min-height: 40px;
}}

QPushButton#deleteButton {{
    background-color: {V['danger_dark']};
    color: black;
}}

QPushButton#secondaryButton {{
    background-color: {V['highlight_dark']};
    color: {V['text_dark']};
}}

QProgressBar {{
    background-color: {V['highlight_dark']};
    border-radius: 10px;
    height: 18px;
}}

QProgressBar::chunk {{
    background-color: {V['primary_dark']};
}}

QLabel#positivo {{
    color: {V['success_dark']};
    font-weight: 600;
}}

QLabel#negativo {{
    color: {V['danger_dark']};
    font-weight: 600;
}}

QLabel#warning {{
    color: {V['warning_dark']};
    font-weight: 600;
}}

QLabel#muted {{
    color: {V['muted_dark']};
}}
"""

# =========================================================
# MAPA
# =========================================================
THEMES = {
    "Claro": LIGHT,
    "Escuro": DARK,
}

# =========================================================
# FUNÇÃO SEGURA
# =========================================================
def get_theme(nome: str) -> str:
    tema = THEMES.get(nome)
    if not isinstance(tema, str) or not tema.strip():
        return LIGHT
    return tema
