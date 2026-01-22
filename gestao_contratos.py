import sys
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, 
                             QHeaderView, QListWidget, QSplitter, 
                             QDialog, QComboBox, QFormLayout, QDialogButtonBox,
                             QAbstractItemView, QDateEdit, QTabWidget)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QAction, QColor, QFont

# --- 1. ESTRUTURA DE DADOS ---

class Aditivo:
    def __init__(self, tipo, valor=0.0, data_nova=None, descricao=""):
        self.tipo = tipo  # "Valor" ou "Prazo"
        self.valor = valor
        self.data_nova = data_nova
        self.descricao = descricao

class SubContrato:
    """Representa um serviço ou item dentro do contrato"""
    def __init__(self, descricao, valor_estimado):
        self.descricao = descricao
        self.valor_estimado = valor_estimado

class Movimentacao:
    def __init__(self, tipo, valor, competencia=""):
        self.tipo = tipo
        self.valor = valor
        self.competencia = competencia 

class Empenho:
    def __init__(self, numero, valor):
        self.numero = numero
        self.valor_inicial = valor
        self.valor_atual = valor
        self.valor_pago = 0.0
        self.historico = []
        self.historico.append(Movimentacao("Emissão Original", valor, "-"))

    def realizar_pagamento(self, valor, competencia):
        saldo = self.valor_atual - self.valor_pago
        if valor > saldo:
            return False, f"Saldo insuficiente! Resta: {saldo:.2f}"
        self.valor_pago += valor
        self.historico.append(Movimentacao("Pagamento", valor, competencia))
        return True, "Pagamento realizado."

    def calcular_media_mensal(self):
        if self.valor_pago == 0: return 0.0
        meses = set(m.competencia for m in self.historico if m.tipo == "Pagamento" and m.competencia)
        return self.valor_pago / len(meses) if len(meses) > 0 else 0.0

class Contrato:
    def __init__(self, numero, descricao, valor_inicial, vig_inicio, vig_fim, comp_inicio, comp_fim):
        self.numero = numero
        self.descricao = descricao
        self.valor_inicial = valor_inicial
        
        # Datas e Competências
        self.vigencia_inicio = vig_inicio
        self.vigencia_fim = vig_fim
        self.comp_inicio = comp_inicio
        self.comp_fim = comp_fim

        # Listas
        self.lista_empenhos = []
        self.lista_aditivos = []
        self.lista_servicos = [] # Subcontratos

    def get_valor_total_atual(self):
        """Calcula: Valor Inicial + Aditivos de Valor"""
        total_aditivos = sum(a.valor for a in self.lista_aditivos if a.tipo == "Valor")
        return self.valor_inicial + total_aditivos

    def get_vigencia_final_atual(self):
        """Retorna a data final original ou a alterada por aditivo de prazo"""
        # Procura o último aditivo de prazo, se houver
        aditivos_prazo = [a for a in self.lista_aditivos if a.tipo == "Prazo"]
        if aditivos_prazo:
            return aditivos_prazo[-1].data_nova
        return self.vigencia_fim

    def adicionar_empenho(self, empenho):
        saldo_livre = self.get_valor_total_atual() - sum(e.valor_inicial for e in self.lista_empenhos)
        if empenho.valor_inicial > saldo_livre:
            return False, "Valor do contrato insuficiente (considerando aditivos)."
        self.lista_empenhos.append(empenho)
        return True, "Empenho vinculado."

# --- 2. JANELAS E DIÁLOGOS ---

