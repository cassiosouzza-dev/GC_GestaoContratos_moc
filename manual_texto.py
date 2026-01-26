# MANUAL TÉCNICO OPERACIONAL - GC GESTOR ENTERPRISE
# DOCUMENTAÇÃO OFICIAL UNIFICADA

HTML_MANUAL = """
<style>
    body { font-family: 'Segoe UI', 'Roboto', Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; margin: 20px; background-color: #fdfdfd; }
    h1 { color: #2c3e50; text-align: center; border-bottom: 3px solid #2c3e50; padding-bottom: 15px; margin-bottom: 30px; font-size: 28px; }

    /* Hierarquia Visual */
    h2 { 
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); 
        color: white; 
        padding: 12px 20px; 
        margin-top: 50px; 
        border-radius: 6px; 
        font-size: 18px; 
        text-transform: uppercase; 
        letter-spacing: 1px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    h3 { 
        color: #2980b9; 
        border-left: 5px solid #2980b9; 
        padding-left: 15px; 
        margin-top: 35px; 
        font-size: 16px; 
        background-color: #ecf0f1;
        padding-top: 8px;
        padding-bottom: 8px;
        border-radius: 0 4px 4px 0;
    }
    h4 { color: #555; margin-top: 20px; font-size: 14px; text-decoration: underline; }

    /* Caixas Especiais */
    .box-info { background-color: #e1f5fe; border: 1px solid #81d4fa; border-left: 5px solid #03a9f4; padding: 15px; margin: 15px 0; font-size: 13px; border-radius: 4px; }
    .box-ai { background-color: #f3e5f5; border: 1px solid #e1bee7; border-left: 5px solid #9c27b0; padding: 15px; margin: 15px 0; font-size: 13px; border-radius: 4px; }
    .box-security { background-color: #fff3e0; border: 1px solid #ffe0b2; border-left: 5px solid #ff9800; padding: 15px; margin: 15px 0; font-size: 13px; border-radius: 4px; }
    .box-cloud { background-color: #e8f5e9; border: 1px solid #c8e6c9; border-left: 5px solid #4caf50; padding: 15px; margin: 15px 0; font-size: 13px; border-radius: 4px; }

    /* Tabelas e Atalhos */
    table { width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    th { background-color: #34495e; border: 1px solid #34495e; padding: 12px; text-align: left; font-weight: bold; color: white; }
    td { border: 1px solid #bdc3c7; padding: 10px; }
    tr:nth-child(even) { background-color: #f9f9f9; }
    kbd { background-color: #f7f7f7; border-radius: 3px; border: 1px solid #ccc; padding: 2px 6px; font-family: monospace; font-weight: 700; color: #333; box-shadow: 0 2px 0 rgba(0,0,0,0.2); }

    /* Listas */
    ul { margin-left: 20px; }
    li { margin-bottom: 8px; }
</style>

<h1>MANUAL TÉCNICO DE OPERAÇÃO (MTO)</h1>
<p style='text-align: center; color: #7f8c8d; font-size: 12px;'>GC Gestor Enterprise v9.0 | Documentação Oficial</p>

<div class="box-info">
    <b>💡 Conceito Central: Ciclos Financeiros</b><br>
    O GC Gestor não trata o contrato como uma linha contínua infinita, mas como "gavetas" separadas chamadas <b>Ciclos Financeiros</b>. 
    <br>Isso garante que o saldo do Ano 1 não se misture indevidamente com o Ano 2, respeitando o princípio da anualidade orçamentária do setor público.
</div>

<h2>1. TRABALHO EM EQUIPE E NUVEM (GOOGLE DRIVE)</h2>
<p>O sistema possui um motor de sincronização "Enterprise" que permite que várias pessoas trabalhem em computadores diferentes. Acesse pelo menu <b>Ferramentas > Sincronizar com Google Drive</b>.</p>

<div class="box-cloud">
    <h3>Entendendo as 4 Opções de Sincronização</h3>
    
    <p><b>1. ⬇️⬆️ Sincronizar Tudo (Recomendado)</b></p>
    <ul>
        <li>Baixa novidades dos colegas e envia as suas. Resolve conflitos se houver.</li>
    </ul>

    <p><b>2. ⬆️ Apenas Subir Minhas Alterações</b></p>
    <ul>
        <li>Envia seu trabalho para a nuvem sem alterar nada na sua tela. Não apaga dados dos outros.</li>
    </ul>

    <p><b>3. ⬇️ Baixar Cópia da Nuvem (Salvar Como...)</b></p>
    <ul>
        <li><b>O que faz:</b> Baixa o arquivo da nuvem e salva numa pasta do seu computador.</li>
        <li><b>Para que serve:</b> Ideal para auditoria. Você pode baixar para ver o que tem na nuvem sem misturar com seus dados atuais. O sistema perguntará se você quer abrir esse arquivo imediatamente.</li>
    </ul>

    <p><b>4. ⚠️ Sobrescrever Nuvem (Reset)</b></p>
    <ul>
        <li>Apaga a nuvem e impõe a versão do seu computador. Use com cautela.</li>
    </ul>
</div>

<hr>

<h2>2. OPERAÇÃO DIÁRIA E FINANCEIRO</h2>

<h3>2.1 Cadastro com Validação</h3>
<p>Ao criar um contrato, selecione o prestador na lista. O sistema puxará automaticamente:</p>
<ul>
    <li>Razão Social e Nome Fantasia</li>
    <li>CNPJ (Formatado)</li>
    <li>CNES e Código CP</li>
</ul>
<p><i>Dica: Mantenha o cadastro de prestadores (Menu Cadastros) sempre atualizado.</i></p>

<h3>2.2 Execução Financeira (Empenhos e Pagamentos)</h3>
<p>Na aba <b>Financeiro</b> do contrato:</p>
<ul>
    <li><b>Emitir NE:</b> O sistema bloqueia se o valor for maior que o saldo do Serviço no ciclo atual.</li>
    <li><b>Realizar Pagamento:</b> Selecione a NE na tabela e clique em "Pagar". O sistema permite selecionar múltiplas competências (meses).</li>
    <li><b>Anular:</b> Estorna o valor para o saldo da NE.</li>
</ul>

<h3>2.3 Visão Detalhada (Tree View)</h3>
<p>Dê <b>duplo clique</b> em qualquer serviço na aba "Serviços" para abrir a auditoria profunda. Você verá:</p>
<ul>
    <li>Gráfico em tabela da evolução mensal.</li>
    <li>Árvore hierárquica expandível: <b>Serviço > Nota de Empenho > Pagamentos/Anulações</b>.</li>
    <li>Botão para copiar esses dados direto para o Excel.</li>
</ul>

<hr>

<h2>3. INTELIGÊNCIA ARTIFICIAL (IA)</h2>

<div class="box-ai">
    <b>O Assistente Virtual (Gemini 1.5 Flash)</b><br>
    O sistema "lê" seus dados e pode responder perguntas complexas.
</div>

<h3>Funcionalidades da IA:</h3>
<ul>
    <li><b>Botão [💬 IA] (Tela Inicial):</b> Chat livre. Pergunte "Qual contrato vence este mês?" ou "Resuma a situação da empresa X".</li>
    <li><b>Botão [Analisar Risco] (Financeiro):</b> A IA audita o contrato aberto e aponta tendências de déficit ou superávit.</li>
    <li><b>Análise de Alertas:</b> Na tela de notificações (Sininho 🔔), a IA pode gerar um plano de ação para resolver pendências críticas.</li>
</ul>

<hr>

<h2>4. SEGURANÇA E BACKUP</h2>

<h3>4.1 O Sistema "Undo" (Desfazer)</h3>
<div class="box-security">
    Se você excluir um contrato, empenho ou serviço por engano, não entre em pânico.
    <br>O sistema cria um <b>Ponto de Restauração</b> automático antes de qualquer exclusão crítica.
    <br><br>
    👉 Pressione <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>Z</kbd> ou vá no menu <b>Editar > Desfazer</b> para voltar no tempo.
</div>

<h3>4.2 Backup Manual</h3>
<p>Além da nuvem, você pode gerar um arquivo local <code>.bak</code> pelo menu <b>Arquivo > Fazer Backup de Segurança</b>.</p>

<hr>

<h2>5. GUIA DE CONFIGURAÇÃO (PRIMEIRO USO)</h2>

<h3>Passo 1: Ativar a IA (Google Gemini)</h3>
<ol>
    <li>Acesse: <b>aistudio.google.com/app/apikey</b></li>
    <li>Faça login com seu Gmail e clique em <b>"Create API Key"</b>.</li>
    <li>Copie o código gerado (começa com "AIza...").</li>
    <li>No sistema, crie um arquivo de texto chamado <b>chave_api.txt</b> na mesma pasta do executável.</li>
    <li>Cole o código dentro e salve.</li>
</ol>

<h3>Passo 2: Ativar a Nuvem (Google Drive)</h3>
<ol>
    <li>Solicite ao administrador o arquivo de credenciais da API do Google Drive.</li>
    <li>Renomeie esse arquivo obrigatoriamente para: <b>credentials.json</b></li>
    <li>Coloque-o na pasta do sistema (junto com o executável).</li>
    <li>Na primeira vez que clicar em Sincronizar, uma janela do navegador abrirá pedindo permissão.</li>
</ol>

<p style='text-align: right; font-size: 10px; color: #999; margin-top: 50px;'>GC Gestor Enterprise - Desenvolvido por Cássio de Souza Lopes.</p>
"""