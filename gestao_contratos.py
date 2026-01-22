import sys
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, 
                             QHeaderView, QListWidget, QSplitter, 
                             QDialog, QComboBox, QFormLayout, QDialogButtonBox,
                             QAbstractItemView, QDateEdit, QTabWidget, QMenu)
from PyQt6.QtCore import Qt, QDate, QPoint
from PyQt6.QtGui import QAction, QColor, QFont, QCursor

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
        # O valor empenhado será calculado somando as Notas de Empenho vinculadas

class Movimentacao:
    def __init__(self, tipo, valor, competencia=""):
        self.tipo = tipo
        self.valor = valor
        self.competencia = competencia 

class NotaEmpenho:
    def __init__(self, numero, valor, descricao, subcontrato_idx):
        self.numero = numero
        self.valor_inicial = valor
        self.descricao = descricao
        self.subcontrato_idx = subcontrato_idx # Índice do subcontrato na lista do contrato
        self.valor_pago = 0.0
        self.historico = []
        # Criação
        self.historico.append(Movimentacao("Emissão Original", valor, "-"))

    def realizar_pagamento(self, valor, competencia):
        saldo = self.valor_inicial - self.valor_pago
        if valor > saldo:
            return False, f"Saldo insuficiente na Nota de Empenho! Resta: {saldo:.2f}"
        self.valor_pago += valor
        self.historico.append(Movimentacao("Pagamento", valor, competencia))
        return True, "Pagamento realizado."

    def excluir_movimentacao(self, index_movimentacao):
        """Remove uma movimentação e estorna o valor se for pagamento"""
        if index_movimentacao < 0 or index_movimentacao >= len(self.historico):
            return False, "Índice inválido."
        
        mov = self.historico[index_movimentacao]
        
        if mov.tipo == "Emissão Original":
            return False, "Não é possível excluir a emissão original. Exclua a Nota de Empenho inteira se necessário."
        
        if mov.tipo == "Pagamento":
            self.valor_pago -= mov.valor # Estorna o valor
        
        self.historico.pop(index_movimentacao)
        return True, "Movimentação excluída e saldo restaurado."

    def calcular_media_mensal(self):
        if self.valor_pago == 0: return 0.0
        meses = set(m.competencia for m in self.historico if m.tipo == "Pagamento" and m.competencia)
        return self.valor_pago / len(meses) if len(meses) > 0 else 0.0

class Contrato:
    def __init__(self, numero, prestador, descricao, valor_inicial, vig_inicio, vig_fim, comp_inicio, comp_fim):
        self.numero = numero
        self.prestador = prestador
        self.descricao = descricao
        self.valor_inicial = valor_inicial
        
        self.vigencia_inicio = vig_inicio
        self.vigencia_fim = vig_fim
        self.comp_inicio = comp_inicio
        self.comp_fim = comp_fim

        self.lista_notas_empenho = []
        self.lista_aditivos = []
        self.lista_servicos = [] # Lista de SubContratos

    def get_valor_total_contrato(self):
        """Valor Inicial + Aditivos de Valor"""
        total_aditivos = sum(a.valor for a in self.lista_aditivos if a.tipo == "Valor")
        return self.valor_inicial + total_aditivos

    def get_vigencia_final_atual(self):
        aditivos_prazo = [a for a in self.lista_aditivos if a.tipo == "Prazo"]
        if aditivos_prazo:
            return aditivos_prazo[-1].data_nova
        return self.vigencia_fim

    def adicionar_nota_empenho(self, ne):
        # 1. Verificar Saldo Geral do Contrato
        total_empenhado_geral = sum(e.valor_inicial for e in self.lista_notas_empenho)
        saldo_livre_geral = self.get_valor_total_contrato() - total_empenhado_geral
        
        if ne.valor_inicial > saldo_livre_geral:
            return False, "Valor indisponível no Saldo Geral do Contrato."

        # 2. Verificar Saldo do Subcontrato (Serviço) específico
        if ne.subcontrato_idx < 0 or ne.subcontrato_idx >= len(self.lista_servicos):
            return False, "Subcontrato inválido."
        
        sub = self.lista_servicos[ne.subcontrato_idx]
        
        # Calcular quanto já foi gasto neste subcontrato específico
        gasto_sub = sum(e.valor_inicial for e in self.lista_notas_empenho if e.subcontrato_idx == ne.subcontrato_idx)
        saldo_livre_sub = sub.valor_estimado - gasto_sub
        
        if ne.valor_inicial > saldo_livre_sub:
             return False, f"Valor excede o saldo do serviço '{sub.descricao}'. Disponível no serviço: {saldo_livre_sub:.2f}"

        self.lista_notas_empenho.append(ne)
        return True, "Nota de Empenho vinculada com sucesso."

