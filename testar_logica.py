import unittest
from gestao_contratos import Contrato, NotaEmpenho, SubContrato, Aditivo


class TesteRegrasNegocio(unittest.TestCase):

    def setUp(self):
        """Cria um ambiente limpo para cada teste"""
        self.contrato = Contrato("CTR-TESTE", "Empresa X", "Objeto X", 10000.00,
                                 "01/01/2025", "31/12/2025", "01/2025", "12/2025", "Lic", "Disp")

        # Serviço com R$ 1.000,00 de orçamento no Ciclo 0
        self.servico = SubContrato("Serviço Limitado", 100.00)
        self.servico.set_valor_ciclo(0, 1000.00)
        self.contrato.lista_servicos.append(self.servico)

    def test_bloqueio_ne_sem_saldo_servico(self):
        """Tenta emitir uma NE maior que o orçamento do serviço"""
        print("Testando bloqueio de NE sem saldo...")

        # Tenta criar NE de 1.500 (O serviço só tem 1.000)
        ne_invalida = NotaEmpenho("NE-FAIL", 1500.00, "Desc", 0, "Fonte", "01/01/2025", 0)

        ok, msg = self.contrato.adicionar_nota_empenho(ne_invalida)

        self.assertFalse(ok, "ERRO: O sistema permitiu criar NE sem saldo no serviço!")
        self.assertIn("excede o saldo do serviço", msg)

    def test_bloqueio_pagamento_sem_saldo_ne(self):
        """Tenta pagar mais do que o valor da NE"""
        print("Testando bloqueio de Pagamento excedente...")

        # Cria NE válida de 1.000
        ne = NotaEmpenho("NE-OK", 1000.00, "Desc", 0, "Fonte", "01/01/2025", 0)
        self.contrato.adicionar_nota_empenho(ne)

        # Tenta pagar 1.001
        ok, msg = ne.realizar_pagamento(1001.00, "01/2025")

        self.assertFalse(ok, "ERRO: O sistema permitiu pagar mais que o valor da NE!")
        self.assertIn("Saldo insuficiente", msg)

    def test_bloqueio_anulacao_excessiva(self):
        """Tenta anular um valor que já foi pago"""
        print("Testando bloqueio de Anulação inválida...")

        ne = NotaEmpenho("NE-ANULA", 1000.00, "Desc", 0, "Fonte", "01/01/2025", 0)
        self.contrato.adicionar_nota_empenho(ne)

        # Paga 800 (Saldo sobra 200)
        ne.realizar_pagamento(800.00, "01/2025")

        # Tenta anular 300 (Só tem 200 sobrando)
        ok, msg = ne.realizar_anulacao(300.00)

        self.assertFalse(ok, "ERRO: O sistema permitiu anular valor já gasto!")
        self.assertAlmostEqual(ne.saldo_disponivel, 200.00)

    def test_ciclo_financeiro_isolado(self):
        """Garante que saldo do Ciclo 0 não vaza para o Ciclo 1"""
        print("Testando isolamento de ciclos...")

        # Ciclo 0 tem 1.000 (configurado no setUp)

        # Adiciona Ciclo 1 vazio (ou com valor diferente)
        from gestao_contratos import CicloFinanceiro
        self.contrato.ciclos.append(CicloFinanceiro(1, "Ciclo 2026", 5000.00))
        self.servico.set_valor_ciclo(1, 5000.00)

        # Tenta usar NE no Ciclo 1 com valor do Ciclo 0 (1.000)
        # Se eu tentar emitir 2.000 no Ciclo 1, deve permitir (tem 5.000 lá)
        # Se eu tentar emitir 2.000 no Ciclo 0, deve bloquear (tem 1.000 lá)

        ne_ciclo0 = NotaEmpenho("NE-C0", 2000.00, "", 0, "", "", 0)
        ne_ciclo1 = NotaEmpenho("NE-C1", 2000.00, "", 0, "", "", 1)

        ok0, _ = self.contrato.adicionar_nota_empenho(ne_ciclo0)
        ok1, _ = self.contrato.adicionar_nota_empenho(ne_ciclo1)

        self.assertFalse(ok0, "Falha no isolamento: Ciclo 0 aceitou valor excessivo")
        self.assertTrue(ok1, "Falha no isolamento: Ciclo 1 bloqueou valor válido")


if __name__ == '__main__':
    unittest.main()