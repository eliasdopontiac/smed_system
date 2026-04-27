from datetime import datetime
from typing import List

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QFont, QPalette
from PyQt6.QtGui import QColor as _QColor
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStatusBar,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from controllers.smed_controller import SmedController


def _force_white_palette(widget) -> None:
    """Força fundo branco via QPalette — ignora tema escuro do sistema."""
    from styles.theme import Theme as _T

    pal = widget.palette()
    white = _QColor(_T.BG_CARD)
    text = _QColor(_T.TEXT_BODY)
    pal.setColor(QPalette.ColorRole.Window, white)
    pal.setColor(QPalette.ColorRole.WindowText, text)
    pal.setColor(QPalette.ColorRole.Base, white)
    pal.setColor(QPalette.ColorRole.AlternateBase, _QColor(_T.BG_SECTION))
    pal.setColor(QPalette.ColorRole.Text, text)
    pal.setColor(QPalette.ColorRole.Button, white)
    pal.setColor(QPalette.ColorRole.ButtonText, text)
    widget.setPalette(pal)
    widget.setAutoFillBackground(True)


from models.maquina import Maquina
from styles.theme import Theme
from views.cronometro_widget import CronometroWidget
from views.dialogs import EstatisticasDialog, GerenciadorOperadoresDialog

# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _make_btn(
    text: str,
    bg: str,
    hover: str,
    text_color: str = "#FFFFFF",
    height: int = 34,
    radius: int = 6,
    font_size: int = 11,
) -> QPushButton:
    btn = QPushButton(text)
    btn.setMinimumHeight(height)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(
        f"QPushButton {{"
        f"  background-color: {bg}; color: {text_color};"
        f"  border: none; border-radius: {radius}px;"
        f"  font-weight: 700; font-size: {font_size}px;"
        f"  font-family: 'Segoe UI', Arial; padding: 6px 16px;"
        f"}}"
        f"QPushButton:hover {{ background-color: {hover}; }}"
        f"QPushButton:pressed {{ background-color: {hover}; }}"
        f"QPushButton:disabled {{ background-color: #E2E8F0; color: #94A3B8; }}"
    )
    return btn


# ─────────────────────────────────────────────────────────────────────────────
#  ParadaExternaWidget
# ─────────────────────────────────────────────────────────────────────────────


class ParadaExternaWidget(QFrame):
    removida = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tempo_decorrido = 0
        self.ativo = False
        self.finalizado = False
        self.inicio = None
        self.fim = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self._build()

    # ── UI ────────────────────────────────────────────────────────────────
    def _build(self):
        self.setObjectName("ParadaCard")
        self.setStyleSheet(
            "QFrame#ParadaCard {"
            f"  background-color: {Theme.WARNING_LIGHT};"
            f"  border: 1px solid {Theme.WARNING_BORDER};"
            f"  border-left: 3px solid {Theme.WARNING};"
            "  border-radius: 6px;"
            "}"
        )
        self.setMaximumHeight(76)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 6, 10, 6)
        root.setSpacing(4)

        # ── Top row
        top = QHBoxLayout()
        top.setSpacing(8)

        ico = QLabel("⏸")
        ico.setStyleSheet(
            f"color: {Theme.WARNING}; background: transparent; border: none; font-size: 13px;"
        )
        top.addWidget(ico)

        lbl = QLabel("Parada")
        lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        lbl.setStyleSheet(
            f"color: {Theme.WARNING_DARK}; background: transparent; border: none;"
        )
        top.addWidget(lbl)

        self.display = QLabel("00:00:00")
        self.display.setFont(QFont("Courier New", 13, QFont.Weight.Bold))
        self.display.setStyleSheet(
            f"color: {Theme.WARNING}; background: transparent; border: none; min-width: 72px;"
        )
        top.addWidget(self.display)

        top.addStretch()

        # Mini action buttons — criados individualmente para renderização confiável dos ícones
        def _mini(label, bg, hov, enabled=True):
            b = QPushButton(label)
            b.setFixedSize(38, 26)
            b.setEnabled(enabled)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(
                f"QPushButton {{"
                f"  background-color: {bg}; color: #FFF; border: none; border-radius: 4px;"
                f"  font-size: 13px; font-weight: 700;"
                f"  font-family: 'Segoe UI Symbol', 'Arial Unicode MS', Arial;"
                f"}}"
                f"QPushButton:hover {{ background-color: {hov}; }}"
                f"QPushButton:disabled {{ background-color: #E2E8F0; color: #94A3B8; }}"
            )
            return b

        self._btn_ini = _mini("▶", "#16A34A", "#15803D", enabled=True)
        self._btn_pau = _mini("⏸", "#D97706", "#B45309", enabled=False)
        self._btn_fin = _mini("⏹", "#DC2626", "#B91C1C", enabled=False)

        self._btn_ini.clicked.connect(self._iniciar)
        self._btn_pau.clicked.connect(self._pausar)
        self._btn_fin.clicked.connect(self._finalizar)

        for b in (self._btn_ini, self._btn_pau, self._btn_fin):
            top.addWidget(b)

        root.addLayout(top)

        # ── Motivo row (hidden until finalizado)
        self._row_motivo = QFrame()
        self._row_motivo.setVisible(False)
        self._row_motivo.setStyleSheet("border: none; background: transparent;")
        ml = QHBoxLayout(self._row_motivo)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(6)

        lbl_m = QLabel("Motivo:")
        lbl_m.setStyleSheet(
            f"color: {Theme.TEXT_MUTED}; background: transparent; border: none; font-size: 10px;"
        )
        ml.addWidget(lbl_m)

        self.descricao_input = QLineEdit()
        self.descricao_input.setPlaceholderText("Descreva o motivo da parada…")
        self.descricao_input.setMaximumHeight(24)
        self.descricao_input.setStyleSheet(
            f"background-color: #FFFFFF; color: {Theme.TEXT_BODY};"
            f"border: 1px solid {Theme.BORDER}; border-radius: 4px;"
            f"padding: 2px 8px; font-size: 10px;"
        )
        ml.addWidget(self.descricao_input)

        root.addWidget(self._row_motivo)

    # ── Controls ──────────────────────────────────────────────────────────
    def _iniciar(self):
        if not self.ativo and not self.finalizado:
            self.ativo = True
            # Só reseta o tempo na primeira vez; se já pausado, continua de onde parou
            if self.inicio is None:
                self.inicio = datetime.now()
                self.tempo_decorrido = 0
            self.timer.start(1000)
            self._btn_ini.setEnabled(False)
            self._btn_pau.setEnabled(True)
            self._btn_fin.setEnabled(True)

    def _pausar(self):
        if self.ativo:
            self.ativo = False
            self.timer.stop()
            self._btn_ini.setEnabled(True)
            self._btn_pau.setEnabled(False)
        # else omitido: botão fica desabilitado quando inativo, então este ramo nunca ocorre

    def _finalizar(self):
        if self.ativo:
            self.ativo = False
            self.finalizado = True
            self.timer.stop()
            self.fim = datetime.now()
            self._btn_ini.setEnabled(False)
            self._btn_pau.setEnabled(False)
            self._btn_fin.setEnabled(False)
            self.setMaximumHeight(120)
            self._row_motivo.setVisible(True)
            self.descricao_input.setFocus()

    def _tick(self):
        if self.ativo:
            self.tempo_decorrido += 1
            h, r = divmod(self.tempo_decorrido, 3600)
            m, s = divmod(r, 60)
            self.display.setText(f"{h:02d}:{m:02d}:{s:02d}")

    def get_tempo(self) -> int:
        return self.tempo_decorrido

    def get_dados(self) -> dict:
        return {
            "descricao": self.descricao_input.text() if self.finalizado else "",
            "tempo": self.tempo_decorrido,
            "inicio": self.inicio.strftime("%H:%M:%S") if self.inicio else "",
            "fim": self.fim.strftime("%H:%M:%S") if self.fim else "",
        }