class DialogoCriarContrato(QDialog):
    """Formulário completo para cadastro de contrato"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo Contrato")
        self.setFixedWidth(400)
        
        layout = QFormLayout(self)

        self.inp_numero = QLineEdit()
        self.inp_desc = QLineEdit()
        self.inp_valor = QLineEdit()
        self.inp_valor.setPlaceholderText("0.00")

        # Campos de Data (QDateEdit é um calendário)
        self.date_vig_ini = QDateEdit(QDate.currentDate())
        self.date_vig_ini.setCalendarPopup(True)
        self.date_vig_fim = QDateEdit(QDate.currentDate().addYears(1))
        self.date_vig_fim.setCalendarPopup(True)

        # Campos de Competência (Texto simples "MM/AAAA")
        self.inp_comp_ini = QLineEdit(QDate.currentDate().toString("MM/yyyy"))
        self.inp_comp_fim = QLineEdit(QDate.currentDate().addYears(1).toString("MM/yyyy"))

        layout.addRow("Número:", self.inp_numero)
        layout.addRow("Objeto:", self.inp_desc)
        layout.addRow("Valor Inicial (R$):", self.inp_valor)
        layout.addRow("Início Vigência:", self.date_vig_ini)
        layout.addRow("Fim Vigência:", self.date_vig_fim)
        layout.addRow("Competência Inicial:", self.inp_comp_ini)
        layout.addRow("Competência Final:", self.inp_comp_fim)

        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)

    def get_dados(self):
        try:
            val = float(self.inp_valor.text().replace(',', '.'))
        except: val = 0.0
        
        return (self.inp_numero.text(), self.inp_desc.text(), val,
                self.date_vig_ini.text(), self.date_vig_fim.text(),
                self.inp_comp_ini.text(), self.inp_comp_fim.text())

class DialogoAditivo(QDialog):
    """Janela para criar aditivo"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo Aditivo")
        layout = QFormLayout(self)
        
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Valor (Acréscimo/Decréscimo)", "Prazo (Prorrogação)"])
        self.combo_tipo.currentIndexChanged.connect(self.mudar_tipo)

        self.inp_valor = QLineEdit("0.00")
        self.date_nova = QDateEdit(QDate.currentDate())
        self.date_nova.setCalendarPopup(True)
        self.date_nova.setEnabled(False) # Começa desativado pois padrão é Valor
        
        self.inp_desc = QLineEdit()

        layout.addRow("Tipo:", self.combo_tipo)
        layout.addRow("Valor (R$):", self.inp_valor)
        layout.addRow("Nova Data Fim:", self.date_nova)
        layout.addRow("Justificativa:", self.inp_desc)

        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botoes.accepted.connect(self.accept)
        layout.addWidget(botoes)

    def mudar_tipo(self):
        if self.combo_tipo.currentText().startswith("Valor"):
            self.inp_valor.setEnabled(True)
            self.date_nova.setEnabled(False)
        else:
            self.inp_valor.setEnabled(False)
            self.date_nova.setEnabled(True)

    def get_dados(self):
        tipo = "Valor" if self.combo_tipo.currentText().startswith("Valor") else "Prazo"
        try: val = float(self.inp_valor.text().replace(',', '.'))
        except: val = 0.0
        return tipo, val, self.date_nova.text(), self.inp_desc.text()

class DialogoPagamento(QDialog):
    def __init__(self, parent=None, ne_numero=""):
        super().__init__(parent)
        self.setWindowTitle(f"Pagamento NE {ne_numero}")
        layout = QFormLayout(self)
        self.combo_mes = QComboBox()
        self.combo_mes.addItems([f"{i:02d}" for i in range(1, 13)])
        self.input_ano = QLineEdit("2024")
        self.input_valor = QLineEdit()
        layout.addRow("Mês:", self.combo_mes)
        layout.addRow("Ano:", self.input_ano)
        layout.addRow("Valor (R$):", self.input_valor)
        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botoes.accepted.connect(self.accept)
        layout.addWidget(botoes)

    def get_dados(self):
        comp = f"{self.combo_mes.currentText()}/{self.input_ano.text()}"
        try: val = float(self.input_valor.text().replace(',', '.'))
        except: val = 0.0
        return comp, val

