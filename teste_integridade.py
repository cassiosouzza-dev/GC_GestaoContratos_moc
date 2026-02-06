import unittest
import json
import os
import sys

# Garante que o Python encontre o seu arquivo principal
# Se o seu arquivo se chama 'gestao_contratos.py', isso vai funcionar.
try:
    from gestao_contratos import Contrato, NotaEmpenho, SubContrato, Aditivo, Prestador
except ImportError:
    print("ERRO CRÍTICO: Não foi possível importar 'gestao_contratos.py'.")
    print("Verifique se este script de teste está na mesma pasta do arquivo principal.")
    sys.exit(1)


class TesteIntegridadeDados(unittest.TestCase):
    ARQUIVO_TEMP = "teste_integridade_temp.json"

    def setUp(self):
        """Cria um cenário de contrato complexo na memória antes do teste."""
        print("\n[SETUP] Montando cenário de dados complexo...")

        # 1. Prestador
        self.prestador = Prestador("Hospital Santa Cura", "Hosp. Cura", "12.345.678/0001-99", "7654321", "100")

        # 2. Contrato Base (Ciclo 0)
        self.contrato = Contrato(
            numero="123/2025",
            prestador="Hosp. Cura",
            descricao="Contrato de Gestão Hospitalar - Teste Full",
            valor_inicial=1_000_000.00,
            vig_inicio="01/01/2025",
            vig_fim="31/12/2025",
            comp_inicio="01/2025",
            comp_fim="12/2025",
            licitacao="PE 05/24",
            dispensa=""
        )

        # 3. Adiciona Serviço (Subcontrato)
        # Cenário: O serviço custa 100k no Ciclo 0, mas sobe para 150k no Ciclo 1
        servico = SubContrato("UTI Adulto", valor_mensal=0.0)
        servico.set_valor_ciclo(0, 500_000.00)  # Orçamento no contrato original
        servico.set_valor_ciclo(1, 750_000.00)  # Orçamento no aditivo futuro
        self.contrato.lista_servicos.append(servico)

        # 4. Adiciona Aditivo de Prazo (Cria o Ciclo 1)
        adt_prazo = Aditivo(id_aditivo=1, tipo="Prazo", valor=1_500_000.00,
                            data_nova="31/12/2026", descricao="Renovação 2026",
                            renovacao_valor=True, data_inicio_vigencia="01/01/2026")
        # Simula a lógica da classe principal que cria o ciclo automaticamente
        # Aqui fazemos manual para o teste de estrutura, ou usamos o método da classe se preferir
        # Vamos confiar no to_dict/from_dict, então vamos simular que o ciclo já existe na lista
        from gestao_contratos import CicloFinanceiro
        ciclo_novo = CicloFinanceiro(1, "1º TA Prazo/Valor", 1_500_000.00)
        self.contrato.ciclos.append(ciclo_novo)
        self.contrato.lista_aditivos.append(adt_prazo)

        # 5. Nota de Empenho (Vinculada ao Ciclo 0 e Serviço 0)
        ne = NotaEmpenho(
            numero="2025NE999",
            valor=100_000.00,
            descricao="Empenho Estimativo Jan/Fev",
            subcontrato_idx=0,  # Vincula à UTI Adulto
            fonte_recurso="1500",
            data_emissao="02/01/2025",
            ciclo_id=0
        )

        # 6. Movimentações Financeiras
        # Pagamento parcial
        ne.realizar_pagamento(50_000.00, "01/2025", "Pgto Janeiro")
        # Anulação de saldo (sobra)
        ne.realizar_anulacao(1_000.00, "Erro de cálculo")

        self.contrato.adicionar_nota_empenho(ne)

    def test_gravacao_e_leitura(self):
        """Salva em JSON, carrega de volta e compara se tudo sobreviveu."""
        print("[TESTE] Salvando e recarregando banco de dados...")

        # Simula o formato do banco de dados completo
        db_original = {
            "contratos": [self.contrato.to_dict()],
            "prestadores": [self.prestador.to_dict()],
            "logs": []
        }

        # 1. Escrita
        with open(self.ARQUIVO_TEMP, 'w', encoding='utf-8') as f:
            json.dump(db_original, f, indent=4, ensure_ascii=False)

        # 2. Leitura
        with open(self.ARQUIVO_TEMP, 'r', encoding='utf-8') as f:
            db_lido = json.load(f)

        # 3. Reconstrução dos Objetos
        c_lido = Contrato.from_dict(db_lido["contratos"][0])
        p_lido = Prestador.from_dict(db_lido["prestadores"][0])

        # --- VALIDAÇÕES (Onde a mágica acontece) ---

        print(" > Verificando dados do Prestador...")
        self.assertEqual(p_lido.cnpj, "12.345.678/0001-99")

        print(" > Verificando Contrato e Ciclos...")
        self.assertEqual(c_lido.numero, "123/2025")
        self.assertEqual(len(c_lido.ciclos), 2, "Deveriam existir 2 ciclos (Original + Aditivo)")
        self.assertEqual(c_lido.ciclos[1].valor_base, 1_500_000.00)

        print(" > Verificando Serviço e Orçamentos por Ciclo...")
        serv_lido = c_lido.lista_servicos[0]
        self.assertEqual(serv_lido.descricao, "UTI Adulto")
        # Verifica se o sistema lembra que no ciclo 0 era 500k e no ciclo 1 é 750k
        self.assertEqual(serv_lido.get_valor_ciclo(0), 500_000.00)
        self.assertEqual(serv_lido.get_valor_ciclo(1), 750_000.00)

        print(" > Verificando Nota de Empenho e Saldos...")
        ne_lida = c_lido.lista_notas_empenho[0]
        self.assertEqual(ne_lida.numero, "2025NE999")

        # Cálculo do Saldo: 100k (Inicial) - 50k (Pago) - 1k (Anulado) = 49k
        saldo_esperado = 49_000.00
        self.assertAlmostEqual(ne_lida.saldo_disponivel, saldo_esperado, places=2)

        print(" > Verificando Histórico de Movimentações...")
        self.assertEqual(len(ne_lida.historico), 3)  # Emissão + Pgto + Anulação
        self.assertEqual(ne_lida.historico[1].tipo, "Pagamento")
        self.assertEqual(ne_lida.historico[1].observacao, "Pgto Janeiro")

        print("\n[SUCESSO] O sistema passou em todos os testes de integridade!")

    def tearDown(self):
        """Limpa a sujeira depois do teste"""
        if os.path.exists(self.ARQUIVO_TEMP):
            os.remove(self.ARQUIVO_TEMP)


if __name__ == "__main__":
    unittest.main()