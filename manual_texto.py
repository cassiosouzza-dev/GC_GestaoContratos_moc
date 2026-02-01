HTML_MANUAL = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Manual Técnico - GC Gestor 2.0</title>
<style>
    /* --- ESTILO GERAL DO DOCUMENTO --- */
    body { 
        font-family: 'Segoe UI', 'Roboto', Helvetica, Arial, sans-serif; 
        line-height: 1.6; 
        color: #333; 
        max-width: 1000px; 
        margin: 0 auto; 
        padding: 40px; 
        background-color: #ffffff; 
    }

    /* --- CABEÇALHOS --- */
    h1 { 
        color: #2c3e50; 
        border-bottom: 3px solid #27ae60; 
        padding-bottom: 10px; 
        margin-top: 60px; 
        font-size: 32px; 
        letter-spacing: -0.5px;
    }
    h2 { 
        color: #2980b9; 
        margin-top: 40px; 
        font-size: 24px; 
        border-left: 6px solid #2980b9; 
        padding-left: 15px; 
        background: linear-gradient(to right, #f4f8fb, #fff);
        padding-top: 5px;
        padding-bottom: 5px;
    }
    h3 { 
        color: #555; 
        margin-top: 30px; 
        font-weight: bold; 
        font-size: 18px; 
    }

    /* --- CAIXAS DE DESTAQUE --- */
    .box-concept { 
        background-color: #eaf2f8; 
        border: 1px solid #aed6f1; 
        padding: 20px; 
        border-radius: 6px; 
        margin: 20px 0; 
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05); 
    }
    .box-tech { 
        background-color: #f8f9fa; 
        border-left: 5px solid #34495e; 
        padding: 15px 20px; 
        font-family: 'Consolas', 'Monaco', monospace; 
        font-size: 0.9em; 
        color: #444; 
        margin: 15px 0; 
    }
    .box-alert { 
        background-color: #fff3cd; 
        border-left: 5px solid #f39c12; 
        padding: 15px; 
        color: #856404; 
        margin: 20px 0;
    }
    .box-success {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 15px;
        color: #155724;
    }

    /* --- TABELAS --- */
    table { 
        width: 100%; 
        border-collapse: collapse; 
        margin: 25px 0; 
        font-size: 14px; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    th, td { 
        border: 1px solid #ddd; 
        padding: 12px; 
        text-align: left; 
    }
    th { 
        background-color: #2c3e50; 
        color: white; 
        text-transform: uppercase;
        font-size: 12px;
    }
    tr:nth-child(even) { background-color: #f8f9fa; }
    tr:hover { background-color: #f1f1f1; }

    /* --- LISTAS --- */
    ul { list-style-type: disc; margin-left: 20px; color: #444; }
    ol { margin-left: 20px; color: #444; }
    li { margin-bottom: 8px; }
    
    /* --- ELEMENTOS DE TEXTO --- */
    strong { color: #c0392b; font-weight: 700; }
    code { 
        background-color: #eee; 
        padding: 2px 5px; 
        border-radius: 3px; 
        font-family: monospace; 
        color: #c7254e;
    }
    .highlight { 
        background-color: #fff3cd; 
        padding: 2px 6px; 
        border-radius: 3px; 
        border: 1px solid #ffeeba; 
    }
    
    /* --- CAPA E RODAPÉ --- */
    .cover { 
        text-align: center; 
        margin-bottom: 80px; 
        padding: 60px; 
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); 
        color: white; 
        border-radius: 12px; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    .cover h1 { border: none; color: white; margin: 0; font-size: 42px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .cover p { font-size: 20px; opacity: 0.9; margin-top: 10px; }
    .footer { 
        text-align: center; 
        font-size: 12px; 
        color: #999; 
        margin-top: 100px; 
        border-top: 1px solid #eee; 
        padding-top: 30px; 
    }
    
    /* --- ÍCONES --- */
    .icon { font-family: 'Segoe UI Emoji', sans-serif; font-size: 1.3em; margin-right: 8px; vertical-align: middle; }
    
</style>
</head>
<body>

    <div class="cover">
        <h1>GC GESTOR DE CONTRATOS</h1>
        <p>Manual Técnico Operacional v2.0</p>
        <p style="font-size: 16px; margin-top: 20px;">Edição Enterprise - SQLite Integration</p>
        <br>
        <small>Secretaria Municipal de Saúde - Montes Claros/MG</small>
    </div>

    <div style="background-color: #fff; border: 1px solid #ddd; padding: 20px; border-radius: 5px;">
        <h3>Índice do Documento</h3>
        <ol>
            <li>Introdução e Mudanças na Versão 2.0</li>
            <li>Arquitetura de Dados (O Motor do Sistema)</li>
            <li>Instalação e Requisitos de Ambiente</li>
            <li>Fluxo de Trabalho: Gestão Contratual</li>
            <li>Gestão Financeira e Execução</li>
            <li>Gestão de Aditivos (Prazos e Valores)</li>
            <li>Monitoramento de Vigências (Semáforo)</li>
            <li>Ferramentas de Auditoria e Segurança</li>
            <li>Conectividade (Nuvem e Inteligência Artificial)</li>
            <li>Guia de Referência da Interface (Botões e Menus)</li>
            <li>Solução de Problemas (Troubleshooting)</li>
        </ol>
    </div>

    <h1>1. Introdução e Mudanças na Versão 2.0</h1>
    <p>
        O <strong>GC Gestor de Contratos</strong> é uma solução de software <em>Standalone</em> (desktop) desenvolvida para orquestrar o ciclo de vida completo de contratos públicos. O sistema transcende o simples registo de dados, oferecendo ferramentas analíticas, validações financeiras em tempo real e auditoria forense das ações dos usuários.
    </p>

    <div class="box-success">
        <h3>🚀 O que há de novo na Versão 2.0?</h3>
        <ul>
            <li><strong>Novo Motor de Dados:</strong> Migração completa de arquivos de texto plano para <strong>SQLite</strong>. Isso garante integridade transacional, maior velocidade e segurança contra corrupção de dados.</li>
            <li><strong>Pesquisa Inteligente:</strong> O campo de "Prestador" no cadastro agora possui <em>Autocomplete</em>. Basta digitar parte do nome fantasia para localizar a empresa.</li>
            <li><strong>Gestão em Massa:</strong> Capacidade de selecionar múltiplos contratos (Ctrl+Click) na tela inicial para <strong>Arquivar</strong> ou <strong>Excluir</strong> em lote pelo menu de contexto.</li>
            <li><strong>Monitor de Vigência 2.0:</strong> Novo visual com código de cores estratégico (Roxo para Vencidos, Vermelho para Críticos).</li>
            <li><strong>Interface Otimizada:</strong> Barra de ferramentas compacta, sem rótulos de texto, maximizando a área de trabalho para tabelas.</li>
            <li><strong>Árvore Financeira (Tree View):</strong> Nova visualização hierárquica na aba de detalhamento, permitindo rastrear cada centavo desde a NE original até os pagamentos e anulações.</li>
        </ul>
    </div>

    <h1>2. Arquitetura de Dados (O Motor do Sistema)</h1>
    <p>
        Para administradores e técnicos de TI, é crucial entender como o GC Gestor 2.0 armazena informações. O sistema utiliza uma arquitetura híbrida <strong>Relacional + Documental</strong>.
    </p>

    <h3>O Arquivo `dados_sistema.db`</h3>
    <p>
        Todo o sistema reside num único arquivo físico SQLite. No entanto, internamente, ele estrutura-se da seguinte forma:
    </p>
    <ul>
        <li><strong>Tabela `contratos`:</strong> Armazena o ID e uma coluna `dados_json` que contém a árvore completa do objeto Contrato (Serviços, Ciclos, NEs, Histórico).</li>
        <li><strong>Tabela `prestadores`:</strong> Cadastro de credores com CNPJ (chave única) e dados bancários/fiscais.</li>
        <li><strong>Tabela `logs`:</strong> Registro imutável de auditoria.</li>
        <li><strong>Tabela `usuarios`:</strong> Credenciais e hashes de senha.</li>
    </ul>

    <div class="box-tech">
        <strong>Vantagem Técnica:</strong> Esta abordagem permite que a estrutura interna do contrato (ex: adicionar um novo campo num aditivo) evolua via código Python sem necessidade de comandos SQL `ALTER TABLE` complexos, mantendo a robustez do banco relacional para backup e integridade.
    </div>

    <h1>3. Instalação e Requisitos de Ambiente</h1>
    
    <h3>Arquivos Essenciais</h3>
    <p>Para o funcionamento pleno, a pasta do executável (<code>.exe</code>) deve conter:</p>
    <ul>
        <li><code>dados_sistema.db</code>: O banco de dados (criado automaticamente se não existir).</li>
        <li><code>config.json</code>: Guarda preferências do usuário (tema, tamanho da fonte).</li>
        <li><code>chave_api.txt</code>: (Opcional) Contém a chave da Google Gemini para recursos de IA.</li>
        <li><code>credentials.json</code>: (Opcional) Credencial de serviço para sincronização com Google Drive.</li>
    </ul>

    <h1>4. Fluxo de Trabalho: Gestão Contratual</h1>

    <h2>4.1. Cadastro de Prestadores (Pré-requisito)</h2>
    <p>Antes de criar um contrato, a empresa deve existir na base. Vá em <strong>Gestão &gt; Prestadores</strong>.</p>
    <ul>
        <li><strong>CNPJ Único:</strong> O sistema não permite dois prestadores com o mesmo CNPJ.</li>
        <li><strong>CNES/Cód CP:</strong> Campos importantes para integração com sistemas de saúde, agora exibidos como "Badges" na tela de detalhes do contrato.</li>
    </ul>

    <h2>4.2. Cadastro do Instrumento Contratual</h2>
    <p>No menu <strong>Novo Contrato</strong>, o sistema valida a consistência dos dados:</p>
    <ul>
        <li><strong>Busca de Prestador:</strong> O campo agora é uma caixa de combinação editável. Digite "Lab" para filtrar todos os laboratórios. Ao selecionar, o sistema vincula internamente o CNPJ.</li>
        <li><strong>Ciclo 0 (Inicial):</strong> O valor inserido no cadastro cria automaticamente o primeiro ciclo financeiro.</li>
        <li><strong>Vigência e Competências:</strong> Definem o período de validade. O campo "Competências" (ex: 01/2024) é vital para o cálculo de médias mensais.</li>
    </ul>

    <h2>4.3. Estrutura de Serviços (O "Objeto" Real)</h2>
    <p>Um contrato é apenas um papel. O que gera despesa são os <strong>Serviços</strong>. Na aba "Serviços", você deve cadastrar os itens (Ex: "Locação de Veículo", "Hora Médica").</p>
    <div class="box-alert">
        <strong>Regra de Ouro:</strong> A soma dos orçamentos dos serviços não deve exceder o valor total do ciclo do contrato. O sistema permite o cadastro (para flexibilidade), mas gerará alertas de inconsistência no painel de auditoria.
    </div>

    <h1>5. Gestão Financeira e Execução</h1>

    <h2>5.1. O Conceito de Ciclos Financeiros</h2>
    <p>
        O GC Gestor não mistura orçamentos de anos diferentes. Cada contrato é fatiado em <strong>Ciclos</strong>.
        <br><em>Exemplo:</em> O "Ciclo 2024" tem R$ 100.000,00. O "Ciclo 2025" (criado por aditivo) tem outros R$ 120.000,00.
        <br>Ao emitir uma Nota de Empenho (NE), você deve obrigatoriamente informar a qual ciclo ela pertence através do menu suspenso na tela de detalhes.
    </p>

    <h2>5.2. Nota de Empenho e Liquidação</h2>
    <p>O fluxo financeiro segue a lógica pública:</p>
    <ol>
        <li><strong>Empenho (+):</strong> Reserva o dinheiro do saldo do serviço.</li>
        <li><strong>Liquidação/Pagamento (-):</strong> Baixa o saldo da NE. O sistema permite parciais.</li>
        <li><strong>Anulação (Estorno):</strong> Devolve o saldo da NE para o "bolo" do serviço, permitindo reempenho.</li>
    </ol>

    <div class="box-concept">
        <h3>Rateio Automático</h3>
        <p>Se você tem um pagamento único de R$ 50.000,00 que deve cobrir 5 notas de empenho diferentes do mesmo prestador, use a ferramenta <strong>Rateio</strong>. O sistema distribuirá o valor automaticamente, liquidando as notas mais antigas primeiro.</p>
    </div>

    <h2>5.3. Bloqueio Administrativo (Cadeado)</h2>
    <p>
        O ícone de cadeado (🔒) serve para encerrar uma NE que ficou com saldo residual (ex: R$ 0,10) que não será mais usado. Isso remove o valor do "Saldo Disponível" do serviço, limpando os relatórios.
    </p>

    <h1>6. Gestão de Aditivos (Prazos e Valores)</h1>
    
    <h3>Aditivo de Valor</h3>
    <p>Altera o teto financeiro do <strong>ciclo atual</strong>. Pode ser acréscimo (+) ou supressão (-). O saldo é imediatamente atualizado na tela principal.</p>

    <h3>Aditivo de Prazo (Prorrogação)</h3>
    <p>Estende a data final. Se a opção <strong>"Haverá Renovação de Valor?"</strong> for marcada, o sistema cria um <strong>NOVO CICLO</strong>. As NEs antigas ficam no ciclo anterior, e o contrato ganha um "saldo virgem" para o novo período.</p>

    <h1>7. Monitoramento de Vigências (Semáforo)</h1>
    <p>O sistema classifica os contratos por cores baseadas na urgência de ação. A lógica da versão 2.0 separa "o que já passou" do que "precisa de ação urgente".</p>
    
    <table>
        <tr>
            <th width="150px">Status / Cor</th>
            <th>Significado e Ação Recomendada</th>
        </tr>
        <tr>
            <td style="color:#8e44ad; font-weight:bold;">🟣 ROXO<br>(Vencido)</td>
            <td>Contrato já expirado. É um passivo (não há mais o que fazer em termos de alerta). <strong>Ação: Arquivar para histórico.</strong></td>
        </tr>
        <tr>
            <td style="color:#c0392b; font-weight:bold;">🔴 VERMELHO<br>(Crítico)</td>
            <td>Vence em <strong>menos de 90 dias</strong>. Risco iminente de descontinuidade. <strong>Ação: Renovar Imediatamente.</strong></td>
        </tr>
        <tr>
            <td style="color:#f39c12; font-weight:bold;">🟠 AMARELO<br>(Atenção)</td>
            <td>Vence entre 90 e 180 dias. Entrou na janela de planejamento.</td>
        </tr>
        <tr>
            <td style="color:#27ae60; font-weight:bold;">🟢 VERDE<br>(Vigente)</td>
            <td>Mais de 6 meses de vigência. Situação confortável.</td>
        </tr>
    </table>

    <h1>8. Ferramentas de Auditoria e Segurança</h1>

    <h2>8.1. Arquivamento e Lixeira</h2>
    <ul>
        <li><strong>Lixeira (Soft Delete):</strong> Ao excluir um contrato, ele vai para a Lixeira. Só lá ele pode ser apagado definitivamente ou restaurado.</li>
        <li><strong>Arquivo Morto (Cumulativo):</strong> Contratos antigos (Roxos) devem ser movidos para o Banco Histórico (Menu Ferramentas > Arquivar Antigos). O sistema move os dados para <code>arquivo_historico.db</code> sem apagar os que já estavam lá.</li>
    </ul>

    <h2>8.2. Backup Local Instantâneo</h2>
    <p>
        O botão <strong>Backup Local</strong> na barra de ferramentas cria instantaneamente um arquivo `.bak` com a data e hora (ex: `dados_sistema_20241020_1400.bak`). Use isso sempre antes de fazer importações em massa ou limpezas grandes.
    </p>

    <h1>9. Conectividade (Nuvem e IA)</h1>
    
    <div class="box-tech">
        <strong>Integração IA Gemini:</strong> O sistema envia os dados do contrato (sem dados sigilosos do paciente, apenas financeiros) para a IA da Google, que retorna uma análise de risco financeiro, apontando tendências de gastos anormais.
    </div>
    
    <div class="box-tech">
        <strong>Google Drive Sync:</strong> O sistema compara a data de modificação do seu arquivo local com o da nuvem.
        <ul>
            <li>Se a nuvem for mais recente: Ele baixa e atualiza.</li>
            <li>Se o local for mais recente: Ele sobe e atualiza a nuvem.</li>
            <li>Se houver conflito: O sistema abre o "Gerenciador de Conflitos" para você decidir linha por linha.</li>
        </ul>
    </div>

    <h1>10. Guia de Referência da Interface</h1>
    <p>Abaixo, a descrição detalhada da nova Barra de Ferramentas v2.0.</p>

    <table>
        <tr>
            <th>Ícone</th>
            <th>Nome</th>
            <th>Função</th>
        </tr>
        <tr>
            <td>⬅️</td>
            <td><strong>Início</strong></td>
            <td>Fecha o contrato atual e volta para a tela de pesquisa/listagem.</td>
        </tr>
        
        <tr><td colspan="3" style="background-color:#eee;"><em>Grupo: Arquivo</em></td></tr>

        <tr>
            <td>📄</td>
            <td><strong>Novo Contrato</strong></td>
            <td>Abre a ficha de cadastro em branco.</td>
        </tr>
        <tr>
            <td>💾</td>
            <td><strong>Salvar Tudo</strong></td>
            <td>Força a gravação em disco (o sistema já salva automático ao fechar telas, mas este botão garante).</td>
        </tr>
        <tr>
            <td>💽</td>
            <td><strong>Backup Local</strong></td>
            <td>Gera um arquivo de segurança `.bak` na pasta do sistema.</td>
        </tr>

        <tr><td colspan="3" style="background-color:#eee;"><em>Grupo: Gestão</em></td></tr>

        <tr>
            <td>🏠</td>
            <td><strong>Prestadores</strong></td>
            <td>Abre o cadastro de empresas (CNPJ, Endereço, Telefones).</td>
        </tr>
        <tr>
            <td>📅</td>
            <td><strong>Prazos</strong></td>
            <td>Abre o painel de Monitoramento de Vigências (Semáforo).</td>
        </tr>

        <tr><td colspan="3" style="background-color:#eee;"><em>Grupo: Conectividade</em></td></tr>

        <tr>
            <td>🔄</td>
            <td><strong>Sincronizar</strong></td>
            <td>Conecta à Nuvem para Upload/Download de dados.</td>
        </tr>
        <tr>
            <td>🤖</td>
            <td><strong>IA Gemini</strong></td>
            <td>Abre o chat inteligente para perguntas livres sobre os dados.</td>
        </tr>

        <tr><td colspan="3" style="background-color:#eee;"><em>Grupo: Ferramentas</em></td></tr>

        <tr>
            <td>ℹ️</td>
            <td><strong>Calculadora</strong></td>
            <td>Abre a calculadora do Windows.</td>
        </tr>
        <tr>
            <td>🗑️</td>
            <td><strong>Lixeira</strong></td>
            <td>Acessa os itens excluídos temporariamente.</td>
        </tr>
        
        <tr><td colspan="3" style="background-color:#eee;"><em>Notificações</em></td></tr>
        
        <tr>
            <td>🔔</td>
            <td><strong>Sino</strong></td>
            <td>Central de Alertas. Exibe lista de contratos vencidos ou com estouro orçamentário.</td>
        </tr>
    </table>

    <h1>11. Solução de Problemas (Troubleshooting)</h1>

    <h3>Erro: "Database is locked"</h3>
    <p><strong>Causa:</strong> Duas instâncias do programa abertas ou o Google Drive/Dropbox está sincronizando o arquivo `.db` enquanto você tenta salvar.<br>
    <strong>Solução:</strong> Feche outras janelas e pause a sincronização externa momentaneamente.</p>

    <h3>Erro: Seta "Voltar" ou Ícones não aparecem</h3>
    <p><strong>Causa:</strong> Estilo visual do Windows ou falta de biblioteca de ícones.<br>
    <strong>Solução:</strong> O sistema usa ícones nativos (`SP_ArrowBack`). Se não aparecer, verifique se o Windows está com tema de alto contraste.</p>

    <h3>Aviso: "Prestador não encontrado na lista"</h3>
    <p><strong>Causa:</strong> Você digitou um nome na criação de contrato que não existe no cadastro de prestadores.<br>
    <strong>Solução:</strong> Vá em "Gestão > Prestadores", cadastre a empresa primeiro e tente novamente. Isso garante a integridade dos dados.</p>

    <hr>
    <p class="footer">
        <em>Manual Técnico - GC Gestor de Contratos v2.0 - Edição Enterprise<br>
        Desenvolvido para a Secretaria Municipal de Saúde de Montes Claros (MG)</em>
    </p>

</body>
</html>
"""