class JanelaVisaoGeral(QDialog):
    def __init__(self, contrato, parent=None):
        super().__init__(parent)
        self.contrato = contrato
        self.setWindowTitle(f"Visão Geral - {contrato.numero}")
        self.resize(700, 400)
        layout = QVBoxLayout(self)
        
        # Resumo do Topo
        valor_atual = contrato.get_valor_total_atual()
        lbl = QLabel(f"Total Contrato (com aditivos): R$ {valor_atual:,.2f}")
        lbl.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(lbl)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["Competência", "Valor Vigente", "Pago no Mês", "Saldo Contrato"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabela)
        self.popular_tabela(valor_atual)

    def popular_tabela(self, valor_total_contrato):
        pagamentos = {}
        for emp in self.contrato.lista_empenhos:
            for mov in emp.historico:
                if mov.tipo == "Pagamento" and mov.competencia:
                    try:
                        p = mov.competencia.split('/')
                        key = f"{p[1]}-{p[0]}"
                        pagamentos[key] = pagamentos.get(key, 0.0) + mov.valor
                    except: continue
        
        acumulado = 0.0
        self.tabela.setRowCount(0)
        for key in sorted(pagamentos.keys()):
            val_mes = pagamentos[key]
            acumulado += val_mes
            ano, mes = key.split('-')
            
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(f"{mes}/{ano}"))
            self.tabela.setItem(row, 1, QTableWidgetItem(f"{valor_total_contrato:,.2f}"))
            self.tabela.setItem(row, 2, QTableWidgetItem(f"{val_mes:,.2f}"))
            
            saldo = valor_total_contrato - acumulado
            item_saldo = QTableWidgetItem(f"{saldo:,.2f}")
            item_saldo.setForeground(QColor("blue"))
            self.tabela.setItem(row, 3, item_saldo)

# --- 3. SISTEMA PRINCIPAL ---

