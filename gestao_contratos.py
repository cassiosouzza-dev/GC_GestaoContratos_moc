import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, 
                             QHeaderView, QFrame, QListWidget, QSplitter, 
                             QMenu, QToolBar, QInputDialog, QAbstractItemView)
from PyQt6.QtCore import Qt
# CORREÇÃO AQUI EM BAIXO: Adicionei QFont
from PyQt6.QtGui import QAction, QIcon, QColor, QFont

# --- 1. ESTRUTURA DE DADOS (Lógica Hierárquica) ---

class Movimentacao:
    """Representa uma linha no histórico (Pagamento, Criação, Anulação)"""
    def __init__(self, tipo, valor, data="Hoje"):
        self.tipo = tipo
        self.valor = valor
        self.data = data

class Empenho:
    def __init__(self, numero, valor):
        self.numero = numero
        self.valor_inicial = valor
        self.valor_atual = valor
        self.valor_pago = 0.0
        # Lista de movimentações para a "tabela vertical"
        self.historico = []
        self.registrar_movimento("Emissão Original", valor)

    def registrar_movimento(self, tipo, valor):
        self.historico.append(Movimentacao(tipo, valor))

    def realizar_pagamento(self, valor):
        saldo = self.valor_atual - self.valor_pago
        if valor > saldo:
            return False, f"Saldo insuficiente! Resta: {saldo:.2f}"
        
        self.valor_pago += valor
        self.registrar_movimento("Pagamento (Liquidação)", valor)
        return True, "Pagamento realizado."

class Contrato:
    def __init__(self, numero, descricao, valor_total):
        self.numero = numero
        self.descricao = descricao # Ex: Limpeza, Vigilância
        self.valor_total = valor_total
        self.lista_empenhos = []

    def adicionar_empenho(self, empenho):
        saldo_livre = self.valor_total - sum(e.valor_inicial for e in self.lista_empenhos)
        if empenho.valor_inicial > saldo_livre:
            return False, "Valor do contrato insuficiente."
        
        self.lista_empenhos.append(empenho)
        return True, "Empenho vinculado."

# --- 2. INTERFACE GRÁFICA (Mestre-Detalhe) ---

