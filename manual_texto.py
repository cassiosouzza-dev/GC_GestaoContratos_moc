# MANUAL TÉCNICO OPERACIONAL - VERSÃO 9.0 (FINAL)
# ATUALIZADO COM NOTIFICAÇÕES, NOVOS MENUS E LAYOUTS

HTML_MANUAL = """
<h1 style='color: #2c3e50; text-align: center; font-family: "Segoe UI", Arial, sans-serif;'>MANUAL TÉCNICO DE OPERAÇÃO (MTO)</h1>
<p style='text-align: center; color: #7f8c8d; font-size: 11px;'>Sistema Integrado de Gestão de Contratos (GC) | Versão 9.0 | Build: AI-Enhanced + Notifications</p>
<hr style='border: 1px solid #34495e;'>

<h2 style='background-color: #34495e; color: white; padding: 5px;'>1. INTRODUÇÃO E ARQUITETURA LÓGICA</h2>

<h3>1.1 Propósito do Sistema</h3>
<p>O GC foi projetado para solucionar a fragmentação temporal de contratos de longo prazo, operando sob a arquitetura de <b>Ciclos Financeiros Independentes</b>.</p>

<h3>1.2 O Conceito de "Ciclo Financeiro" (Core)</h3>
<ul>
    <li><b>Definição:</b> Um ciclo representa um período orçamentário estanque (ex: Ano 2025 ou Vigência de um Aditivo).</li>
    <li><b>Isolamento:</b> O saldo de um Serviço no Ciclo 1 <b>NÃO</b> se comunica com o saldo do Ciclo 2.</li>
    <li><b>Visualização:</b> Na tela de detalhes, o campo <b>"Visualizar dados do Ciclo"</b> atua como filtro global. Todas as tabelas (Financeiro, Serviços) recarregam baseadas nesta escolha.</li>
</ul>

<hr>

<h2 style='background-color: #34495e; color: white; padding: 5px;'>2. MENUS E CADASTROS</h2>

<h3>2.1 Menu Prestadores (Gestão Corporativa)</h3>
<p>Centraliza o cadastro de empresas para evitar duplicidades.</p>
<ul>
    <li><b>Gerenciar Registro:</b> Abre a tabela de empresas cadastradas.
        <ul>
            <li><b>Menu de Contexto (Novidade):</b> Clique com o <b>botão direito</b> sobre uma empresa na lista para <i>Editar</i> ou <i>Excluir</i> rapidamente.</li>
            <li><b>Ordenação:</b> Clique no título das colunas para ordenar por Razão Social, Fantasia ou CNPJ.</li>
        </ul>
    </li>
</ul>

<h3>2.2 Menu Importação (Lote / CSV)</h3>
<p>Automação para carga de dados. Os arquivos devem ser CSV (separado por ponto e vírgula). Layouts obrigatórios:</p>
<ul>
    <li><b>Importar Prestadores:</b>
        <br><code>Razão Social; Nome Fantasia; CNPJ; CNES; Cód. CP</code>
    </li>
    <li><b>Importar Pagamentos:</b>
        <br><i>O sistema busca a NE pelo número exato dentro do contrato aberto.</i>
        <br><code>Número da NE; Valor (ex: 1500,50); Competência (MM/AAAA)</code>
    </li>
</ul>

<h3>2.3 Menu Nuvem (Google Drive)</h3>
<ul>
    <li><b>Sincronizar:</b> Mescla dados locais com a nuvem.</li>
    <li><b>Baixar Base Separada:</b> Cria uma cópia local (Sandbox) para consulta segura sem alterar seus dados principais.</li>
</ul>

<hr>

<h2 style='background-color: #34495e; color: white; padding: 5px;'>3. DASHBOARD (TELA INICIAL)</h2>

<h3>3.1 Barra Superior (Top Bar)</h3>
<p>Localizada no canto superior direito, contém as ferramentas de inteligência:</p>
<ul>
    <li><b>[💬 IA]:</b> Abre o chat global com o Google Gemini para perguntas sobre toda a base de dados.</li>
    <li><b>[🔔 Notificações]:</b> Ícone do "Sino Inteligente".
        <ul>
            <li>Fica <b>Cinza</b> se estiver tudo OK.</li>
            <li>Fica <b>Vermelho</b> com contador numérico se houver alertas (Prazos ou Saldos).</li>
        </ul>
    </li>
</ul>

<h3>3.2 Central de Notificações</h3>
<p>Ao clicar no sino, abre-se a janela de alertas. O sistema monitora automaticamente:</p>
<ul>
    <li><b>Vencimentos:</b> Alerta amarelo (45 dias) e vermelho (vencido).</li>
    <li><b>Déficit Orçamentário:</b> Alerta se algum serviço gastou mais que o previsto.</li>
    <li><b>Botão [🤖 Gerar Plano de Ação]:</b> A IA lê os alertas listados e gera um relatório executivo sugerindo o que deve ser priorizado (ex: "Inicie o aditivo do contrato X imediatamente").</li>
</ul>

<h3>3.3 Tabela de Pesquisa Expandida</h3>
<p>A tabela principal agora ocupa toda a largura da tela e exibe 8 colunas de dados:</p>
<ul>
    <li><b>Colunas:</b> Número, Prestador (Fantasia), Razão Social, CNPJ, CNES, Cód. CP, Objeto, Status.</li>
    <li><b>Busca Inteligente:</b> A barra de pesquisa procura simultaneamente em todos esses campos (inclusive CNPJ).</li>
</ul>

<hr>

<h2 style='background-color: #34495e; color: white; padding: 5px;'>4. GESTÃO DE CONTRATOS (DETALHES)</h2>

<h3>4.1 Aba Financeiro (Execução)</h3>
<ul>
    <li><b>Botão [+ NE]:</b> Emite nota de empenho (valida saldo do serviço).</li>
    <li><b>Botão [Pagar]:</b> Baixa financeira. Permite seleção múltipla de meses.</li>
    <li><b>Botão [Anular]:</b> Estorno de saldo. Devolve o valor para o serviço.</li>
    <li><b>Botão [Analisar Risco]:</b> A IA audita o ciclo atual em busca de desequilíbrios.</li>
    <li><b>Maximizar Histórico:</b> Botão acima da tabela inferior para ver o extrato financeiro em tela cheia.</li>
</ul>

<h3>4.2 Aba Serviços (Itens)</h3>
<p>Gerenciamento dos itens de despesa.</p>
<ul>
    <li><b>Cálculo em Tempo Real:</b> Colunas mostram Orçamento vs. Empenhado vs. Pago.</li>
    <li><b>Detalhamento (Duplo Clique):</b> Ao clicar duas vezes num serviço, abre-se uma visão profunda:
        <ol>
            <li><b>Aba Evolução Mensal:</b> Matriz mês a mês. Meses sem pagamento ficam vazios (traço) para limpeza visual. O saldo mensal é calculado linha a linha.</li>
            <li><b>Aba Por NE:</b> Lista quais empenhos custeiam aquele serviço.</li>
            <li><b>Botão IA:</b> Análise focada apenas no ritmo daquele serviço específico.</li>
        </ol>
    </li>
</ul>

<h3>4.3 Aba Aditivos</h3>
<p>Gerencia alterações. Tipos:</p>
<ul>
    <li><b>Valor:</b> Soma/Subtrai orçamento. Pode ser vinculado a um serviço específico.</li>
    <li><b>Prazo (Com Renovação):</b> Cria um <b>Novo Ciclo Financeiro</b> e zera os saldos para o novo período.</li>
</ul>

<hr>

<h2 style='background-color: #c0392b; color: white; padding: 5px;'>5. REGRAS DE INTEGRIDADE</h2>

<table border="1" cellpadding="5" cellspacing="0" width="100%" style="font-size: 11px;">
    <tr style="background-color: #f2f2f2;">
        <th>Ação</th>
        <th>Regra de Bloqueio</th>
    </tr>
    <tr>
        <td><b>Emitir NE</b></td>
        <td>Bloqueado se <code>Valor > Saldo Livre do Serviço</code> no ciclo atual.</td>
    </tr>
    <tr>
        <td><b>Pagar</b></td>
        <td>Bloqueado se <code>Valor > Saldo da NE</code>. Não existe saldo negativo.</td>
    </tr>
    <tr>
        <td><b>Excluir Serviço</b></td>
        <td>Impedido se houver NEs vinculadas neste ciclo. (Para exclusão total, não pode haver NE em nenhum ciclo).</td>
    </tr>
    <tr>
        <td><b>Importação</b></td>
        <td>O sistema valida se as NEs do CSV de pagamentos realmente existem no contrato aberto.</td>
    </tr>
</table>

<hr>
<p style='text-align: right; font-size: 10px; color: #555;'>MTO - GC Gestor v9.0 (Final Edition)</p>
"""