from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from styles.theme import Theme

# ── Helpers ───────────────────────────────────────────────────────────────────


def _section_label(text: str, color: str = Theme.PRIMARY) -> QLabel:
    lbl = QLabel(text)
    lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(
        f"color: {color}; background-color: transparent; border: none; padding: 6px 0;"
    )
    return lbl


def _divider() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(
        f"background-color: {Theme.BORDER}; border: none; max-height: 1px;"
    )
    return line


# ── Gerenciador de Operadores ─────────────────────────────────────────────────


class GerenciadorOperadoresDialog(QDialog):
    operadores_atualizados = pyqtSignal(list)

    def __init__(self, operadores, parent=None):
        super().__init__(parent)
        self.operadores = list(operadores) if operadores else []
        self.setWindowTitle("Gerenciar Responsáveis")
        self.setModal(True)
        self.setMinimumSize(420, 500)
        self.setStyleSheet(Theme.get_theme_light())
        self._force_white_bg()
        self._build()

    def _force_white_bg(self):
        """Força fundo branco via QPalette, ignorando o tema escuro do sistema."""
        pal = self.palette()
        white = QColor(Theme.BG_CARD)
        text = QColor(Theme.TEXT_BODY)
        pal.setColor(QPalette.ColorRole.Window, white)
        pal.setColor(QPalette.ColorRole.WindowText, text)
        pal.setColor(QPalette.ColorRole.Base, white)
        pal.setColor(QPalette.ColorRole.AlternateBase, QColor(Theme.BG_SECTION))
        pal.setColor(QPalette.ColorRole.Text, text)
        pal.setColor(QPalette.ColorRole.Button, white)
        pal.setColor(QPalette.ColorRole.ButtonText, text)
        pal.setColor(QPalette.ColorRole.ToolTipBase, white)
        pal.setColor(QPalette.ColorRole.ToolTipText, text)
        self.setPalette(pal)
        self.setAutoFillBackground(True)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        # Header
        root.addWidget(_section_label("👷 Responsáveis Técnicos"))
        root.addWidget(_divider())

        # List
        lbl = QLabel("Responsáveis cadastrados:")
        lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl.setStyleSheet(
            f"color: {Theme.TEXT_TITLE}; background: transparent; border: none;"
        )
        root.addWidget(lbl)

        self.list_widget = QListWidget()
        self.list_widget.addItems(self.operadores)
        self.list_widget.setMinimumHeight(180)
        root.addWidget(self.list_widget)

        # Add row
        grp = QGroupBox("Adicionar novo responsável")
        grp_layout = QHBoxLayout(grp)
        grp_layout.setContentsMargins(10, 10, 10, 10)
        grp_layout.setSpacing(8)

        self.novo_input = QLineEdit()
        self.novo_input.setPlaceholderText("Nome completo…")
        self.novo_input.setMinimumHeight(34)
        self.novo_input.returnPressed.connect(self._adicionar)
        grp_layout.addWidget(self.novo_input, stretch=3)

        btn_add = QPushButton("Adicionar")
        btn_add.setMinimumHeight(34)
        btn_add.clicked.connect(self._adicionar)
        btn_add.setStyleSheet(Theme.get_botao_sucesso())
        grp_layout.addWidget(btn_add)
        root.addWidget(grp)

        # Remove button
        btn_rem = QPushButton("🗑  Remover selecionado")
        btn_rem.setMinimumHeight(34)
        btn_rem.clicked.connect(self._remover)
        btn_rem.setStyleSheet(Theme.get_botao_perigo())
        root.addWidget(btn_rem)

        root.addStretch()

        # OK / Cancel
        box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        box.accepted.connect(self._salvar)
        box.rejected.connect(self.reject)
        root.addWidget(box)

    def _adicionar(self):
        nome = self.novo_input.text().strip()
        if not nome:
            return
        if nome in self.operadores:
            QMessageBox.warning(self, "Duplicado", f'"{nome}" já está cadastrado.')
            return
        self.operadores.append(nome)
        self.list_widget.addItem(nome)
        self.novo_input.clear()
        self.novo_input.setFocus()

    def _remover(self):
        item = self.list_widget.currentItem()
        if item:
            self.operadores.remove(item.text())
            self.list_widget.takeItem(self.list_widget.row(item))

    def _salvar(self):
        self.operadores_atualizados.emit(self.operadores)
        self.accept()


# ── Estatísticas ──────────────────────────────────────────────────────────────


class EstatisticasDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Estatísticas — SMED")
        self.setModal(True)
        self.setMinimumSize(660, 560)
        self.setStyleSheet(Theme.get_theme_light())
        self._force_white_bg()
        self._build()

    def _force_white_bg(self):
        """Força fundo branco via QPalette, ignorando o tema escuro do sistema."""
        pal = self.palette()
        white = QColor(Theme.BG_CARD)
        text = QColor(Theme.TEXT_BODY)
        pal.setColor(QPalette.ColorRole.Window, white)
        pal.setColor(QPalette.ColorRole.WindowText, text)
        pal.setColor(QPalette.ColorRole.Base, white)
        pal.setColor(QPalette.ColorRole.AlternateBase, QColor(Theme.BG_SECTION))
        pal.setColor(QPalette.ColorRole.Text, text)
        pal.setColor(QPalette.ColorRole.Button, white)
        pal.setColor(QPalette.ColorRole.ButtonText, text)
        pal.setColor(QPalette.ColorRole.ToolTipBase, white)
        pal.setColor(QPalette.ColorRole.ToolTipText, text)
        self.setPalette(pal)
        self.setAutoFillBackground(True)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)

        root.addWidget(_section_label("📊  Estatísticas de Atividades"))
        root.addWidget(_divider())

        stats = self.controller.get_estatisticas()

        # ── KPI cards row
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(10)

        kpis = [
            ("Máquinas", str(stats["total_maquinas"]), Theme.PRIMARY),
            ("Atividades", str(stats["total_atividades"]), Theme.TEXT_TITLE),
            ("Concluídas", str(stats["atividades_concluidas"]), Theme.SUCCESS),
            ("Em andamento", str(stats["atividades_andamento"]), Theme.WARNING),
            ("Pausadas", str(stats["atividades_pausadas"]), Theme.DANGER),
        ]
        for title, value, color in kpis:
            card = QFrame()
            card.setStyleSheet(
                f"QFrame {{"
                f"  background-color: #FFFFFF;"
                f"  border: 1.5px solid #E2E8F0;"
                f"  border-top: 3px solid {color};"
                f"  border-radius: 8px;"
                f"}}"
            )
            cl = QVBoxLayout(card)
            cl.setContentsMargins(10, 8, 10, 8)
            cl.setSpacing(2)

            v_lbl = QLabel(value)
            v_lbl.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
            v_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v_lbl.setStyleSheet(
                f"color: {color}; background: transparent; border: none;"
            )
            cl.addWidget(v_lbl)

            t_lbl = QLabel(title)
            t_lbl.setFont(QFont("Segoe UI", 9))
            t_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            t_lbl.setStyleSheet(
                f"color: {Theme.TEXT_MUTED}; background: transparent; border: none;"
            )
            cl.addWidget(t_lbl)

            kpi_row.addWidget(card)

        root.addLayout(kpi_row)

        # ── Time summary row
        tt = int(stats["tempo_total"])
        tm = int(stats["tempo_medio"])

        def fmt(sec):
            h, r = divmod(sec, 3600)
            m, s = divmod(r, 60)
            return f"{h:02d}:{m:02d}:{s:02d}"

        time_row = QHBoxLayout()
        time_row.setSpacing(10)

        for label, value in [
            ("⏱  Tempo Total", fmt(tt) if tt else "--:--:--"),
            ("⌀  Tempo Médio", fmt(tm) if tm else "--:--:--"),
        ]:
            card = QFrame()
            card.setStyleSheet(
                f"QFrame {{"
                f"  background-color: {Theme.PRIMARY_LIGHT};"
                f"  border: 1.5px solid {Theme.PRIMARY_BORDER};"
                f"  border-radius: 8px;"
                f"}}"
            )
            cl = QHBoxLayout(card)
            cl.setContentsMargins(14, 10, 14, 10)

            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            lbl.setStyleSheet(
                f"color: {Theme.PRIMARY}; background: transparent; border: none;"
            )
            cl.addWidget(lbl)
            cl.addStretch()

            val = QLabel(value)
            val.setFont(QFont("Courier New", 18, QFont.Weight.Bold))
            val.setStyleSheet(
                f"color: {Theme.PRIMARY}; background: transparent; border: none;"
            )
            cl.addWidget(val)

            time_row.addWidget(card)

        root.addLayout(time_row)

        # ── Completed table
        grp = QGroupBox("Atividades Concluídas")
        gl = QVBoxLayout(grp)
        gl.setContentsMargins(8, 8, 8, 8)

        tabela = QTableWidget()
        tabela.setColumnCount(5)
        tabela.setHorizontalHeaderLabels(
            ["Máquina", "Descrição", "Responsável", "Tempo Total", "Finalizado em"]
        )
        tabela.setAlternatingRowColors(True)
        tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabela.verticalHeader().setVisible(False)

        concluidas = [
            a for a in self.controller.get_atividades() if a.status == "Concluído"
        ]
        tabela.setRowCount(len(concluidas))

        for i, atv in enumerate(concluidas):
            t = int(atv.cronometro_principal.tempo_decorrido)
            h, r = divmod(t, 3600)
            m, s = divmod(r, 60)
            fim_str = atv.fim.strftime("%H:%M:%S") if atv.fim else "--"

            for j, val in enumerate(
                [
                    atv.maquina_nome,
                    atv.descricao[:40],
                    atv.responsavel,
                    f"{h:02d}:{m:02d}:{s:02d}",
                    fim_str,
                ]
            ):
                item = QTableWidgetItem(val)
                item.setForeground(QColor(Theme.TEXT_BODY))
                tabela.setItem(i, j, item)

        hdr = tabela.horizontalHeader()
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        for col in (0, 3, 4):
            hdr.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

        gl.addWidget(tabela)
        root.addWidget(grp)

        # Close button
        btn_fechar = QPushButton("Fechar")
        btn_fechar.setMinimumHeight(36)
        btn_fechar.clicked.connect(self.close)
        btn_fechar.setStyleSheet(Theme.get_botao_primario())
        root.addWidget(btn_fechar)