class SistemaGestao(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_contratos = [] 
        self.contrato_selecionado = None
        self.empenho_selecionado = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("SGF - Gestão Completa de Contratos")
        self.setGeometry(100, 100, 1200, 800) 

        # Menus
        mb = self.menuBar()
        m_arq = mb.addMenu("Arquivo")
        m_arq.addAction("Sair", self.close)
        
        m_con = mb.addMenu("Contratos")
        m_con.addAction("Novo Contrato...", self.abrir_novo_contrato)
        m_con.addAction("Adicionar Aditivo...", self.abrir_novo_aditivo)
        m_con.addAction("Adicionar Subcontrato/Serviço...", self.abrir_novo_servico)

        m_exi = mb.addMenu("Exibir")
        m_exi.addAction("Visão Geral Contrato", self.abrir_visao_geral)

        # Layout Principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        # Esquerda: Lista
        p_esq = QWidget()
        l_esq = QVBoxLayout(p_esq)
        l_esq.addWidget(QLabel("<b>Meus Contratos</b>"))
        self.lista_contratos_widget = QListWidget()
        self.lista_contratos_widget.itemClicked.connect(self.selecionar_contrato)
        l_esq.addWidget(self.lista_contratos_widget)
        splitter.addWidget(p_esq)

        # Direita: Detalhes
        p_dir = QWidget()
        self.layout_dir = QVBoxLayout(p_dir)
        
        # Cabeçalho Contrato
        self.lbl_titulo = QLabel("Selecione um contrato")
        self.lbl_titulo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.layout_dir.addWidget(self.lbl_titulo)
        
        self.lbl_datas = QLabel("-")
        self.lbl_datas.setStyleSheet("color: gray;")
        self.layout_dir.addWidget(self.lbl_datas)

        self.lbl_saldo = QLabel("")
        self.lbl_saldo.setStyleSheet("font-size: 14px; margin-bottom: 10px")
        self.layout_dir.addWidget(self.lbl_saldo)

        # Abas para separar Financeiro de Serviços
        self.abas = QTabWidget()
        self.layout_dir.addWidget(self.abas)

        # --- ABA 1: FINANCEIRO (Empenhos) ---
        tab_fin = QWidget()
        l_fin = QVBoxLayout(tab_fin)
        
        btns_fin = QHBoxLayout()
        b_ne = QPushButton("+ Novo Empenho")
        b_ne.clicked.connect(self.dialogo_novo_empenho)
        b_pg = QPushButton("Pagar / Baixar")
        b_pg.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold")
        b_pg.clicked.connect(self.abrir_pagamento)
        btns_fin.addWidget(b_ne)
        btns_fin.addWidget(b_pg)
        btns_fin.addStretch()
        l_fin.addLayout(btns_fin)

        self.tab_empenhos = QTableWidget()
        self.tab_empenhos.setColumnCount(5)
        self.tab_empenhos.setHorizontalHeaderLabels(["NE", "Valor", "Pago", "Saldo NE", "Média"])
        self.tab_empenhos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_empenhos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tab_empenhos.itemClicked.connect(self.selecionar_empenho)
        l_fin.addWidget(self.tab_empenhos)

        l_fin.addWidget(QLabel("Histórico NE:"))
        self.tab_mov = QTableWidget()
        self.tab_mov.setColumnCount(3)
        self.tab_mov.setHorizontalHeaderLabels(["Comp.", "Tipo", "Valor"])
        self.tab_mov.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_mov.setMaximumHeight(150)
        l_fin.addWidget(self.tab_mov)

        self.abas.addTab(tab_fin, "Financeiro (Empenhos)")

        # --- ABA 2: SERVIÇOS (Subcontratos) ---
        tab_serv = QWidget()
        l_serv = QVBoxLayout(tab_serv)
        self.tab_subcontratos = QTableWidget()
        self.tab_subcontratos.setColumnCount(2)
        self.tab_subcontratos.setHorizontalHeaderLabels(["Descrição do Serviço", "Valor Estimado"])
        self.tab_subcontratos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        l_serv.addWidget(self.tab_subcontratos)
        self.abas.addTab(tab_serv, "Serviços / Subcontratos")
        
        # --- ABA 3: ADITIVOS ---
        tab_adit = QWidget()
        l_adit = QVBoxLayout(tab_adit)
        self.tab_aditivos = QTableWidget()
        self.tab_aditivos.setColumnCount(4)
        self.tab_aditivos.setHorizontalHeaderLabels(["Tipo", "Valor", "Nova Data", "Justificativa"])
        self.tab_aditivos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        l_adit.addWidget(self.tab_aditivos)
        self.abas.addTab(tab_adit, "Aditivos")

        splitter.addWidget(p_dir)
        splitter.setSizes([250, 900])

    # --- FUNÇÕES ---

    def abrir_novo_contrato(self):
        dial = DialogoCriarContrato(self)
        if dial.exec():
            # Desempacota os 7 valores retornados
            num, desc, val, vig_ini, vig_fim, comp_ini, comp_fim = dial.get_dados()
            c = Contrato(num, desc, val, vig_ini, vig_fim, comp_ini, comp_fim)
            self.db_contratos.append(c)
            self.atualizar_lista_contratos()

    def abrir_novo_aditivo(self):
        if not self.contrato_selecionado: return
        dial = DialogoAditivo(self)
        if dial.exec():
            tipo, valor, data, just = dial.get_dados()
            adt = Aditivo(tipo, valor, data, just)
            self.contrato_selecionado.lista_aditivos.append(adt)
            self.atualizar_painel_detalhes()
            QMessageBox.information(self, "Sucesso", "Aditivo registrado!")

    def abrir_novo_servico(self):
        if not self.contrato_selecionado: return
        # Como é simples, usaremos InputDialog aqui para rapidez
        from PyQt6.QtWidgets import QInputDialog
        desc, ok = QInputDialog.getText(self, "Novo Serviço", "Descrição do Serviço/Subcontrato:")
        if ok and desc:
            val, ok2 = QInputDialog.getDouble(self, "Valor", "Valor Estimado:", decimals=2)
            if ok2:
                sub = SubContrato(desc, val)
                self.contrato_selecionado.lista_servicos.append(sub)
                self.atualizar_painel_detalhes()

    def atualizar_lista_contratos(self):
        self.lista_contratos_widget.clear()
        for c in self.db_contratos:
            self.lista_contratos_widget.addItem(f"{c.numero} - {c.descricao}")

    def selecionar_contrato(self, item):
        num = item.text().split(" - ")[0]
        for c in self.db_contratos:
            if c.numero == num:
                self.contrato_selecionado = c
                break
        self.atualizar_painel_detalhes()

    def atualizar_painel_detalhes(self):
        if not self.contrato_selecionado: return
        c = self.contrato_selecionado
        
        # Atualiza Labels
        self.lbl_titulo.setText(f"{c.numero} - {c.descricao}")
        
        vig_fim_real = c.get_vigencia_final_atual()
        self.lbl_datas.setText(f"Vigência: {c.vigencia_inicio} até {vig_fim_real} | Comp: {c.comp_inicio} a {c.comp_fim}")

        val_total = c.get_valor_total_atual()
        val_empenhado = sum(e.valor_inicial for e in c.lista_empenhos)
        saldo_livre = val_total - val_empenhado
        
        txt_saldo = f"<b>Valor Total: R$ {val_total:,.2f}</b>  |  Empenhado: R$ {val_empenhado:,.2f}  |  <span style='color:green'>Livre: R$ {saldo_livre:,.2f}</span>"
        self.lbl_saldo.setText(txt_saldo)

        # Atualiza Tabela Empenhos
        self.tab_empenhos.setRowCount(0)
        self.tab_mov.setRowCount(0)
        for row, emp in enumerate(c.lista_empenhos):
            self.tab_empenhos.insertRow(row)
            self.tab_empenhos.setItem(row, 0, QTableWidgetItem(emp.numero))
            self.tab_empenhos.setItem(row, 1, QTableWidgetItem(f"{emp.valor_inicial:,.2f}"))
            self.tab_empenhos.setItem(row, 2, QTableWidgetItem(f"{emp.valor_pago:,.2f}"))
            saldo_ne = emp.valor_inicial - emp.valor_pago
            self.tab_empenhos.setItem(row, 3, QTableWidgetItem(f"{saldo_ne:,.2f}"))
            self.tab_empenhos.setItem(row, 4, QTableWidgetItem(f"{emp.calcular_media_mensal():,.2f}"))
            self.tab_empenhos.item(row, 0).setData(Qt.ItemDataRole.UserRole, emp)

        # Atualiza Tabela Subcontratos
        self.tab_subcontratos.setRowCount(0)
        for row, sub in enumerate(c.lista_servicos):
            self.tab_subcontratos.insertRow(row)
            self.tab_subcontratos.setItem(row, 0, QTableWidgetItem(sub.descricao))
            self.tab_subcontratos.setItem(row, 1, QTableWidgetItem(f"{sub.valor_estimado:,.2f}"))

        # Atualiza Tabela Aditivos
        self.tab_aditivos.setRowCount(0)
        for row, adt in enumerate(c.lista_aditivos):
            self.tab_aditivos.insertRow(row)
            self.tab_aditivos.setItem(row, 0, QTableWidgetItem(adt.tipo))
            val_txt = f"{adt.valor:,.2f}" if adt.tipo == "Valor" else "-"
            self.tab_aditivos.setItem(row, 1, QTableWidgetItem(val_txt))
            data_txt = adt.data_nova if adt.tipo == "Prazo" else "-"
            self.tab_aditivos.setItem(row, 2, QTableWidgetItem(data_txt))
            self.tab_aditivos.setItem(row, 3, QTableWidgetItem(adt.descricao))

    def dialogo_novo_empenho(self):
        if not self.contrato_selecionado: return
        from PyQt6.QtWidgets import QInputDialog
        num, ok = QInputDialog.getText(self, "NE", "Número:")
        if ok:
            val, ok2 = QInputDialog.getDouble(self, "Valor", "R$:", decimals=2)
            if ok2:
                ok_emp, msg = self.contrato_selecionado.adicionar_empenho(Empenho(num, val))
                if ok_emp: self.atualizar_painel_detalhes()
                else: QMessageBox.warning(self, "Erro", msg)

    def selecionar_empenho(self, item):
        row = item.row()
        self.empenho_selecionado = self.tab_empenhos.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self.atualizar_movimentos()

    def atualizar_movimentos(self):
        if not self.empenho_selecionado: return
        self.tab_mov.setRowCount(0)
        for row, m in enumerate(self.empenho_selecionado.historico):
            self.tab_mov.insertRow(row)
            self.tab_mov.setItem(row, 0, QTableWidgetItem(m.competencia))
            self.tab_mov.setItem(row, 1, QTableWidgetItem(m.tipo))
            self.tab_mov.setItem(row, 2, QTableWidgetItem(f"{m.valor:,.2f}"))

    def abrir_pagamento(self):
        if not self.empenho_selecionado: return
        d = DialogoPagamento(self, self.empenho_selecionado.numero)
        if d.exec():
            c, v = d.get_dados()
            ok, msg = self.empenho_selecionado.realizar_pagamento(v, c)
            if not ok: QMessageBox.warning(self, "Erro", msg)
            self.atualizar_painel_detalhes()
            self.atualizar_movimentos()

    def abrir_visao_geral(self):
        if self.contrato_selecionado:
            JanelaVisaoGeral(self.contrato_selecionado, self).exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = SistemaGestao()
    win.show()
    sys.exit(app.exec())