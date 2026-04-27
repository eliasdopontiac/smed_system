class Theme:
    # ─── Palette ──────────────────────────────────────────────────────────
    HEADER_BG = "#1B2A4A"  # dark navy — header & menu bar
    HEADER_BG2 = "#243553"  # slightly lighter for hover

    PRIMARY = "#2563EB"  # vibrant blue — primary actions
    PRIMARY_DARK = "#1D4ED8"
    PRIMARY_LIGHT = "#EFF6FF"
    PRIMARY_BORDER = "#BFDBFE"

    SUCCESS = "#16A34A"  # green — disponível / iniciar
    SUCCESS_DARK = "#15803D"
    SUCCESS_LIGHT = "#F0FDF4"
    SUCCESS_BORDER = "#86EFAC"

    WARNING = "#D97706"  # amber — pausar / paradas
    WARNING_DARK = "#B45309"
    WARNING_LIGHT = "#FFFBEB"
    WARNING_BORDER = "#FCD34D"

    DANGER = "#DC2626"  # red — finalizar
    DANGER_DARK = "#B91C1C"
    DANGER_LIGHT = "#FEF2F2"
    DANGER_BORDER = "#FCA5A5"

    PURPLE = "#7C3AED"  # violet — PCD
    PURPLE_DARK = "#6D28D9"
    PURPLE_LIGHT = "#F5F3FF"
    PURPLE_BORDER = "#C4B5FD"

    ORANGE = "#EA580C"  # orange — qualidade
    ORANGE_DARK = "#C2410C"
    ORANGE_LIGHT = "#FFF7ED"
    ORANGE_BORDER = "#FDBA74"

    # Neutrals
    BG_APP = "#F1F5F9"  # cool light gray app background
    BG_CARD = "#FFFFFF"  # pure white cards
    BG_SECTION = "#F8FAFC"  # slightly off-white sections
    BG_INPUT = "#FFFFFF"

    BORDER = "#E2E8F0"  # slate-200
    BORDER_MEDIUM = "#CBD5E1"  # slate-300
    BORDER_DARK = "#94A3B8"  # slate-400

    # Text
    TEXT_TITLE = "#0F172A"  # slate-900
    TEXT_BODY = "#334155"  # slate-700
    TEXT_MUTED = "#64748B"  # slate-500
    TEXT_FAINT = "#94A3B8"  # slate-400
    TEXT_WHITE = "#FFFFFF"
    TEXT_LIGHT = "#CBD5E1"  # light text on dark bg

    # ─── Button helpers ───────────────────────────────────────────────────
    @classmethod
    def _btn(
        cls,
        bg: str,
        hover: str,
        text: str = "#FFFFFF",
        radius: int = 6,
        pad: str = "7px 18px",
    ) -> str:
        return (
            f"QPushButton {{"
            f"  background-color: {bg}; color: {text};"
            f"  border: none; border-radius: {radius}px;"
            f"  padding: {pad}; font-weight: 700;"
            f"  font-size: 11px; font-family: 'Segoe UI', Arial;"
            f"  letter-spacing: 0.3px;"
            f"}}"
            f"QPushButton:hover {{ background-color: {hover}; }}"
            f"QPushButton:pressed {{ background-color: {hover}; }}"
            f"QPushButton:disabled {{"
            f"  background-color: #E2E8F0; color: #94A3B8;"
            f"}}"
        )

    @classmethod
    def get_botao_primario(cls) -> str:
        return cls._btn(cls.PRIMARY, cls.PRIMARY_DARK)

    @classmethod
    def get_botao_sucesso(cls) -> str:
        return cls._btn(cls.SUCCESS, cls.SUCCESS_DARK)

    @classmethod
    def get_botao_perigo(cls) -> str:
        return cls._btn(cls.DANGER, cls.DANGER_DARK)

    @classmethod
    def get_botao_aviso(cls) -> str:
        return cls._btn(cls.WARNING, cls.WARNING_DARK)

    @classmethod
    def get_botao_neutro(cls) -> str:
        return cls._btn("#475569", "#334155")

    # Back-compat aliases used by dialogs.py
    BOTAO_SUCESSO = property(lambda self: Theme.get_botao_sucesso())
    BOTAO_PERIGO = property(lambda self: Theme.get_botao_perigo())
    BOTAO_PRIMARIO = property(lambda self: Theme.get_botao_primario())

    # ─── Full application stylesheet ─────────────────────────────────────
    @classmethod
    def get_theme_light(cls) -> str:
        return f"""
/* ── Root containers ───────────────────────────────────────────────── */
QMainWindow {{
    background-color: {cls.BG_APP};
}}
QDialog {{
    background-color: {cls.BG_CARD};
}}

/* ── Default widget: transparent bg, explicit text colour ───────────── */
QWidget {{
    color: {cls.TEXT_BODY};
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 11px;
    background-color: transparent;
}}

/* ── Labels ─────────────────────────────────────────────────────────── */
QLabel {{
    color: {cls.TEXT_BODY};
    background-color: transparent;
    border: none;
}}

/* ── Line edits ─────────────────────────────────────────────────────── */
QLineEdit {{
    background-color: {cls.BG_INPUT};
    color: {cls.TEXT_TITLE};
    border: 1.5px solid {cls.BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
    min-height: 20px;
    selection-background-color: {cls.PRIMARY_LIGHT};
    selection-color: {cls.PRIMARY};
}}
QLineEdit:focus {{
    border: 1.5px solid {cls.PRIMARY};
    background-color: {cls.BG_INPUT};
}}
QLineEdit:disabled {{
    background-color: {cls.BG_SECTION};
    color: {cls.TEXT_MUTED};
    border-color: {cls.BORDER};
}}
QLineEdit[placeholderText] {{
    color: {cls.TEXT_FAINT};
}}

/* ── Buttons (global default) ───────────────────────────────────────── */
QPushButton {{
    background-color: {cls.PRIMARY};
    color: {cls.TEXT_WHITE};
    border: none;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 700;
    font-size: 11px;
    font-family: 'Segoe UI', Arial, sans-serif;
}}
QPushButton:hover {{
    background-color: {cls.PRIMARY_DARK};
}}
QPushButton:pressed {{
    background-color: {cls.PRIMARY_DARK};
}}
QPushButton:disabled {{
    background-color: #E2E8F0;
    color: #94A3B8;
}}

/* ── Menu bar ───────────────────────────────────────────────────────── */
QMenuBar {{
    background-color: {cls.HEADER_BG};
    color: {cls.TEXT_WHITE};
    padding: 2px 4px;
    spacing: 2px;
    border-bottom: none;
    font-size: 11px;
}}
QMenuBar::item {{
    background-color: transparent;
    color: {cls.TEXT_WHITE};
    padding: 6px 14px;
    border-radius: 4px;
}}
QMenuBar::item:selected, QMenuBar::item:pressed {{
    background-color: rgba(255, 255, 255, 0.18);
}}

/* ── Dropdown menus ─────────────────────────────────────────────────── */
QMenu {{
    background-color: {cls.BG_CARD};
    color: {cls.TEXT_BODY};
    border: 1px solid {cls.BORDER};
    border-radius: 8px;
    padding: 5px 4px;
}}
QMenu::item {{
    padding: 8px 22px 8px 14px;
    border-radius: 4px;
    color: {cls.TEXT_BODY};
    background-color: transparent;
}}
QMenu::item:selected {{
    background-color: {cls.PRIMARY_LIGHT};
    color: {cls.PRIMARY};
}}
QMenu::separator {{
    height: 1px;
    background: {cls.BORDER};
    margin: 4px 8px;
}}

/* ── Scroll bars ────────────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: {cls.BG_APP};
    width: 8px;
    border: none;
    border-radius: 4px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {cls.BORDER_MEDIUM};
    border-radius: 4px;
    min-height: 32px;
}}
QScrollBar::handle:vertical:hover {{
    background: {cls.BORDER_DARK};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
    background: none;
}}
QScrollBar:horizontal {{
    background: {cls.BG_APP};
    height: 8px;
    border: none;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {cls.BORDER_MEDIUM};
    border-radius: 4px;
    min-width: 32px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {cls.BORDER_DARK};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
    background: none;
}}

/* ── Status bar ─────────────────────────────────────────────────────── */
QStatusBar {{
    background-color: {cls.HEADER_BG};
    color: {cls.TEXT_LIGHT};
    border-top: none;
    padding: 0 8px;
    font-size: 11px;
}}
QStatusBar QLabel {{
    color: {cls.TEXT_LIGHT};
    background-color: transparent;
    border: none;
    padding: 0 6px;
}}

/* ── Group boxes ────────────────────────────────────────────────────── */
QGroupBox {{
    background-color: {cls.BG_CARD};
    color: {cls.TEXT_TITLE};
    border: 1.5px solid {cls.BORDER};
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 14px;
    padding-left: 8px;
    padding-right: 8px;
    font-weight: 700;
    font-size: 11px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: {cls.PRIMARY};
    background-color: {cls.BG_CARD};
    font-weight: 700;
}}

/* ── Table widget ───────────────────────────────────────────────────── */
QTableWidget {{
    background-color: {cls.BG_CARD};
    color: {cls.TEXT_BODY};
    border: 1px solid {cls.BORDER};
    border-radius: 6px;
    gridline-color: {cls.BORDER};
    outline: none;
    alternate-background-color: {cls.BG_SECTION};
}}
QTableWidget::item {{
    padding: 7px 10px;
    color: {cls.TEXT_BODY};
    border: none;
    background-color: transparent;
}}
QTableWidget::item:selected {{
    background-color: {cls.PRIMARY_LIGHT};
    color: {cls.PRIMARY};
}}
QTableCornerButton::section {{
    background-color: {cls.BG_SECTION};
    border: none;
}}
QHeaderView {{
    background-color: {cls.BG_SECTION};
}}
QHeaderView::section {{
    background-color: {cls.BG_SECTION};
    color: {cls.TEXT_TITLE};
    font-weight: 700;
    font-size: 11px;
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid {cls.BORDER_MEDIUM};
    border-right: 1px solid {cls.BORDER};
}}
QHeaderView::section:last {{
    border-right: none;
}}

/* ── List widget ────────────────────────────────────────────────────── */
QListWidget {{
    background-color: {cls.BG_CARD};
    color: {cls.TEXT_BODY};
    border: 1.5px solid {cls.BORDER};
    border-radius: 6px;
    outline: none;
    padding: 3px;
}}
QListWidget::item {{
    padding: 8px 12px;
    border-radius: 5px;
    color: {cls.TEXT_BODY};
    border: none;
}}
QListWidget::item:selected {{
    background-color: {cls.PRIMARY_LIGHT};
    color: {cls.PRIMARY};
}}
QListWidget::item:hover:!selected {{
    background-color: {cls.BG_SECTION};
}}

/* ── Dialog button box ──────────────────────────────────────────────── */
QDialogButtonBox QPushButton {{
    min-width: 90px;
    min-height: 32px;
    padding: 6px 18px;
}}

/* ── Scroll area ────────────────────────────────────────────────────── */
QScrollArea {{
    border: none;
    background-color: {cls.BG_APP};
}}
QScrollArea > QWidget > QWidget {{
    background-color: {cls.BG_APP};
}}

/* ── Tooltip ────────────────────────────────────────────────────────── */
QToolTip {{
    background-color: {cls.HEADER_BG};
    color: {cls.TEXT_WHITE};
    border: 1px solid {cls.HEADER_BG2};
    border-radius: 4px;
    padding: 5px 8px;
    font-size: 11px;
}}
        """
