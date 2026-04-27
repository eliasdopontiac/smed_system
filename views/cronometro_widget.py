from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class CronometroWidget(QWidget):
    """A self-contained stopwatch card with start / pause controls."""

    def __init__(self, titulo: str, cor: str = "#2563EB", parent=None):
        super().__init__(parent)
        self.titulo = titulo
        self.cor = cor
        self.tempo_decorrido = 0
        self.ativo = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self._build()

    # ── UI ────────────────────────────────────────────────────────────────
    def _build(self):
        self.setObjectName("CronCard")

        # Derive light-background version of the accent colour
        # We create a simple hex-lightened bg by hardcoding per-colour
        light_bg = {
            "#2563EB": "#EFF6FF",
            "#EA580C": "#FFF7ED",
            "#7C3AED": "#F5F3FF",
        }.get(self.cor, "#F8FAFC")

        self.setStyleSheet(
            f"QWidget#CronCard {{"
            f"  background-color: #FFFFFF;"
            f"  border: 1.5px solid #E2E8F0;"
            f"  border-top: 3px solid {self.cor};"
            f"  border-radius: 8px;"
            f"}}"
        )
        self.setMinimumWidth(160)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(6)

        # Title
        lbl_titulo = QLabel(self.titulo)
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet(
            f"color: {self.cor}; background: transparent; border: none;"
        )
        root.addWidget(lbl_titulo)

        # Time display
        self.display = QLabel("00:00:00")
        self.display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display.setFont(QFont("Courier New", 26, QFont.Weight.Bold))
        self.display.setMinimumHeight(46)
        self.display.setStyleSheet(
            f"color: {self.cor};"
            f"background-color: {light_bg};"
            f"border: 1px solid #E2E8F0;"
            f"border-radius: 6px;"
            f"padding: 4px 8px;"
        )
        root.addWidget(self.display)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        self.btn_iniciar = QPushButton("▶  Iniciar")
        self.btn_iniciar.setFixedHeight(30)
        self.btn_iniciar.clicked.connect(self.iniciar)
        self.btn_iniciar.setStyleSheet(
            "QPushButton {"
            "  background-color: #16A34A; color: #FFFFFF;"
            "  border: none; border-radius: 5px;"
            "  font-weight: 700; font-size: 10px; padding: 4px 10px;"
            "}"
            "QPushButton:hover { background-color: #15803D; }"
            "QPushButton:disabled { background-color: #E2E8F0; color: #94A3B8; }"
        )
        btn_row.addWidget(self.btn_iniciar)

        self.btn_pausar = QPushButton("⏸  Pausar")
        self.btn_pausar.setFixedHeight(30)
        self.btn_pausar.clicked.connect(self.pausar)
        self.btn_pausar.setEnabled(False)
        self.btn_pausar.setStyleSheet(
            "QPushButton {"
            "  background-color: #D97706; color: #FFFFFF;"
            "  border: none; border-radius: 5px;"
            "  font-weight: 700; font-size: 10px; padding: 4px 10px;"
            "}"
            "QPushButton:hover { background-color: #B45309; }"
            "QPushButton:disabled { background-color: #E2E8F0; color: #94A3B8; }"
        )
        btn_row.addWidget(self.btn_pausar)

        root.addLayout(btn_row)

    # ── Control API ───────────────────────────────────────────────────────
    def iniciar(self):
        if not self.ativo:
            self.ativo = True
            self.timer.start(1000)
            self.btn_iniciar.setEnabled(False)
            self.btn_pausar.setEnabled(True)

    def pausar(self):
        if self.ativo:
            self.ativo = False
            self.timer.stop()
            self.btn_iniciar.setEnabled(True)
            self.btn_pausar.setEnabled(False)
        else:
            self.iniciar()

    def reset(self):
        self.ativo = False
        self.timer.stop()
        self.tempo_decorrido = 0
        self.display.setText("00:00:00")
        self.btn_iniciar.setEnabled(True)
        self.btn_pausar.setEnabled(False)

    # ── Internals ─────────────────────────────────────────────────────────
    def _tick(self):
        if self.ativo:
            self.tempo_decorrido += 1
            h, rem = divmod(self.tempo_decorrido, 3600)
            m, s = divmod(rem, 60)
            self.display.setText(f"{h:02d}:{m:02d}:{s:02d}")

    def set_display_only(self):
        """Hide internal start/pause buttons — the parent widget controls the cronômetro."""
        self.btn_iniciar.setVisible(False)
        self.btn_pausar.setVisible(False)

    def get_tempo(self) -> int:
        return self.tempo_decorrido

    def get_tempo_formatado(self) -> str:
        h, rem = divmod(self.tempo_decorrido, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
