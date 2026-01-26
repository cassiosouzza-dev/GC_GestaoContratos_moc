# MANUAL TÉCNICO OPERACIONAL - VERSÃO 9.5 (ENTERPRISE)
# ATUALIZADO: DETALHAMENTO DE RELATÓRIOS, BUSCAS, ÁRVORES HIERÁRQUICAS E FLUXOS

HTML_MANUAL = """
<style>
    body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }
    h1 { color: #2c3e50; text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; }
    h2 { background-color: #34495e; color: white; padding: 8px 15px; margin-top: 30px; border-radius: 4px; font-size: 18px; }
    h3 { color: #16a085; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-top: 25px; }
    h4 { color: #2980b9; margin-top: 15px; margin-bottom: 5px; font-size: 14px; }
    p { margin-bottom: 15px; text-align: justify; }
    ul, ol { margin-bottom: 15px; }
    li { margin-bottom: 5px; }
    code { background-color: #f8f9fa; padding: 2px 5px; border: 1px solid #ddd; border-radius: 3px; font-family: Consolas, monospace; color: #c7254e; }
    .box-info { background-color: #e8f6f3; border-left: 5px solid #1abc9c; padding: 10px; margin: 15px 0; font-size: 13px; }
    .box-alert { background-color: #fdedec; border-left: 5px solid #e74c3c; padding: 10px; margin: 15px 0; font-size: 13px; }
    table { width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 20px; }
    th { background-color: #ecf0f1; border: 1px solid #bdc3c7; padding: 8px; text-align: left; }
    td { border: 1px solid #bdc3c7; padding: 8px; }
</style>

<h1>MANUAL TÉCNICO DE OPERAÇÃO (MTO)</h1>
<p style='text-align: center; color: #7f8c8d; font-size: 12px;'>GC Gestor | Versão 9.5 Enterprise | Revisão: Jan/2026</p>

<h2>1. CONCEITOS FUNDAMENTAIS E ARQUITETURA</h2>

<h3>1.1 A Lógica de Ciclos Financeiros</h3>
<p>Diferente de planilhas comuns que tratam o contrato como uma linha contínua, o GC Gestor opera sob a arquitetura de <b>Ciclos Financeiros Estanques</b>. Isso é crucial para contratos de longa duração (48, 60 meses) ou com múltiplas renovações.</p>
<ul>
    <li><b>O que é um Ciclo:</b> Um período orçamentário isolado. Pode ser o "Contrato Inicial (12 meses)" ou um "1º Termo Aditivo de Prazo".</li>
    <li><b>Isolamento de Saldos:</b> O saldo não utilizado no Ciclo 1 <b>NÃO</b> é transferido automaticamente para o Ciclo 2. Cada ciclo nasce com seu próprio orçamento e teto.</li>
    <li><b>Navegação:</b> Na tela de detalhes do contrato, o menu suspenso <i>"Visualizar dados do Ciclo"</i> funciona como uma "máquina do tempo". Ao alterar o ciclo ali, todas as tabelas (Financeiro, Serviços, Gráficos) são recarregadas para exibir apenas os dados daquele período específico.</li>
</ul>

<div class="box-info">
    <b>Nota de Auditoria:</b> O sistema mantém o histórico de qual ciclo o usuário estava visualizando por último, para evitar erros de lançamento em períodos errados.
</div>

<hr>

<h2>2. INTERFACE E NAVEGAÇÃO AVANÇADA</h2>

<h3>2.1 Barra de Status (Rodapé)</h3>
<p>Localizada na parte inferior da janela, esta barra fornece feedback constante sobre o estado do sistema:</p>
<ul>
    <li><b>Esquerda:</b> Exibe mensagens de ação (ex: "Salvando dados...", "Conectando à IA...").</li>
    <li><b>Direita:</b> Identificação do usuário logado (Nome) e Versão do Sistema. Isso é essencial para prints de tela em auditorias.</li>
</ul>

<h3>2.2 Filtros e Ordenação Inteligente</h3>
<p>Todas as tabelas de dados do sistema (Pesquisa Principal, Financeiro, Serviços, Prestadores) possuem recursos avançados de manipulação:</p>
<ul>
    <li><b>Ordenação por Coluna:</b> Clicar no cabeçalho de qualquer coluna (ex: "Valor", "Data", "Razão Social") reordena as linhas instantaneamente de forma ascendente ou descendente. O sistema reconhece datas e valores monetários para ordenar corretamente (não alfabeticamente).</li>
    <li><b>Busca Contextual:</b> 
        <ul>
            <li>Na <b>Tela Inicial</b>, a busca varre Número, Prestador, CNPJ e Objeto simultaneamente.</li>
            <li>Na <b>Aba Financeiro</b>, a nova barra de busca filtra Notas de Empenho por Número, Fonte de Recurso ou Descrição.</li>
            <li>Na <b>Aba Serviços</b>, é possível filtrar a lista de itens pela descrição do serviço.</li>
        </ul>
    </li>
</ul>

<hr>

<h2>3. RELATÓRIOS EXECUTIVOS E PRESTAÇÃO DE CONTAS</h2>

<p>O menu <b>Relatórios</b> foi completamente reestruturado para oferecer visões gerenciais distintas. Todos os relatórios são gerados em HTML renderizado localmente, abrindo automaticamente no navegador padrão com a janela de impressão (PDF/Papel) já acionada.</p>

<h3>3.1 Geral do Contrato (Visão Macro)</h3>
<p>Gera um documento contendo o cabeçalho completo do contrato (Vigência, Valores, Objeto) seguido de uma lista sumária de todas as Notas de Empenho emitidas, com seus valores originais, totais pagos e saldos disponíveis. Ideal para capa de processo de pagamento.</p>

<h3>3.2 Por Serviço (Detalhamento Analítico)</h3>
<p>Foca na execução de um item específico (ex: "Serviço de Limpeza"). O diferencial deste relatório é a quebra detalhada:</p>
<ul>
    <li>Mostra o orçamento do serviço no ciclo atual.</li>
    <li>Lista cada Nota de Empenho vinculada a este serviço.</li>
    <li>Dentro de cada linha de NE, exibe uma <b>sub-tabela</b> com todos os pagamentos realizados (Data e Valor), permitindo rastrear exatamente quando o saldo foi consumido.</li>
</ul>

<h3>3.3 Evolução Mensal (Duas Modalidades)</h3>
<p>Esta categoria responde à pergunta: <i>"Quanto gastamos em cada mês?"</i>.</p>
<ul>
    <li><b>Visão Contrato Global:</b> Soma todos os pagamentos de todos os serviços naquela competência (Mês/Ano). Compara com a meta mensal global do contrato.</li>
    <li><b>Visão Por Serviço:</b> Permite selecionar um item (ex: "Locação de Veículos") e ver a evolução mensal apenas dele, comparando com o valor unitário mensal contratado.</li>
</ul>
<p>Ambos os relatórios exibem colunas de "Déficit/Superávit" visualmente coloridas (Vermelho/Verde) para indicar desvios da meta.</p>

<h3>3.4 Caderno de Notas de Empenho (Extrato Bancário)</h3>
<p>Gera um relatório extenso, estilo "Extrato", para cada Nota de Empenho ativa no ciclo. Ele imprime bloco a bloco, mostrando a emissão, e linha a linha cada abate (pagamento ou anulação), calculando o saldo remanescente progressivamente.</p>

<hr>

<h2>4. OPERACIONALIZAÇÃO DOS DADOS</h2>

<h3>4.1 Gestão de Serviços (Aba 3)</h3>
<p>Esta é a área de controle orçamentário. As colunas são dinâmicas:</p>
<ul>
    <li><b>Orçamento (neste ciclo):</b> Quanto dinheiro este item tem para gastar neste período.</li>
    <li><b>Empenhado:</b> O total bruto reservado em Notas de Empenho.</li>
    <li><b>Não Empenhado:</b> O saldo "livre" que ainda permite a emissão de novas NEs.</li>
    <li><b>Saldo de Empenhos:</b> Dinheiro que já está em NEs mas ainda não foi pago (Liquidação pendente).</li>
</ul>

<h4>4.1.1 Detalhamento Profundo (Duplo Clique)</h4>
<p>Ao dar duplo clique em um serviço, abre-se a janela de <b>Detalhamento Avançado</b>:</p>
<ul>
    <li><b>Aba Evolução Mensal:</b> Uma matriz que cruza Competências vs. Valores. Mostra percentuais de execução e acumula o saldo mês a mês.</li>
    <li><b>Aba Por Nota de Empenho (Árvore Hierárquica):</b> 
        <br>Esta visualização utiliza uma estrutura de árvore (Tree View). 
        <br>1. O "Nó Pai" é a Nota de Empenho (Mostra número e valor total).
        <br>2. Ao expandir o nó (clicando na seta), revelam-se os "Nós Filhos", que são os pagamentos individuais e anulações, com suas respectivas competências e datas.
        <br>3. O botão <b>"Copiar Tabela"</b> nesta tela é inteligente: ele converte essa estrutura visual em texto tabulado compatível com Excel, mantendo a relação de pertencimento.
    </li>
</ul>

<h3>4.2 Gestão Financeira (Aba 2)</h3>
<p>O coração da execução. Aqui ocorrem os lançamentos.</p>
<ul>
    <li><b>Anulação de Empenho:</b> O botão "Anular" permite estornar valores. A anulação reduz o valor "Empenhado" e devolve o saldo para o Serviço de origem, permitindo que o recurso seja reutilizado em outra NE.</li>
    <li><b>Pagamentos:</b> Ao realizar um pagamento, o sistema solicita as competências. É possível digitar múltiplas (ex: "01/2025, 02/2025"). Isso abate o saldo da NE, mas não devolve o recurso para o contrato (pois foi gasto).</li>
</ul>

<hr>

<h2>5. FERRAMENTAS ENTERPRISE E INTEGRIDADE</h2>

<h3>5.1 Menu Ferramentas</h3>
<ul>
    <li><b>Calculadora do Sistema:</b> Atalho rápido para a calculadora nativa do Windows.</li>
    <li><b>Verificar Integridade:</b> Realiza um <i>Health Check</i> no banco de dados JSON, contando registros e verificando a consistência do arquivo físico.</li>
    <li><b>Assistente de Importação:</b> Permite carga em lote via arquivos CSV padronizados. Essencial para implantação inicial de dados legados.</li>
</ul>

<h3>5.2 Menu Arquivo > Backup de Segurança</h3>
<p>Gera instantaneamente uma cópia do banco de dados atual (arquivo <code>.json</code>) na mesma pasta, renomeando-o com um carimbo de data e hora (ex: <code>dados_BACKUP_20250126_1030.bak</code>). Use antes de grandes alterações ou importações.</p>

<div class="box-alert">
    <b>Atenção:</b> O sistema de Auditoria (Logs) registra quem fez o quê, mas não desfaz ações. O Backup é sua rede de segurança para restauração de dados.
</div>

<h3>5.3 Menu Nuvem (Drive)</h3>
<p>Permite sincronização bidirecional. O recurso "Mesclar" é capaz de unir lançamentos feitos em computadores diferentes (desde que não conflitem no mesmo ID), ideal para trabalho em equipe distribuída.</p>

<hr>

<h2 style='background-color: #c0392b; color: white; padding: 5px;'>6. REGRAS DE BLOQUEIO E VALIDAÇÃO</h2>

<table border="1" cellpadding="5" cellspacing="0">
    <tr style="background-color: #f2f2f2;">
        <th>Operação</th>
        <th>Condição de Bloqueio (O sistema impede a ação)</th>
    </tr>
    <tr>
        <td><b>Emitir Nova NE</b></td>
        <td>Se o valor da NE for maior que o <b>Saldo Não Empenhado</b> do serviço escolhido no ciclo atual.</td>
    </tr>
    <tr>
        <td><b>Realizar Pagamento</b></td>
        <td>Se o valor do pagamento for maior que o <b>Saldo Disponível</b> da Nota de Empenho.</td>
    </tr>
    <tr>
        <td><b>Excluir Serviço</b></td>
        <td>
            1. Bloqueado totalmente se houver NEs vinculadas a este serviço no ciclo atual.
            <br>2. Se houver histórico em <i>outros</i> ciclos, o sistema pergunta se deseja "Excluir Totalmente" (apaga tudo) ou "Remover deste Ciclo" (apenas desvincula o orçamento atual).
        </td>
    </tr>
    <tr>
        <td><b>Excluir Aditivo</b></td>
        <td>Se for um aditivo de "Prazo com Renovação" que gerou um Ciclo Financeiro, a exclusão é bloqueada caso já existam NEs lançadas dentro desse ciclo criado.</td>
    </tr>
</table>

<p style='text-align: right; font-size: 10px; color: #555; margin-top: 50px;'>Documentação gerada internamente pelo sistema GC Gestor.</p>
"""