# --- 2. JANELAS E DIÁLOGOS ---

class DialogoCriarContrato(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo Contrato")
        self.setFixedWidth(450)
        layout = QFormLayout(self)

        self.inp_numero = QLineEdit()
        self.inp_prestador = QLineEdit() # Novo Campo
        self.inp_desc = QLineEdit()
        self.inp_valor = QLineEdit()
        self.inp_valor.setPlaceholderText("0.00")

        self.date_vig_ini = QDateEdit(QDate.currentDate())
        self.date_vig_ini.setCalendarPopup(True)
        self.date_vig_fim = QDateEdit(QDate.currentDate().addYears(1))
        self.date_vig_fim.setCalendarPopup(True)

        self.inp_comp_ini = QLineEdit(QDate.currentDate().toString("MM/yyyy"))
        self.inp_comp_fim = QLineEdit(QDate.currentDate().addYears(1).toString("MM/yyyy"))

        layout.addRow("Número:", self.inp_numero)
        layout.addRow("Prestador:", self.inp_prestador)
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
        try: val = float(self.inp_valor.text().replace(',', '.'))
        except: val = 0.0
        return (self.inp_numero.text(), self.inp_prestador.text(), self.inp_desc.text(), val,
                self.date_vig_ini.text(), self.date_vig_fim.text(),
                self.inp_comp_ini.text(), self.inp_comp_fim.text())

class DialogoNovoEmpenho(QDialog):
    """Agora exige a seleção do subcontrato"""
    def __init__(self, lista_subcontratos, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nova Nota de Empenho")
        self.setFixedWidth(400)
        layout = QFormLayout(self)
        
        self.inp_num = QLineEdit()
        self.inp_desc = QLineEdit()
        self.inp_val = QLineEdit()
        
        self.combo_sub = QComboBox()
        for sub in lista_subcontratos:
            self.combo_sub.addItem(f"{sub.descricao} (Est: {sub.valor_estimado:,.2f})")
            
        layout.addRow("Número da Nota:", self.inp_num)
        layout.addRow("Descrição:", self.inp_desc)
        layout.addRow("Vincular a Serviço:", self.combo_sub)
        layout.addRow("Valor (R$):", self.inp_val)

        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)

    def get_dados(self):
        idx = self.combo_sub.currentIndex()
        try: val = float(self.inp_val.text().replace(',', '.'))
        except: val = 0.0
        return self.inp_num.text(), self.inp_desc.text(), idx, val

class DialogoAditivo(QDialog):
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
        self.date_nova.setEnabled(False)
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
        self.setWindowTitle(f"Pagamento Nota {ne_numero}")
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
        self.resize(750, 450)
        layout = QVBoxLayout(self)
        
        valor_atual = contrato.get_valor_total_contrato()
        lbl = QLabel(f"CONTRATO: {contrato.numero} - {contrato.prestador}\nTotal (c/ aditivos): R$ {valor_atual:,.2f}")
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
        for emp in self.contrato.lista_notas_empenho:
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
        self.ne_selecionada = None # Antigo empenho_selecionado
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("SGF - Gestão Profissional de Contratos")
        self.setGeometry(100, 100, 1280, 800) 

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
        
        self.lbl_prestador = QLabel("")
        self.lbl_prestador.setStyleSheet("color: #555; font-weight: bold;")
        self.layout_dir.addWidget(self.lbl_prestador)

        self.lbl_datas = QLabel("-")
        self.lbl_datas.setStyleSheet("color: gray;")
        self.layout_dir.addWidget(self.lbl_datas)

        self.lbl_saldo = QLabel("")
        self.lbl_saldo.setStyleSheet("font-size: 14px; margin-bottom: 10px")
        self.layout_dir.addWidget(self.lbl_saldo)

        self.abas = QTabWidget()
        self.layout_dir.addWidget(self.abas)

        # --- ABA 1: FINANCEIRO (Notas de Empenho) ---
        tab_fin = QWidget()
        l_fin = QVBoxLayout(tab_fin)
        
        btns_fin = QHBoxLayout()
        b_ne = QPushButton("+ Nova Nota de Empenho")
        b_ne.clicked.connect(self.dialogo_nova_ne)
        b_pg = QPushButton("Registrar Pagamento")
        b_pg.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold")
        b_pg.clicked.connect(self.abrir_pagamento)
        btns_fin.addWidget(b_ne)
        btns_fin.addWidget(b_pg)
        btns_fin.addStretch()
        l_fin.addLayout(btns_fin)

        self.tab_empenhos = QTableWidget()
        self.tab_empenhos.setColumnCount(7) # Aumentado para incluir Serviço e Descrição
        self.tab_empenhos.setHorizontalHeaderLabels(["Nota (NE)", "Serviço/Sub", "Descrição", "Valor NE", "Pago", "Saldo NE", "Média"])
        self.tab_empenhos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_empenhos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tab_empenhos.itemClicked.connect(self.selecionar_ne)
        l_fin.addWidget(self.tab_empenhos)

        l_fin.addWidget(QLabel("Histórico da Nota Selecionada (Clique Dir. para Excluir):"))
        self.tab_mov = QTableWidget()
        self.tab_mov.setColumnCount(4) # Adicionada coluna Saldo
        self.tab_mov.setHorizontalHeaderLabels(["Comp.", "Tipo", "Valor Mov.", "Saldo Nota"])
        self.tab_mov.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tab_mov.setMaximumHeight(200)
        # Habilitar Menu de Contexto
        self.tab_mov.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_mov.customContextMenuRequested.connect(self.menu_contexto_mov)

        l_fin.addWidget(self.tab_mov)

        self.abas.addTab(tab_fin, "Financeiro (Notas de Empenho)")

        # --- ABA 2: SERVIÇOS (Subcontratos) ---
        tab_serv = QWidget()
        l_serv = QVBoxLayout(tab_serv)
        self.tab_subcontratos = QTableWidget()
        self.tab_subcontratos.setColumnCount(4)
        self.tab_subcontratos.setHorizontalHeaderLabels(["Descrição Serviço", "Valor Estimado", "Empenhado", "Saldo Serviço"])
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
        splitter.setSizes([250, 1000])

    # --- FUNÇÕES LÓGICAS ---

    def abrir_novo_contrato(self):
        dial = DialogoCriarContrato(self)
        if dial.exec():
            num, prest, desc, val, vig_ini, vig_fim, comp_ini, comp_fim = dial.get_dados()
            c = Contrato(num, prest, desc, val, vig_ini, vig_fim, comp_ini, comp_fim)
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
        from PyQt6.QtWidgets import QInputDialog
        desc, ok = QInputDialog.getText(self, "Novo Serviço", "Descrição do Serviço/Subcontrato:")
        if ok and desc:
            val, ok2 = QInputDialog.getDouble(self, "Valor", "Valor Estimado (Teto do serviço):", decimals=2)
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
        self.ne_selecionada = None # Reseta a seleção da NE
        self.atualizar_painel_detalhes()

    def atualizar_painel_detalhes(self):
        if not self.contrato_selecionado: return
        c = self.contrato_selecionado
        
        self.lbl_titulo.setText(f"Contrato {c.numero} - {c.descricao}")
        self.lbl_prestador.setText(f"Prestador: {c.prestador}")
        vig_fim_real = c.get_vigencia_final_atual()
        self.lbl_datas.setText(f"Vigência: {c.vigencia_inicio} até {vig_fim_real} | Comp: {c.comp_inicio} a {c.comp_fim}")

        val_total = c.get_valor_total_contrato()
        val_empenhado_geral = sum(e.valor_inicial for e in c.lista_notas_empenho)
        saldo_livre = val_total - val_empenhado_geral
        
        txt_saldo = f"<b>Total Contrato: R$ {val_total:,.2f}</b> | Empenhado Total: R$ {val_empenhado_geral:,.2f} | <span style='color:green'>Saldo p/ Empenhar: R$ {saldo_livre:,.2f}</span>"
        self.lbl_saldo.setText(txt_saldo)

        # 1. Tabela Notas de Empenho
        self.tab_empenhos.setRowCount(0)
        self.tab_mov.setRowCount(0)
        
        for row, ne in enumerate(c.lista_notas_empenho):
            self.tab_empenhos.insertRow(row)
            
            # Busca nome do serviço
            nome_servico = "Desconhecido"
            if 0 <= ne.subcontrato_idx < len(c.lista_servicos):
                nome_servico = c.lista_servicos[ne.subcontrato_idx].descricao

            self.tab_empenhos.setItem(row, 0, QTableWidgetItem(ne.numero))
            self.tab_empenhos.setItem(row, 1, QTableWidgetItem(nome_servico))
            self.tab_empenhos.setItem(row, 2, QTableWidgetItem(ne.descricao))
            self.tab_empenhos.setItem(row, 3, QTableWidgetItem(f"{ne.valor_inicial:,.2f}"))
            self.tab_empenhos.setItem(row, 4, QTableWidgetItem(f"{ne.valor_pago:,.2f}"))
            saldo_ne = ne.valor_inicial - ne.valor_pago
            item_saldo = QTableWidgetItem(f"{saldo_ne:,.2f}")
            item_saldo.setForeground(QColor("blue"))
            self.tab_empenhos.setItem(row, 5, item_saldo)
            self.tab_empenhos.setItem(row, 6, QTableWidgetItem(f"{ne.calcular_media_mensal():,.2f}"))
            self.tab_empenhos.item(row, 0).setData(Qt.ItemDataRole.UserRole, ne)

        # 2. Tabela Subcontratos (Com saldo específico)
        self.tab_subcontratos.setRowCount(0)
        for idx, sub in enumerate(c.lista_servicos):
            # Calcula quanto foi empenhado para ESTE serviço específico
            empenhado_sub = sum(ne.valor_inicial for ne in c.lista_notas_empenho if ne.subcontrato_idx == idx)
            saldo_sub = sub.valor_estimado - empenhado_sub
            
            row = self.tab_subcontratos.rowCount()
            self.tab_subcontratos.insertRow(row)
            self.tab_subcontratos.setItem(row, 0, QTableWidgetItem(sub.descricao))
            self.tab_subcontratos.setItem(row, 1, QTableWidgetItem(f"{sub.valor_estimado:,.2f}"))
            self.tab_subcontratos.setItem(row, 2, QTableWidgetItem(f"{empenhado_sub:,.2f}"))
            
            item_saldo_sub = QTableWidgetItem(f"{saldo_sub:,.2f}")
            if saldo_sub < 0: item_saldo_sub.setForeground(QColor("red"))
            else: item_saldo_sub.setForeground(QColor("green"))
            self.tab_subcontratos.setItem(row, 3, item_saldo_sub)

        # 3. Tabela Aditivos
        self.tab_aditivos.setRowCount(0)
        for row, adt in enumerate(c.lista_aditivos):
            self.tab_aditivos.insertRow(row)
            self.tab_aditivos.setItem(row, 0, QTableWidgetItem(adt.tipo))
            val_txt = f"{adt.valor:,.2f}" if adt.tipo == "Valor" else "-"
            self.tab_aditivos.setItem(row, 1, QTableWidgetItem(val_txt))
            data_txt = adt.data_nova if adt.tipo == "Prazo" else "-"
            self.tab_aditivos.setItem(row, 2, QTableWidgetItem(data_txt))
            self.tab_aditivos.setItem(row, 3, QTableWidgetItem(adt.descricao))

    def dialogo_nova_ne(self):
        if not self.contrato_selecionado: return
        if not self.contrato_selecionado.lista_servicos:
            QMessageBox.warning(self, "Atenção", "Crie pelo menos um Serviço/Subcontrato antes de criar uma Nota de Empenho.")
            return

        dial = DialogoNovoEmpenho(self.contrato_selecionado.lista_servicos, self)
        if dial.exec():
            num, desc, sub_idx, val = dial.get_dados()
            nova_ne = NotaEmpenho(num, val, desc, sub_idx)
            
            ok, msg = self.contrato_selecionado.adicionar_nota_empenho(nova_ne)
            if ok: 
                self.atualizar_painel_detalhes()
            else: 
                QMessageBox.critical(self, "Erro de Saldo", msg)

    def selecionar_ne(self, item):
        row = item.row()
        self.ne_selecionada = self.tab_empenhos.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self.atualizar_movimentos()

    def atualizar_movimentos(self):
        if not self.ne_selecionada: return
        self.tab_mov.setRowCount(0)
        
        # Calcular o saldo linha a linha (como extrato)
        saldo_corrente = self.ne_selecionada.valor_inicial
        
        for row, m in enumerate(self.ne_selecionada.historico):
            self.tab_mov.insertRow(row)
            
            # Se for pagamento, subtrai. Se for emissão original, define o inicial.
            if m.tipo == "Pagamento":
                saldo_corrente -= m.valor
            
            self.tab_mov.setItem(row, 0, QTableWidgetItem(m.competencia))
            self.tab_mov.setItem(row, 1, QTableWidgetItem(m.tipo))
            self.tab_mov.setItem(row, 2, QTableWidgetItem(f"{m.valor:,.2f}"))
            
            item_saldo = QTableWidgetItem(f"{saldo_corrente:,.2f}")
            item_saldo.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            self.tab_mov.setItem(row, 3, item_saldo)

    def menu_contexto_mov(self, posicao):
        """Cria o menu de clique direito para excluir"""
        if not self.ne_selecionada: return
        
        # Descobre qual linha foi clicada
        item = self.tab_mov.itemAt(posicao)
        if not item: return
        row = item.row()
        
        menu = QMenu()
        acao_excluir = QAction("Excluir Lançamento", self)
        menu.addAction(acao_excluir)
        
        acao = menu.exec(self.tab_mov.mapToGlobal(posicao))
        
        if acao == acao_excluir:
            confirmar = QMessageBox.question(self, "Confirmar", 
                                             "Tem a certeza que deseja excluir este lançamento? O saldo será restaurado.",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirmar == QMessageBox.StandardButton.Yes:
                ok, msg = self.ne_selecionada.excluir_movimentacao(row)
                if ok:
                    self.atualizar_painel_detalhes()
                    self.atualizar_movimentos()
                    QMessageBox.information(self, "Sucesso", msg)
                else:
                    QMessageBox.warning(self, "Erro", msg)

    def abrir_pagamento(self):
        if not self.ne_selecionada: 
            QMessageBox.warning(self, "Aviso", "Selecione uma Nota de Empenho na tabela para pagar.")
            return
        d = DialogoPagamento(self, self.ne_selecionada.numero)
        if d.exec():
            c, v = d.get_dados()
            ok, msg = self.ne_selecionada.realizar_pagamento(v, c)
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