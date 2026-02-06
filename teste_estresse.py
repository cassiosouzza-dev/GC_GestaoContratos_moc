import time
import sys
from gestao_contratos import Contrato, NotaEmpenho, SubContrato


def executar_teste_estresse(qtd_contratos=5000):
    print(f"--- INICIANDO TESTE DE ESTRESSE ---")
    print(f"Objetivo: Gerar {qtd_contratos} Contratos completos na memória RAM.")

    inicio = time.time()
    banco_dados = []

    print("1. Gerando Contratos e Serviços...")
    for i in range(qtd_contratos):
        # Cria Contrato
        c = Contrato(f"CTR-{i}", f"Prestador {i}", "Objeto Teste Carga", 100000.0,
                     "01/01/2025", "31/12/2025", "01/25", "12/25", "PE", "N/A")

        # Cria Serviço
        sub = SubContrato(f"Serviço Padrão {i}", 1000.0)
        sub.set_valor_ciclo(0, 100000.0)
        c.lista_servicos.append(sub)

        # Cria 5 Notas de Empenho por contrato
        for n in range(5):
            ne = NotaEmpenho(f"NE-{i}-{n}", 5000.0, "NE Carga", 0, "100", "01/01/2025", 0)

            # Realiza 1 Pagamento em cada NE
            ne.realizar_pagamento(1000.0, "01/2025", "Pgto Carga")

            c.adicionar_nota_empenho(ne)

        banco_dados.append(c)

        if i % 1000 == 0 and i > 0:
            print(f"   -> {i} contratos processados...")

    fim = time.time()
    tempo_total = fim - inicio

    # Estatísticas Finais
    total_contratos = len(banco_dados)
    total_nes = sum(len(c.lista_notas_empenho) for c in banco_dados)
    total_movimentos = sum(len(ne.historico) for c in banco_dados for ne in c.lista_notas_empenho)

    print("\n--- RESULTADOS DO TESTE ---")
    print(f"Tempo Total: {tempo_total:.4f} segundos")
    print(f"Contratos Gerados: {total_contratos}")
    print(f"Notas de Empenho: {total_nes}")
    print(f"Movimentações (Emissões + Pagamentos): {total_movimentos}")
    print(f"Média: {tempo_total / total_contratos:.6f} seg/contrato")

    # Validação de Performance
    if tempo_total < 5.0:
        print("\n✅ PERFORMANCE: EXCELENTE (Voando baixo!)")
    elif tempo_total < 15.0:
        print("\n⚠️ PERFORMANCE: BOA (Aceitável para grandes volumes)")
    else:
        print("\n❌ PERFORMANCE: LENTA (Pode precisar de otimização)")

    # Validação de Dados (Amostragem)
    ultimo = banco_dados[-1]
    print(f"\nVerificação Amostral (Último Contrato):")
    print(f"Número: {ultimo.numero}")
    print(f"Qtd NEs: {len(ultimo.lista_notas_empenho)} (Esperado: 5)")
    print(f"Saldo NE 0: {fmt_br(ultimo.lista_notas_empenho[0].saldo_disponivel)} (Esperado: R$ 4.000,00)")


def fmt_br(val):
    return f"R$ {val:,.2f}"


if __name__ == "__main__":
    executar_teste_estresse()