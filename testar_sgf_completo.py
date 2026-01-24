import unittest
import os
import sys
import json
from datetime import datetime
from PyQt6.QtWidgets import QApplication

# Tenta importar o sistema principal
try:
    import gestao_contratos as sgf
except ImportError:
    print("❌ ERRO CRÍTICO: O arquivo 'gestao_contratos.py' não foi encontrado nesta pasta.")
    sys.exit(1)

# Inicializa QApplication para evitar erros de fontes/gráficos do Qt durante os testes
app = QApplication(sys.argv)

class TesteSGFCompleto(unittest.TestCase):
    
    def setUp(self):
        """PREPARAÇÃO: Executa antes de CADA teste para garantir ambiente limpo."""
        # Cria um contrato base: R$ 100.000,00 inicial
        self.ctr = sgf.Contrato(
            numero="CTR-2026/999",
            prestador="Hospital de Testes S.A.",
            descricao="Gestão Hospitalar Completa",
            valor_inicial=100000.00,
            vig_inicio="01/01/2026",
            vig_fim="31/12/2026",
            comp_inicio="01/2026",
            comp_fim="12/2026",
            licitacao="Dispensa 01",
            dispensa=""
        )
        
        # Adiciona um Serviço (Subcontrato) de R$ 20.000,00
        # Isso significa que, dos 100k do contrato, 20k são exclusivos para "Limpeza"
        self.servico_limpeza = sgf.SubContrato("Serviço de Limpeza", valor_mensal=2000.00)
        self.servico_limpeza.set_valor_ciclo(0, 20000.00) # Vincula 20k ao Ciclo 0
        self.ctr.lista_servicos.append(self.servico_limpeza)

    def test_01_validacao_teto_contrato(self):
        """TESTE 01: O sistema impede gastar mais que o valor total do contrato?"""
        print("\n--- Teste 01: Teto Global do Contrato ---")
        
        # Tenta empenhar 101.000,00 (O contrato só tem 100.000,00)
        ne_invalida = sgf.NotaEmpenho("NE-OVER", 101000.00, "Tentativa de Fraude", -1, "100", "01/01/2026", 0)
        ok, msg = self.ctr.adicionar_nota_empenho(ne_invalida)
        
        self.assertFalse(ok, "FALHA: Sistema permitiu empenhar mais que o teto do contrato!")
        print(f"✅ Bloqueio Funcionou: {msg}")

    def test_02_validacao_teto_servico(self):
        """TESTE 02: O sistema impede gastar mais que o orçamento do serviço?"""
        print("\n--- Teste 02: Teto Específico do Serviço ---")
        
        # O serviço de limpeza tem 20k. O contrato tem 100k livres (no total).
        # Tenta tirar 25k do serviço de limpeza.
        ne_servico_estouro = sgf.NotaEmpenho(
            "NE-LIMPEZA-FAIL", 25000.00, "Limpeza Geral", 
            0, # Índice 0 = Serviço de Limpeza
            "100", "01/01/2026", 0
        )
        
        ok, msg = self.ctr.adicionar_nota_empenho(ne_servico_estouro)
        self.assertFalse(ok, "FALHA: Sistema permitiu estourar o orçamento do serviço!")
        print(f"✅ Bloqueio de Serviço Funcionou: {msg}")
        
        # Agora tenta tirar 15k (deve passar)
        ne_servico_ok = sgf.NotaEmpenho("NE-LIMPEZA-OK", 15000.00, "Limpeza ok", 0, "100", "01/01/2026", 0)
        ok, msg = self.ctr.adicionar_nota_empenho(ne_servico_ok)
        self.assertTrue(ok, f"FALHA: Deveria ter aceitado NE dentro do saldo. Erro: {msg}")
        
        # Saldo restante do serviço deve ser 5k
        # (Não temos método direto público fácil, mas podemos calcular somando NEs)
        gasto = sum(n.valor_inicial for n in self.ctr.lista_notas_empenho if n.subcontrato_idx == 0)
        self.assertEqual(gasto, 15000.00)
        print(f"✅ Saldo do serviço atualizado corretamente. Gasto: {gasto}")

    def test_03_aditivo_prazo_gera_novo_ciclo(self):
        """TESTE 03: Aditivo de Prazo com Valor cria um Novo Ciclo Financeiro?"""
        print("\n--- Teste 03: Renovação Contratual (Novo Ciclo) ---")
        
        # Cenário: Renovação por mais 12 meses com mais R$ 100.000,00
        adt_renovacao = sgf.Aditivo(
            id_aditivo=0, 
            tipo="Prazo", 
            valor=100000.00, 
            data_nova="31/12/2027", 
            descricao="Renovação 2027", 
            renovacao_valor=True, 
            data_inicio_vigencia="01/01/2027"
        )
        
        msg = self.ctr.adicionar_aditivo(adt_renovacao)
        print(f"ℹ️ Resultado Aditivo: {msg}")
        
        # Verificações
        self.assertEqual(len(self.ctr.ciclos), 2, "FALHA: Deveria ter criado o Ciclo 2")
        ciclo_novo = self.ctr.ciclos[1]
        self.assertEqual(ciclo_novo.valor_base, 100000.00, "FALHA: Valor base do novo ciclo incorreto")
        
        # Verifica se o serviço de limpeza foi copiado para o novo ciclo (mas com saldo zerado ou replicado?)
        # A lógica atual do seu código replica o valor antigo para o novo ciclo ao criar aditivo de prazo
        val_limpeza_ciclo2 = self.servico_limpeza.get_valor_ciclo(1)
        self.assertEqual(val_limpeza_ciclo2, 20000.00, "FALHA: Orçamento do serviço não foi replicado para 2027")
        print("✅ Novo Ciclo criado e Orçamentos de Serviço replicados com sucesso.")

    def test_04_aditivo_valor_especifico(self):
        """TESTE 04: Aditivo de Valor vinculado a um Serviço aumenta o saldo dele?"""
        print("\n--- Teste 04: Aditivo de Valor (Acréscimo) ---")
        
        # Temos 20k no serviço. Vamos dar um aditivo de +5k APENAS para o serviço.
        # E vamos vincular isso ao Ciclo 0 (Inicial)
        adt_valor = sgf.Aditivo(
            id_aditivo=0, tipo="Valor", valor=5000.00, descricao="Aumento Limpeza",
            renovacao_valor=False, servico_idx=0 # Índice 0 = Limpeza
        )
        
        # Usa id_ciclo_alvo=0 para forçar cair no primeiro ciclo
        self.ctr.adicionar_aditivo(adt_valor, id_ciclo_alvo=0)
        
        # Verifica se o teto do serviço subiu de 20k para 25k
        novo_teto_servico = self.servico_limpeza.get_valor_ciclo(0)
        self.assertEqual(novo_teto_servico, 25000.00, f"FALHA: Serviço devia ter 25k, tem {novo_teto_servico}")
        
        # Verifica se o teto GERAL do ciclo também subiu (100k + 5k = 105k)
        teto_ciclo = self.ctr.ciclos[0].get_teto_total()
        self.assertEqual(teto_ciclo, 105000.00, "FALHA: Teto global não subiu com o aditivo")
        print("✅ Aditivo incrementou Saldo Global e Saldo do Serviço.")

    def test_05_fluxo_pagamento_e_estorno(self):
        """TESTE 05: Pagamento, Edição (Erro e Sucesso) e Exclusão"""
        print("\n--- Teste 05: Fluxo Financeiro Completo ---")
        
        # 1. Cria NE de 10k
        ne = sgf.NotaEmpenho("NE-FLUXO", 10000.00, "Teste Fluxo", -1, "100", "05/01/2026", 0)
        self.ctr.adicionar_nota_empenho(ne)
        
        # 2. Paga 4k
        ok, msg = ne.realizar_pagamento(4000.00, "01/2026")
        self.assertTrue(ok, "Pagamento de 4k falhou")
        self.assertEqual(ne.valor_pago, 4000.00)
        
        # 3. Tenta Editar para 11k (Maior que a NE inteira) -> Deve Falhar
        # Índice 1 pois o 0 é a "Emissão Original"
        ok, msg = ne.editar_movimentacao(1, 11000.00, "01/2026")
        self.assertFalse(ok, "Sistema permitiu editar pagamento para valor maior que a NE!")
        self.assertEqual(ne.valor_pago, 4000.00, "Saldo foi alterado indevidamente após falha")
        print("✅ Bloqueio de Edição Indevida OK")
        
        # 4. Edita para 6k (Válido) -> Deve Sucesso
        ok, msg = ne.editar_movimentacao(1, 6000.00, "02/2026") # Mudou valor e data
        self.assertTrue(ok, f"Edição válida falhou: {msg}")
        self.assertEqual(ne.valor_pago, 6000.00)
        self.assertEqual(ne.historico[1].competencia, "02/2026")
        print("✅ Edição Válida OK")
        
        # 5. Exclui Pagamento -> Saldo deve voltar a 0 (pago)
        ok = ne.excluir_movimentacao(1)
        self.assertTrue(ok, "Exclusão falhou")
        self.assertEqual(ne.valor_pago, 0.00, "Valor pago não zerou após exclusão")
        print("✅ Exclusão e Estorno de Saldo OK")

    def test_06_integridade_json(self):
        """TESTE 06: Salvar e Carregar mantém os dados complexos?"""
        print("\n--- Teste 06: Persistência de Dados (JSON) ---")
        
        # Preenche o contrato com dados complexos
        self.ctr.adicionar_aditivo(sgf.Aditivo(0, "Valor", 500.00, None, "Teste JSON", False))
        ne = sgf.NotaEmpenho("NE-JSON", 100.00, "Teste", -1, "100", "01/01/2026", 0)
        ne.realizar_pagamento(50.00, "01/2026")
        self.ctr.adicionar_nota_empenho(ne)
        
        # Salva
        arquivo_teste = "temp_test_db.json"
        try:
            dados = [self.ctr.to_dict()]
            with open(arquivo_teste, 'w', encoding='utf-8') as f:
                json.dump(dados, f)
            
            # Carrega em novo objeto
            with open(arquivo_teste, 'r', encoding='utf-8') as f:
                dados_lidos = json.load(f)
                ctr_lido = sgf.Contrato.from_dict(dados_lidos[0])
            
            # Comparações
            self.assertEqual(ctr_lido.numero, self.ctr.numero)
            self.assertEqual(len(ctr_lido.lista_notas_empenho), 1)
            self.assertEqual(ctr_lido.lista_notas_empenho[0].valor_pago, 50.00)
            self.assertEqual(len(ctr_lido.ciclos[0].aditivos_valor), 1)
            print("✅ Integridade do JSON verificada com sucesso.")
            
        finally:
            if os.path.exists(arquivo_teste):
                os.remove(arquivo_teste)

if __name__ == '__main__':
    print("=======================================================")
    print(" INICIANDO BATERIA DE TESTES DETALHADA DO SGF")
    print("=======================================================")
    unittest.main(verbosity=2)