class SistemaGestao(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_contratos = [] # Nossa "memória" que guarda vários contratos
        self.contrato_selecionado = None
        self.empenho_selecionado = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("SGF - Gestão Multi-Contratos")
        self.setGeometry(100, 100, 1024, 768) # Resolução padrão maior

        # --- A. BARRA DE MENUS ---
        menu_bar = self.menuBar()
        
        # Menu Arquivo
        menu_arquivo = menu_bar.addMenu("Arquivo")
        acao_sair = QAction("Sair", self)
        acao_sair.triggered.connect(self.close)
        menu_arquivo.addAction(acao_sair)

        # Menu Contratos
        menu_contratos = menu_bar.addMenu("Contratos")
        acao_novo = QAction("Novo Contrato...", self)
        acao_novo.triggered.connect(self.dialogo_novo_contrato)
        menu_contratos.addAction(acao_novo)

        # --- B. LAYOUT PRINCIPAL (DIVISOR) ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        # --- PAINEL ESQUERDO: Lista de Contratos ---
        painel_esq = QWidget()
        layout_esq = QVBoxLayout(painel_esq)
        layout_esq.addWidget(QLabel("<b>Meus Contratos</b>"))
        
        self.lista_contratos_widget = QListWidget()
        self.lista_contratos_widget.itemClicked.connect(self.selecionar_contrato)
        layout_esq.addWidget(self.lista_contratos_widget)
        
        splitter.addWidget(painel_esq)

        # --- PAINEL DIREITO: Área de Trabalho ---
        painel_dir = QWidget()
        self.layout_dir = QVBoxLayout(painel_dir)
        
        # 1. Cabeçalho do Contrato
        self.lbl_titulo_contrato = QLabel("Selecione um contrato ao lado")
        # AGORA VAI FUNCIONAR POIS IMPORTAMOS QFONT
        self.lbl_titulo_contrato.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.lbl_titulo_contrato.setStyleSheet("color: #2c3e50")
        self.layout_dir.addWidget(self.lbl_titulo_contrato)

        self.lbl_saldo_contrato = QLabel("")
        self.layout_dir.addWidget(self.lbl_saldo_contrato)

        # 2. Barra de Ferramentas do Contrato (Botões de Ação)
        ferramentas_layout = QHBoxLayout()
        btn_novo_empenho = QPushButton("+ Novo Empenho")
        btn_novo_empenho.clicked.connect(self.dialogo_novo_empenho)
        ferramentas_layout.addWidget(btn_novo_empenho)
        
        btn_pagar = QPushButton("Registrar Pagamento")
        btn_pagar.setStyleSheet("background-color: #27ae60; color: white")
        btn_pagar.clicked.connect(self.dialogo_pagamento)
        ferramentas_layout.addWidget(btn_pagar)
        
        ferramentas_layout.addStretch() # Empurra botões para a esquerda
        self.layout_dir.addLayout(ferramentas_layout)

        # 3. Tabela de Empenhos (Lista Principal)
        self.layout_dir.addWidget(QLabel("<b>Lista de Empenhos</b>"))
        self.tabela_empenhos = QTableWidget()
        self.tabela_empenhos.setColumnCount(4)
        self.tabela_empenhos.setHorizontalHeaderLabels(["NE", "Valor Empenhado", "Valor Pago", "Saldo a Pagar"])
        self.tabela_empenhos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_empenhos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_empenhos.itemClicked.connect(self.selecionar_empenho)
        self.layout_dir.addWidget(self.tabela_empenhos)

        # 4. Tabela de Movimentações (A "Tabela Vertical" de detalhes)
        self.layout_dir.addWidget(QLabel("<b>Movimentações da NE Selecionada</b>"))
        self.tabela_movimentos = QTableWidget()
        self.tabela_movimentos.setColumnCount(2)
        self.tabela_movimentos.setHorizontalHeaderLabels(["Tipo de Movimento", "Valor (R$)"])
        self.tabela_movimentos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Altura fixa menor, pois é detalhe
        self.tabela_movimentos.setMaximumHeight(150) 
        self.layout_dir.addWidget(self.tabela_movimentos)

        splitter.addWidget(painel_dir)
        
        # Define proporção inicial (25% lista, 75% detalhes)
        splitter.setSizes([200, 800])

    # --- LÓGICA DE INTERFACE ---

    def dialogo_novo_contrato(self):
        # Forma simples de pedir dados (input dialog)
        num, ok1 = QInputDialog.getText(self, "Novo Contrato", "Número do Contrato:")
        if not ok1 or not num: return
        
        desc, ok2 = QInputDialog.getText(self, "Descrição", "Objeto (ex: Limpeza):")
        
        val, ok3 = QInputDialog.getDouble(self, "Valor", "Valor Total (R$):", decimals=2, max=100000000)
        
        if ok3:
            novo_c = Contrato(num, desc, val)
            self.db_contratos.append(novo_c)
            self.atualizar_lista_contratos()

    def atualizar_lista_contratos(self):
        self.lista_contratos_widget.clear()
        for c in self.db_contratos:
            self.lista_contratos_widget.addItem(f"{c.numero} - {c.descricao}")

    def selecionar_contrato(self, item):
        # Acha o contrato pelo texto da lista (forma simplificada)
        texto = item.text()
        numero = texto.split(" - ")[0]
        
        # Busca na lista
        for c in self.db_contratos:
            if c.numero == numero:
                self.contrato_selecionado = c
                break
        
        self.atualizar_painel_detalhes()

    def atualizar_painel_detalhes(self):
        if not self.contrato_selecionado: return

        c = self.contrato_selecionado
        # Atualiza cabeçalho
        self.lbl_titulo_contrato.setText(f"Contrato: {c.numero} - {c.descricao}")
        saldo_livre = c.valor_total - sum(e.valor_inicial for e in c.lista_empenhos)
        self.lbl_saldo_contrato.setText(f"Total: R$ {c.valor_total:,.2f} | Livre para Empenhar: R$ {saldo_livre:,.2f}")

        # Atualiza Tabela de Empenhos
        self.tabela_empenhos.setRowCount(0)
        self.tabela_movimentos.setRowCount(0) # Limpa movimentos também
        
        for row, emp in enumerate(c.lista_empenhos):
            self.tabela_empenhos.insertRow(row)
            self.tabela_empenhos.setItem(row, 0, QTableWidgetItem(emp.numero))
            self.tabela_empenhos.setItem(row, 1, QTableWidgetItem(f"{emp.valor_inicial:,.2f}"))
            self.tabela_empenhos.setItem(row, 2, QTableWidgetItem(f"{emp.valor_pago:,.2f}"))
            
            saldo = emp.valor_inicial - emp.valor_pago
            item_saldo = QTableWidgetItem(f"{saldo:,.2f}")
            item_saldo.setForeground(QColor("blue"))
            self.tabela_empenhos.setItem(row, 3, item_saldo)
            
            # Guardamos o objeto real na linha da tabela para recuperar depois
            self.tabela_empenhos.item(row, 0).setData(Qt.ItemDataRole.UserRole, emp)

    def dialogo_novo_empenho(self):
        if not self.contrato_selecionado:
            QMessageBox.warning(self, "Aviso", "Selecione um contrato na lista à esquerda.")
            return

        num, ok1 = QInputDialog.getText(self, "Nova NE", "Número da NE:")
        if not ok1: return
        val, ok2 = QInputDialog.getDouble(self, "Valor", "Valor (R$):", decimals=2, max=10000000)
        
        if ok2:
            ne = Empenho(num, val)
            sucesso, msg = self.contrato_selecionado.adicionar_empenho(ne)
            if sucesso:
                self.atualizar_painel_detalhes()
            else:
                QMessageBox.critical(self, "Erro", msg)

    def selecionar_empenho(self, item):
        # Recupera o objeto Empenho escondido na linha
        row = item.row()
        # O objeto está guardado na coluna 0
        self.empenho_selecionado = self.tabela_empenhos.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self.atualizar_tabela_movimentos()

    def atualizar_tabela_movimentos(self):
        if not self.empenho_selecionado: return
        
        self.tabela_movimentos.setRowCount(0)
        for row, mov in enumerate(self.empenho_selecionado.historico):
            self.tabela_movimentos.insertRow(row)
            self.tabela_movimentos.setItem(row, 0, QTableWidgetItem(mov.tipo))
            self.tabela_movimentos.setItem(row, 1, QTableWidgetItem(f"{mov.valor:,.2f}"))

    def dialogo_pagamento(self):
        if not self.empenho_selecionado:
            QMessageBox.warning(self, "Aviso", "Selecione uma NE na tabela acima para pagar.")
            return
            
        val, ok = QInputDialog.getDouble(self, "Pagamento", 
                                        f"Valor a pagar na NE {self.empenho_selecionado.numero}:", 
                                        decimals=2, max=10000000)
        if ok:
            sucesso, msg = self.empenho_selecionado.realizar_pagamento(val)
            if sucesso:
                self.atualizar_painel_detalhes() # Atualiza saldos
                self.atualizar_tabela_movimentos() # Atualiza histórico
            else:
                QMessageBox.critical(self, "Erro", msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Estilo sóbrio e moderno
    janela = SistemaGestao()
    janela.show()
    sys.exit(app.exec())