# ─────────────────────────────────────────────────────────────────────────────
#  BlocoMaquina
# ─────────────────────────────────────────────────────────────────────────────


class BlocoMaquina(QFrame):
    removido = pyqtSignal(object)
    iniciar_atividade = pyqtSignal(object)

    # Status → accent colour
    _STATUS_COLOR = {
        "Disponível": Theme.SUCCESS,
        "Em Setup": Theme.PRIMARY,
        "Pausado": Theme.WARNING,
    }

    def __init__(self, maquina: Maquina, parent=None):
        super().__init__(parent)
        self.maquina = maquina
        self.atividade_atual = None
        self.paradas_externas: List[ParadaExternaWidget] = []
        self._pausado = False  # flag dedicada: True = cronômetro principal pausado
        self._build()

    # ── Build ─────────────────────────────────────────────────────────────
    def _build(self):
        self.setObjectName("BlocoMaquina")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Inner card (white) ── ─────────────────────────────────────────
        self._card = QFrame()
        self._card.setObjectName("CardInner")
        self._card.setStyleSheet(
            "QFrame#CardInner {"
            "  background-color: #FFFFFF;"
            "  border: 1px solid #E2E8F0;"
            "  border-radius: 10px;"
            "}"
        )
        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(10)

        # ── Header row ────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(10)

        # Left accent stripe (a thin colored QFrame)
        self._stripe = QFrame()
        self._stripe.setObjectName("StatusStripe")
        self._stripe.setFixedWidth(4)
        self._stripe.setMinimumHeight(24)
        hdr.addWidget(self._stripe)

        # Machine name
        self.lbl_titulo = QLabel(f"🏭  {self.maquina.nome}")
        self.lbl_titulo.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.lbl_titulo.setStyleSheet(
            f"color: {Theme.TEXT_TITLE}; background: transparent; border: none;"
        )
        hdr.addWidget(self.lbl_titulo)

        # Descrição da atividade — destaque como "nome" da atividade
        self._lbl_descricao = QLabel()
        self._lbl_descricao.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self._lbl_descricao.setStyleSheet(
            f"color: {Theme.PRIMARY}; background: transparent; border: none;"
        )
        self._lbl_descricao.setVisible(False)
        hdr.addWidget(self._lbl_descricao)

        # Status badge
        self.lbl_status = QLabel()
        self.lbl_status.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr.addWidget(self.lbl_status)

        hdr.addStretch()

        # Timestamps (shown only during/after activity)
        self.lbl_inicio = QLabel()
        self.lbl_inicio.setFont(QFont("Segoe UI", 9))
        self.lbl_inicio.setVisible(False)
        self.lbl_inicio.setStyleSheet(
            f"color: {Theme.SUCCESS}; background: transparent; border: none;"
        )
        hdr.addWidget(self.lbl_inicio)

        self.lbl_fim = QLabel()
        self.lbl_fim.setFont(QFont("Segoe UI", 9))
        self.lbl_fim.setVisible(False)
        self.lbl_fim.setStyleSheet(
            f"color: {Theme.DANGER}; background: transparent; border: none;"
        )
        hdr.addWidget(self.lbl_fim)

        # Close button — X
        self._btn_close = QPushButton("×")
        self._btn_close.setFixedSize(28, 28)
        self._btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_close.setToolTip("Remover máquina")
        self._btn_close.clicked.connect(lambda: self.removido.emit(self))
        self._btn_close.setStyleSheet(
            "QPushButton {"
            "  background-color: #F1F5F9;"
            "  color: #1E293B;"
            "  border: 1.5px solid #CBD5E1;"
            "  border-radius: 6px;"
            "  font-size: 16px;"
            "  font-weight: 700;"
            "  font-family: Arial, 'Segoe UI', sans-serif;"
            "}"
            "QPushButton:hover { background-color: #FEF2F2; color: #DC2626; border-color: #FECACA; }"
        )
        hdr.addWidget(self._btn_close)
        card_layout.addLayout(hdr)

        # Thin separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(
            f"background-color: {Theme.BORDER}; border: none; max-height: 1px;"
        )
        card_layout.addWidget(sep)

        # ── Form panel ────────────────────────────────────────────────────
        self._frame_form = QFrame()
        self._frame_form.setObjectName("FrameForm")
        self._frame_form.setStyleSheet(
            "QFrame#FrameForm {"
            f"  background-color: {Theme.BG_SECTION};"
            f"  border: 1px solid {Theme.BORDER};"
            "  border-radius: 8px;"
            "}"
        )
        fl = QHBoxLayout(self._frame_form)
        fl.setContentsMargins(12, 8, 12, 8)
        fl.setSpacing(10)

        self.descricao_input = QLineEdit()
        self.descricao_input.setPlaceholderText("Descrição da atividade…")
        self.descricao_input.setMinimumHeight(36)
        self.descricao_input.setStyleSheet(
            f"background-color: #FFFFFF; color: {Theme.TEXT_TITLE};"
            f"border: 1.5px solid {Theme.BORDER}; border-radius: 6px;"
            f"padding: 6px 10px; font-size: 12px;"
            f"selection-background-color: {Theme.PRIMARY_LIGHT};"
        )
        fl.addWidget(self.descricao_input, stretch=3)

        self.responsavel_input = QLineEdit()
        self.responsavel_input.setPlaceholderText("Responsável")
        self.responsavel_input.setMinimumHeight(36)
        self.responsavel_input.setMaximumWidth(180)
        self.responsavel_input.setStyleSheet(
            f"background-color: #FFFFFF; color: {Theme.TEXT_TITLE};"
            f"border: 1.5px solid {Theme.BORDER}; border-radius: 6px;"
            f"padding: 6px 10px; font-size: 12px;"
            f"selection-background-color: {Theme.PRIMARY_LIGHT};"
        )
        fl.addWidget(self.responsavel_input, stretch=1)

        self._btn_iniciar = _make_btn(
            "▶  INICIAR", Theme.SUCCESS, Theme.SUCCESS_DARK, height=36, font_size=11
        )
        self._btn_iniciar.setMinimumWidth(110)
        self._btn_iniciar.clicked.connect(self._on_iniciar)
        fl.addWidget(self._btn_iniciar)

        card_layout.addWidget(self._frame_form)

        # ── Cronômetros panel ─────────────────────────────────────────────
        self._frame_cron = QFrame()
        self._frame_cron.setObjectName("FrameCron")
        self._frame_cron.setStyleSheet(
            "QFrame#FrameCron { background: transparent; border: none; }"
        )
        self._frame_cron.setVisible(False)
        cl = QHBoxLayout(self._frame_cron)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(8)

        self.cron_principal = CronometroWidget("Atividade", Theme.PRIMARY)
        self.cron_qualidade = CronometroWidget("Qualidade", Theme.ORANGE)
        self.cron_pcd = CronometroWidget("PCD", Theme.PURPLE)

        for c in (self.cron_principal, self.cron_qualidade, self.cron_pcd):
            c.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            cl.addWidget(c)

        card_layout.addWidget(self._frame_cron)

        # ── Paradas externas panel ────────────────────────────────────────
        self._frame_paradas = QFrame()
        self._frame_paradas.setObjectName("FrameParadas")
        self._frame_paradas.setStyleSheet(
            "QFrame#FrameParadas { background: transparent; border: none; }"
        )
        self._frame_paradas.setVisible(False)
        pl = QVBoxLayout(self._frame_paradas)
        pl.setContentsMargins(0, 0, 0, 0)
        pl.setSpacing(5)

        ph = QHBoxLayout()
        ph.setSpacing(8)

        ico_p = QLabel("⏸")
        ico_p.setStyleSheet(
            f"color: {Theme.WARNING}; background: transparent; border: none; font-size: 12px;"
        )
        ph.addWidget(ico_p)

        lbl_p = QLabel("Paradas Externas")
        lbl_p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl_p.setStyleSheet(
            f"color: {Theme.WARNING_DARK}; background: transparent; border: none;"
        )
        ph.addWidget(lbl_p)
        ph.addStretch()

        btn_add_p = _make_btn(
            "+ Parada", Theme.WARNING, Theme.WARNING_DARK, height=28, font_size=10
        )
        btn_add_p.clicked.connect(self._add_parada)
        ph.addWidget(btn_add_p)
        pl.addLayout(ph)

        self._container_paradas = QWidget()
        self._container_paradas.setStyleSheet("background: transparent;")
        self._layout_paradas = QVBoxLayout(self._container_paradas)
        self._layout_paradas.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._layout_paradas.setSpacing(4)
        self._layout_paradas.setContentsMargins(0, 0, 0, 0)
        pl.addWidget(self._container_paradas)
        card_layout.addWidget(self._frame_paradas)

        # ── Controls row (PAUSAR / FINALIZAR) ────────────────────────────
        self._frame_ctrl = QFrame()
        self._frame_ctrl.setObjectName("FrameCtrl")
        self._frame_ctrl.setStyleSheet(
            "QFrame#FrameCtrl { background: transparent; border: none; }"
        )
        self._frame_ctrl.setVisible(False)
        ctrl = QHBoxLayout(self._frame_ctrl)
        ctrl.setContentsMargins(0, 0, 0, 0)
        ctrl.setSpacing(8)

        self._btn_pausar = _make_btn(
            "⏸  PAUSAR", Theme.WARNING, Theme.WARNING_DARK, height=38, font_size=11
        )
        self._btn_pausar.setMinimumWidth(130)
        self._btn_pausar.clicked.connect(self._on_pausar)
        ctrl.addWidget(self._btn_pausar)

        self._btn_finalizar = _make_btn(
            "⏹  FINALIZAR", Theme.DANGER, Theme.DANGER_DARK, height=38, font_size=11
        )
        self._btn_finalizar.setMinimumWidth(130)
        self._btn_finalizar.clicked.connect(self._on_finalizar)
        ctrl.addStretch()
        ctrl.addWidget(self._btn_finalizar)

        card_layout.addWidget(self._frame_ctrl)

        # ── Resumo panel ──────────────────────────────────────────────────
        self._frame_resumo = QFrame()
        self._frame_resumo.setObjectName("FrameResumo")
        self._frame_resumo.setStyleSheet(
            "QFrame#FrameResumo {"
            f"  background-color: {Theme.SUCCESS_LIGHT};"
            f"  border: 1.5px solid {Theme.SUCCESS_BORDER};"
            f"  border-left: 4px solid {Theme.SUCCESS};"
            "  border-radius: 8px;"
            "}"
        )
        self._frame_resumo.setVisible(False)
        rl = QVBoxLayout(self._frame_resumo)
        rl.setContentsMargins(14, 10, 14, 10)
        rl.setSpacing(5)

        self._lbl_resumo = QLabel()
        self._lbl_resumo.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self._lbl_resumo.setStyleSheet(
            f"color: {Theme.SUCCESS_DARK}; background: transparent; border: none;"
        )
        self._lbl_resumo.setWordWrap(True)
        rl.addWidget(self._lbl_resumo)

        self._lbl_resumo_det = QLabel()
        self._lbl_resumo_det.setFont(QFont("Segoe UI", 10))
        self._lbl_resumo_det.setStyleSheet(
            f"color: {Theme.TEXT_MUTED}; background: transparent; border: none;"
        )
        self._lbl_resumo_det.setWordWrap(True)
        rl.addWidget(self._lbl_resumo_det)

        # Resumo bottom row — horários apenas, sem botão de nova atividade
        resumo_btns = QHBoxLayout()
        resumo_btns.setSpacing(8)

        self._lbl_horarios = QLabel()
        self._lbl_horarios.setFont(QFont("Segoe UI", 9))
        self._lbl_horarios.setStyleSheet(
            f"color: {Theme.TEXT_MUTED}; background: transparent; border: none;"
        )
        resumo_btns.addWidget(self._lbl_horarios)
        rl.addLayout(resumo_btns)

        card_layout.addWidget(self._frame_resumo)

        root.addWidget(self._card)
        self._update_style()

    # ── Style update ──────────────────────────────────────────────────────
    def _update_style(self):
        cor = self._STATUS_COLOR.get(self.maquina.status, Theme.BORDER_MEDIUM)

        # Outer wrapper: just a margin container, transparent
        self.setObjectName("BlocoMaquina")
        self.setStyleSheet(
            "QFrame#BlocoMaquina { background: transparent; border: none; margin: 3px 6px; }"
        )

        # Card left border changes with status
        self._card.setStyleSheet(
            "QFrame#CardInner {"
            "  background-color: #FFFFFF;"
            f"  border: 1px solid #E2E8F0;"
            f"  border-left: 4px solid {cor};"
            "  border-radius: 10px;"
            "}"
        )

        # Accent stripe (visible in header row)
        self._stripe.setStyleSheet(
            f"QFrame#StatusStripe {{"
            f"  background-color: {cor};"
            f"  border: none; border-radius: 2px;"
            f"}}"
        )

        # Status badge
        self.lbl_status.setText(f"  {self.maquina.status}  ")
        self.lbl_status.setStyleSheet(
            f"color: {cor}; background-color: transparent;"
            f"border: 1.5px solid {cor}; border-radius: 10px;"
            f"font-size: 9px; font-weight: 700; padding: 2px 6px;"
        )

    # ── Slots ─────────────────────────────────────────────────────────────
    def _add_parada(self):
        p = ParadaExternaWidget()
        self._layout_paradas.addWidget(p)
        self.paradas_externas.append(p)

    def _on_iniciar(self):
        d = self.descricao_input.text().strip()
        r = self.responsavel_input.text().strip()
        if not d or not r:
            _WhiteMessageBox.warning(
                self,
                "Campos obrigatórios",
                "Preencha a descrição da atividade e o nome do responsável.",
            )
            return
        self.iniciar_atividade.emit(self)

    def iniciar_cronometros(self):
        agora = datetime.now()
        self.lbl_inicio.setText(f"▶ Início {agora.strftime('%H:%M:%S')}")
        self.lbl_inicio.setVisible(True)
        self.lbl_fim.setVisible(False)

        self._frame_form.setVisible(False)
        self._frame_cron.setVisible(True)
        self._frame_paradas.setVisible(True)
        self._frame_ctrl.setVisible(True)
        self._frame_resumo.setVisible(False)

        # Oculta apenas os botões do cron principal — BlocoMaquina tem o botão PAUSAR para ele.
        # Qualidade e PCD mantêm seus próprios botões para controle independente.
        self.cron_principal.set_display_only()

        self._pausado = False
        self.cron_principal.iniciar()
        # Qualidade e PCD NÃO são iniciados automaticamente — o usuário controla
        self.maquina.status = "Em Setup"

        # Mostra a descrição da atividade no cabeçalho do bloco
        self._lbl_descricao.setText(f"—  {self.descricao_input.text()}")
        self._lbl_descricao.setVisible(True)

        self._update_style()

    def _on_pausar(self):
        if not self._pausado:
            # Rodando → pausar todos os cronômetros da atividade
            for c in (self.cron_principal, self.cron_qualidade, self.cron_pcd):
                if c.ativo:
                    c.timer.stop()
                    c.ativo = False
            if self.atividade_atual:
                self.atividade_atual.pausar()  # sincroniza status no model
            self._btn_pausar.setText("▶  RETOMAR")
            self._btn_pausar.setStyleSheet(
                _make_btn("", Theme.SUCCESS, Theme.SUCCESS_DARK).styleSheet()
            )
            self.maquina.status = "Pausado"
            self._pausado = True
        else:
            # Pausado → retomar apenas os que estavam ativos antes
            # O cron principal sempre retoma; qualidade e PCD só se já tinham sido iniciados
            self.cron_principal.ativo = True
            self.cron_principal.timer.start(1000)
            for c in (self.cron_qualidade, self.cron_pcd):
                if c.tempo_decorrido > 0:
                    c.ativo = True
                    c.timer.start(1000)
            if self.atividade_atual:
                self.atividade_atual.retomar()  # sincroniza status no model
            self._btn_pausar.setText("⏸  PAUSAR")
            self._btn_pausar.setStyleSheet(
                _make_btn("", Theme.WARNING, Theme.WARNING_DARK).styleSheet()
            )
            self.maquina.status = "Em Setup"
            self._pausado = False
        self._update_style()

    def _on_finalizar(self):
        if self.maquina.status not in ("Em Setup", "Pausado"):
            return

        resp = _WhiteMessageBox.question(
            self,
            "Confirmar finalização",
            "Deseja finalizar a atividade atual?\n\nOs cronômetros serão parados e o resumo exibido.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return

        agora = datetime.now()
        self.lbl_fim.setText(f"⏹ Fim {agora.strftime('%H:%M:%S')}")
        self.lbl_fim.setVisible(True)

        tp = self.cron_principal.get_tempo()
        tq = self.cron_qualidade.get_tempo()
        tpc = self.cron_pcd.get_tempo()

        if self.atividade_atual:
            self.atividade_atual.cronometro_principal.tempo_decorrido = tp
            self.atividade_atual.cronometro_qualidade.tempo_decorrido = tq
            self.atividade_atual.cronometro_pcd.tempo_decorrido = tpc
            self.atividade_atual.finalizar()  # sets status="Concluído" + fim
            self.atividade_atual.fim = agora  # precise timestamp
            self.maquina.finalizar_atividade(tp)  # increment counter

        # Stop all timers
        for c in (self.cron_principal, self.cron_qualidade, self.cron_pcd):
            c.timer.stop()
            c.ativo = False

        self.maquina.status = "Disponível"

        # Build resumo text
        h, rem = divmod(tp, 3600)
        m, s = divmod(rem, 60)
        qm, qs = divmod(tq, 60)
        pm, ps = divmod(tpc, 60)

        self._lbl_resumo.setText(
            f"✅  Atividade concluída  —  "
            f"⏱ {h:02d}:{m:02d}:{s:02d}  |  "
            f"🔍 Qualidade {qm:02d}:{qs:02d}  |  "
            f"📐 PCD {pm:02d}:{ps:02d}"
        )

        # Paradas summary
        paradas_ok = [p for p in self.paradas_externas if p.finalizado]
        if paradas_ok:
            partes = []
            for p in paradas_ok:
                d = p.get_dados()
                motivo = d["descricao"] or "Sem motivo"
                pm2, ps2 = divmod(d["tempo"], 60)
                partes.append(f"⏸ {motivo} ({pm2:02d}:{ps2:02d})")
            self._lbl_resumo_det.setText("Paradas:  " + "   |   ".join(partes))
        else:
            self._lbl_resumo_det.setText("Nenhuma parada externa registrada.")

        self._lbl_horarios.setText(
            f"Início: {self.lbl_inicio.text().replace('▶ Início ', '')}   "
            f"Fim: {agora.strftime('%H:%M:%S')}"
        )

        # Swap visible panels
        self._frame_cron.setVisible(False)
        self._frame_paradas.setVisible(False)
        self._frame_ctrl.setVisible(False)
        self._frame_resumo.setVisible(True)

        self._update_style()
        # Cronômetros NÃO são zerados — os valores ficam disponíveis para exportação


# ─────────────────────────────────────────────────────────────────────────────
#  MainWindow
# ─────────────────────────────────────────────────────────────────────────────


class _WhiteMessageBox(QMessageBox):
    """QMessageBox com fundo sempre branco (ignora dark mode do sistema)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _force_white_palette(self)
        self.setStyleSheet(Theme.get_theme_light())

    @staticmethod
    def question(
        parent,
        title,
        text,
        buttons=QMessageBox.StandardButton.Ok,
        default=QMessageBox.StandardButton.Ok,
    ):
        box = _WhiteMessageBox(parent)
        box.setWindowTitle(title)
        box.setText(text)
        box.setStandardButtons(buttons)
        box.setDefaultButton(default)
        box.setIcon(QMessageBox.Icon.Question)
        return box.exec()

    @staticmethod
    def warning(parent, title, text):
        box = _WhiteMessageBox(parent)
        box.setWindowTitle(title)
        box.setText(text)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.setIcon(QMessageBox.Icon.Warning)
        box.exec()

    @staticmethod
    def critical(parent, title, text):
        box = _WhiteMessageBox(parent)
        box.setWindowTitle(title)
        box.setText(text)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.setIcon(QMessageBox.Icon.Critical)
        box.exec()

    @staticmethod
    def about(parent, title, text):
        box = _WhiteMessageBox(parent)
        box.setWindowTitle(title)
        box.setText(text)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.setIcon(QMessageBox.Icon.Information)
        box.exec()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = SmedController()
        self.setWindowTitle("SMED — Controle de Atividades")
        self.setMinimumSize(900, 640)
        self.resize(1140, 760)
        self.blocos: List[BlocoMaquina] = []
        self._setup_menu()
        self._setup_ui()
        self._setup_statusbar()
        self.setStyleSheet(Theme.get_theme_light())
        _force_white_palette(self)

    # ── Menu ──────────────────────────────────────────────────────────────
    def _setup_menu(self):
        bar = self.menuBar()

        arq = bar.addMenu("&Arquivo")
        arq.addAction(
            QAction("&Nova Máquina", self, shortcut="Ctrl+N", triggered=self._add_bloco)
        )
        arq.addAction(
            QAction(
                "📊  &Exportar Relatório",
                self,
                shortcut="Ctrl+E",
                triggered=self._exportar,
            )
        )
        arq.addSeparator()
        arq.addAction(QAction("&Sair", self, shortcut="Ctrl+Q", triggered=self.close))

        ger = bar.addMenu("&Gerenciar")
        ger.addAction(QAction("&Responsáveis", self, triggered=self._gerenciar_resp))

        vis = bar.addMenu("&Visualizar")
        vis.addAction(
            QAction(
                "&Estatísticas", self, shortcut="Ctrl+T", triggered=self._estatisticas
            )
        )

        hlp = bar.addMenu("&Ajuda")
        hlp.addAction(QAction("&Sobre", self, triggered=self._sobre))

    # ── UI ────────────────────────────────────────────────────────────────
    def _setup_ui(self):
        central = QWidget()
        central.setObjectName("CentralWidget")
        central.setStyleSheet(
            f"QWidget#CentralWidget {{ background-color: {Theme.BG_APP}; }}"
        )
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ────────────────────────────────────────────────────
        header = QFrame()
        header.setObjectName("HeaderBar")
        header.setFixedHeight(64)
        header.setStyleSheet(
            f"QFrame#HeaderBar {{"
            f"  background-color: {Theme.HEADER_BG};"
            f"  border: none;"
            f"}}"
        )
        hbl = QHBoxLayout(header)
        hbl.setContentsMargins(20, 0, 20, 0)
        hbl.setSpacing(16)

        # Logo + titles
        title_col = QVBoxLayout()
        title_col.setSpacing(1)

        lbl_app = QLabel("SMED")
        lbl_app.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        lbl_app.setStyleSheet(
            f"color: {Theme.TEXT_WHITE}; background: transparent; border: none;"
        )
        title_col.addWidget(lbl_app)

        lbl_sub = QLabel("Sistema de Controle de Atividades")
        lbl_sub.setFont(QFont("Segoe UI", 9))
        lbl_sub.setStyleSheet(
            f"color: {Theme.TEXT_LIGHT}; background: transparent; border: none;"
        )
        title_col.addWidget(lbl_sub)

        hbl.addLayout(title_col)
        hbl.addStretch()

        # Header action buttons
        btn_exp = QPushButton("📊  Exportar")
        btn_exp.setMinimumSize(120, 36)
        btn_exp.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_exp.clicked.connect(self._exportar)
        btn_exp.setToolTip("Exportar relatório CSV (Ctrl+E)")
        btn_exp.setStyleSheet(
            "QPushButton {"
            "  background-color: rgba(255,255,255,0.12);"
            f"  color: {Theme.TEXT_WHITE};"
            "  border: 1px solid rgba(255,255,255,0.25);"
            "  border-radius: 6px; font-weight: 700; font-size: 11px;"
            "  padding: 6px 16px;"
            "}"
            "QPushButton:hover { background-color: rgba(255,255,255,0.22); }"
        )
        hbl.addWidget(btn_exp)

        btn_add = QPushButton("＋  Nova Máquina")
        btn_add.setMinimumSize(150, 36)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self._add_bloco)
        btn_add.setToolTip("Adicionar máquina (Ctrl+N)")
        btn_add.setStyleSheet(
            "QPushButton {"
            f"  background-color: {Theme.SUCCESS};"
            f"  color: {Theme.TEXT_WHITE};"
            "  border: none; border-radius: 6px;"
            "  font-weight: 700; font-size: 11px; padding: 6px 18px;"
            "}"
            f"QPushButton:hover {{ background-color: {Theme.SUCCESS_DARK}; }}"
        )
        hbl.addWidget(btn_add)

        root.addWidget(header)

        # ── Scroll area ────────────────────────────────────────────────────
        sa = QScrollArea()
        sa.setObjectName("MainScroll")
        sa.setWidgetResizable(True)
        sa.setStyleSheet(
            f"QScrollArea#MainScroll {{ border: none; background-color: {Theme.BG_APP}; }}"
        )

        self._container = QWidget()
        self._container.setObjectName("ScrollContainer")
        self._container.setStyleSheet(
            f"QWidget#ScrollContainer {{ background-color: {Theme.BG_APP}; }}"
        )
        self._lb = QVBoxLayout(self._container)
        self._lb.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._lb.setSpacing(2)
        self._lb.setContentsMargins(8, 10, 8, 16)

        sa.setWidget(self._container)
        root.addWidget(sa, stretch=1)

        # ── Empty state ────────────────────────────────────────────────────
        self._lbl_vazio = QFrame()
        self._lbl_vazio.setObjectName("EmptyState")
        self._lbl_vazio.setStyleSheet(
            "QFrame#EmptyState {"
            f"  background-color: {Theme.BG_CARD};"
            f"  border: 2px dashed {Theme.BORDER_MEDIUM};"
            "  border-radius: 12px;"
            "}"
        )
        es_layout = QVBoxLayout(self._lbl_vazio)
        es_layout.setContentsMargins(40, 50, 40, 50)
        es_layout.setSpacing(8)

        ico_lbl = QLabel("🏭")
        ico_lbl.setFont(QFont("Segoe UI", 36))
        ico_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico_lbl.setStyleSheet("background: transparent; border: none;")
        es_layout.addWidget(ico_lbl)

        tit_lbl = QLabel("Nenhuma máquina adicionada")
        tit_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        tit_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tit_lbl.setStyleSheet(
            f"color: {Theme.TEXT_TITLE}; background: transparent; border: none;"
        )
        es_layout.addWidget(tit_lbl)

        sub_lbl = QLabel(
            "Clique em  ＋ Nova Máquina  no cabeçalho ou pressione Ctrl+N\n"
            "para adicionar uma máquina e iniciar uma atividade SMED."
        )
        sub_lbl.setFont(QFont("Segoe UI", 11))
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_lbl.setWordWrap(True)
        sub_lbl.setStyleSheet(
            f"color: {Theme.TEXT_MUTED}; background: transparent; border: none;"
        )
        es_layout.addWidget(sub_lbl)

        btn_es = _make_btn(
            "＋  Adicionar Primeira Máquina",
            Theme.PRIMARY,
            Theme.PRIMARY_DARK,
            height=40,
            font_size=12,
        )
        btn_es.setMaximumWidth(300)
        btn_es.clicked.connect(self._add_bloco)
        es_layout.addSpacing(8)
        es_layout.addWidget(btn_es, alignment=Qt.AlignmentFlag.AlignCenter)

        self._lb.addWidget(self._lbl_vazio)

    # ── Status bar ────────────────────────────────────────────────────────
    def _setup_statusbar(self):
        sb = QStatusBar()
        self.setStatusBar(sb)

        self._sb_msg = QLabel("Pronto")
        sb.addWidget(self._sb_msg)

        self._sb_count = QLabel("Máquinas: 0")
        sb.addPermanentWidget(self._sb_count)

        sep = QLabel("  |  ")
        sep.setStyleSheet(
            f"color: {Theme.BORDER_MEDIUM}; border: none; background: transparent;"
        )
        sb.addPermanentWidget(sep)

        self._sb_hora = QLabel(datetime.now().strftime("%H:%M:%S"))
        sb.addPermanentWidget(self._sb_hora)

        self._timer_hora = QTimer(self)
        self._timer_hora.timeout.connect(
            lambda: self._sb_hora.setText(datetime.now().strftime("%H:%M:%S"))
        )
        self._timer_hora.start(1000)

    # ── Machine management ────────────────────────────────────────────────
    def _add_bloco(self):
        if self._lbl_vazio.isVisible():
            self._lb.removeWidget(self._lbl_vazio)
            self._lbl_vazio.setVisible(False)

        n = len(self.blocos) + 1
        maq = Maquina(id=n, nome=f"Máquina {n:02d}")
        b = BlocoMaquina(maq)
        b.removido.connect(self._rem_bloco)
        b.iniciar_atividade.connect(self._ini_bloco)

        self._lb.addWidget(b)
        self.blocos.append(b)
        self.controller.adicionar_maquina(maq)

        self._sb_msg.setText(f"✅  {maq.nome} adicionada")
        self._sb_count.setText(f"Máquinas: {len(self.blocos)}")

    def _rem_bloco(self, b: BlocoMaquina):
        resp = _WhiteMessageBox.question(
            self,
            "Remover máquina",
            f"Remover  {b.maquina.nome}  e todos os dados associados?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resp == QMessageBox.StandardButton.Yes:
            self._lb.removeWidget(b)
            self.blocos.remove(b)
            b.deleteLater()
            if not self.blocos:
                self._lb.addWidget(self._lbl_vazio)
                self._lbl_vazio.setVisible(True)
            self._sb_count.setText(f"Máquinas: {len(self.blocos)}")
            self._sb_msg.setText(f"🗑  {b.maquina.nome} removida")

    def _ini_bloco(self, b: BlocoMaquina):
        try:
            atv = self.controller.iniciar_atividade(
                b.maquina.id,
                b.descricao_input.text().strip(),
                b.responsavel_input.text().strip(),
                "Setup",
            )
            b.atividade_atual = atv
            b.iniciar_cronometros()
            self._sb_msg.setText(f"▶  Atividade iniciada em {b.maquina.nome}")
        except Exception as exc:
            _WhiteMessageBox.critical(self, "Erro ao iniciar", str(exc))

    # ── Export ────────────────────────────────────────────────────────────
    def _exportar(self):
        import csv
        import subprocess

        if not self.blocos:
            _WhiteMessageBox.warning(
                self, "Sem dados", "Adicione ao menos uma máquina antes de exportar."
            )
            return

        def _fmt(sec: int) -> str:
            h, r = divmod(sec, 3600)
            m, s = divmod(r, 60)
            return f"{h:02d}:{m:02d}:{s:02d}"

        dados = []
        for b in self.blocos:
            atv = b.atividade_atual
            concluida = atv is not None and atv.status == "Concluído"
            info = {
                "maquina": b.maquina.nome,
                "status": b.maquina.status,
                "descricao": atv.descricao
                if atv
                else (b.descricao_input.text() or "-"),
                "responsavel": atv.responsavel
                if atv
                else (b.responsavel_input.text() or "-"),
                "inicio": atv.inicio.strftime("%H:%M:%S")
                if (atv and atv.inicio)
                else "-",
                "fim": atv.fim.strftime("%H:%M:%S") if (atv and atv.fim) else "-",
                "tempo_total": _fmt(atv.cronometro_principal.tempo_decorrido)
                if concluida
                else "-",
                "tempo_qualidade": _fmt(atv.cronometro_qualidade.tempo_decorrido)
                if concluida
                else "-",
                "tempo_pcd": _fmt(atv.cronometro_pcd.tempo_decorrido)
                if concluida
                else "-",
                "paradas": " | ".join(
                    f"{p.get_dados()['descricao'] or 'Sem motivo'} ({p.get_tempo()}s)"
                    for p in b.paradas_externas
                    if p.finalizado
                )
                or "-",
            }
            dados.append(info)

        arquivo, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar relatório",
            f"relatorio_smed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV (*.csv)",
        )
        if not arquivo:
            return

        with open(arquivo, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(
                [
                    "Máquina",
                    "Status",
                    "Descrição",
                    "Responsável",
                    "Início",
                    "Fim",
                    "Tempo Total",
                    "Tempo Qualidade",
                    "Tempo PCD",
                    "Paradas",
                ]
            )
            for d in dados:
                w.writerow(
                    [
                        d["maquina"],
                        d["status"],
                        d["descricao"],
                        d["responsavel"],
                        d["inicio"],
                        d["fim"],
                        d["tempo_total"],
                        d["tempo_qualidade"],
                        d["tempo_pcd"],
                        d["paradas"],
                    ]
                )

        self._sb_msg.setText(f"✅  Exportado: {arquivo}")

        if (
            _WhiteMessageBox.question(
                self,
                "Exportação concluída",
                f"Relatório salvo em:\n{arquivo}\n\nDeseja abrir o arquivo?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        ):
            subprocess.Popen(["start", arquivo], shell=True)

    # ── Dialogs ───────────────────────────────────────────────────────────
    def _gerenciar_resp(self):
        dlg = GerenciadorOperadoresDialog(self.controller.get_responsaveis(), self)
        dlg.operadores_atualizados.connect(self.controller.atualizar_responsaveis)
        dlg.exec()

    def _estatisticas(self):
        EstatisticasDialog(self.controller, self).exec()

    def _sobre(self):
        _WhiteMessageBox.about(
            self,
            "Sobre — SMED System",
            "<b>SMED System v2.1</b><br><br>"
            "Sistema de controle de atividades SMED<br>"
            "com cronômetros independentes por máquina.<br><br>"
            "<small>Python 3.12 + PyQt6</small>",
        )
