import unittest
import os
import json
import sys
from datetime import datetime
from PyQt6.QtWidgets import QApplication

# Importa o seu sistema (o arquivo gestao_contratos.py deve estar na mesma pasta)
try:
    import gestao_contratos as sgf
except ImportError:
    print("ERRO: Não encontrei o arquivo 'gestao_contratos.py'.")
    print("Salve este script de teste na mesma pasta do seu sistema.")
    sys.exit(1)

class TesteSGF(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Cria a aplicação Qt uma única vez para os testes
        cls.app = QApplication(sys.argv)

    def setUp(self):
        # Executa ANTES de cada teste
        # Cria uma instância limpa do contrato para testar lógica
        self.contrato = sgf.Contrato(
            numero="TESTE-001",
            prestador="Empresa Teste Ltda",
            descricao="Prestação de Serviços de Teste",
            valor_inicial=1000.00,
            vig_inicio="01/01/2026",
            vig_fim="31/12/2026",
            comp_inicio="01/2026",
            comp_fim="12/2026",
            licitacao="Pregão 01",
            dispensa=""
        )

    def test_01_saldo_inicial(self):
        """Testa se o saldo inicial do ciclo 0 está correto"""
        saldo = self.contrato.get_saldo_ciclo_geral(0)
        self.assertEqual(saldo, 1000.00, "O saldo inicial deve ser igual ao valor do contrato")
        print("✅ Saldo Inicial OK")

    def test_02_adicionar_ne(self):
        """Testa se adicionar uma NE desconta do saldo"""
        ne = sgf.NotaEmpenho(
            numero="2026NE001",
            valor=400.00,
            descricao="Empenho Parcial",
            subcontrato_idx=-1,
            fonte_recurso="100",
            data_emissao="10/01/2026",
            ciclo_id=0
        )
        sucesso, msg = self.contrato.adicionar_nota_empenho(ne)
        self.assertTrue(sucesso, f"Falha ao adicionar NE: {msg}")
        
        saldo_restante = self.contrato.get_saldo_ciclo_geral(0)
        self.assertEqual(saldo_restante, 600.00, "Saldo deve ser 1000 - 400 = 600")
        print("✅ Inserção de NE e Cálculo de Saldo OK")

    def test_03_bloqueio_saldo_insuficiente(self):
        """Testa se o sistema bloqueia NE maior que o saldo"""
        ne_gigante = sgf.NotaEmpenho("NE999", 2000.00, "Exagero", -1, "100", "01/01/2026", 0)
        sucesso, msg = self.contrato.adicionar_nota_empenho(ne_gigante)
        self.assertFalse(sucesso, "O sistema deveria ter bloqueado a NE")
        print("✅ Bloqueio de Saldo Insuficiente OK")

    def test_04_pagamento_parcial(self):
        """Testa o fluxo de pagamento dentro da NE"""
        ne = sgf.NotaEmpenho("NE_PAG", 100.00, "Teste Pagto", -1, "100", "01/01/2026", 0)
        self.contrato.adicionar_nota_empenho(ne)
        
        # Pagar 50 reais
        ok, msg = ne.realizar_pagamento(50.00, "01/2026")
        self.assertTrue(ok)
        self.assertEqual(ne.valor_pago, 50.00)
        self.assertEqual(ne.valor_inicial - ne.valor_pago, 50.00)
        print("✅ Pagamento Parcial OK")

    def test_05_aditivo_valor(self):
        """Testa se Aditivo de Valor aumenta o teto do ciclo"""
        # Aditivo de R$ 500,00
        adt = sgf.Aditivo(0, "Valor", 500.00, None, "Aumento de meta", False, None)
        self.contrato.adicionar_aditivo(adt, id_ciclo_alvo=0)
        
        teto = self.contrato.ciclos[0].get_teto_total()
        self.assertEqual(teto, 1500.00, "Teto deveria subir para 1000 + 500 = 1500")
        print("✅ Aditivo de Valor OK")

    def test_06_persistencia_arquivo(self):
        """Testa se o sistema Salva e Carrega sem erros (Simulação)"""
        nome_arquivo_teste = "dados_teste_unitario.json"
        
        # Cria sistema principal
        sistema = sgf.SistemaGestao()
        sistema.arquivo_db = nome_arquivo_teste # Muda para não estragar seu arquivo real
        sistema.db_contratos = [self.contrato]
        
        # Salva
        sistema.salvar_dados()
        self.assertTrue(os.path.exists(nome_arquivo_teste), "Arquivo JSON não foi criado")
        
        # Limpa memória e Carrega
        sistema.db_contratos = []
        sistema.carregar_dados()
        
        self.assertEqual(len(sistema.db_contratos), 1, "Deveria ter carregado 1 contrato")
        self.assertEqual(sistema.db_contratos[0].numero, "TESTE-001")
        
        # Limpeza
        if os.path.exists(nome_arquivo_teste):
            os.remove(nome_arquivo_teste)
            
        print("✅ Salvar e Carregar JSON OK")

    def test_07_formato_monetario(self):
        """Testa a função fmt_br que alteramos recentemente"""
        val = 1250.50
        texto = sgf.fmt_br(val)
        # O caractere de espaço pode variar (non-breaking space), então checamos partes
        self.assertIn("R$", texto)
        self.assertIn("1.250,50", texto)
        print("✅ Formatação R$ OK")

if __name__ == '__main__':
    print("--- INICIANDO TESTES AUTOMATIZADOS DO SGF ---")
    unittest.main(verbosity=2)