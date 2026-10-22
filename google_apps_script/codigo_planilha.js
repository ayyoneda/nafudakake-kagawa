/**
 * =========================================================================
 * NAFUDAKAKE DIGITAL - ASSOCIAÇÃO KAGAWA DE KENDO (洗心香武館)
 * Integração Google Sheets -> GitHub Actions -> Datastudio
 * =========================================================================
 * 
 * Instruções de Instalação:
 * 1. Na planilha do Google Sheets, clique no menu: Extensões > Apps Script.
 * 2. Cole este código no editor (substituindo o código existente).
 * 3. Clique no ícone de Disquete (Salvar) ou Ctrl + S.
 * 4. Recarregue a planilha (F5). O menu "🥋 Nafudakake" aparecerá no topo!
 */

var GITHUB_REPO_OWNER = "ayyoneda";
var GITHUB_REPO_NAME = "nafudakake-kagawa";

/**
 * Cria o menu personalizado quando a planilha é aberta.
 */
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('🥋 Nafudakake')
    .addItem('🔄 Atualizar Painel no Datastudio', 'atualizarNafudakake')
    .addSeparator()
    .addItem('⚙️ Configurar / Trocar Token do GitHub', 'configurarTokenGitHub')
    .addToUi();
}

/**
 * Dispara a atualização do Nafudakake via GitHub Actions.
 */
function atualizarNafudakake() {
  var ui = SpreadsheetApp.getUi();
  var props = PropertiesService.getScriptProperties();
  var token = props.getProperty('GITHUB_TOKEN');

  // Se o token ainda não estiver configurado, solicita ao usuário
  if (!token) {
    var promptRes = ui.prompt(
      'Configuração Inicial - Token do GitHub',
      'Para permitir que a planilha envie o comando de atualização para o GitHub, insira seu GitHub Personal Access Token (PAT):\n\n' +
      '(Dica: crie em github.com/settings/tokens com permissão de "repo" ou fine-grained "Contents: Read & Write")',
      ui.ButtonSet.OK_CANCEL
    );

    if (promptRes.getSelectedButton() == ui.Button.OK) {
      token = promptRes.getResponseText().trim();
      if (!token) {
        ui.alert('Aviso', 'Token não fornecido. A atualização foi cancelada.', ui.ButtonSet.OK);
        return;
      }
      props.setProperty('GITHUB_TOKEN', token);
    } else {
      return;
    }
  }

  // Notificação inicial na planilha
  SpreadsheetApp.getActiveSpreadsheet().toast(
    'Conectando ao GitHub para compilar o Nafudakake...',
    '🥋 Atualização Iniciada',
    5
  );

  var url = 'https://api.github.com/repos/' + GITHUB_REPO_OWNER + '/' + GITHUB_REPO_NAME + '/dispatches';
  var payload = JSON.stringify({
    event_type: 'update_nafudakake'
  });

  var options = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'Authorization': 'Bearer ' + token,
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'Google-Apps-Script-Nafudakake'
    },
    payload: payload,
    muteHttpExceptions: true
  };

  try {
    var response = UrlFetchApp.fetch(url, options);
    var statusCode = response.getResponseCode();

    // 204 No Content é o retorno padrão de sucesso do GitHub para 'repository_dispatch'
    if (statusCode === 204) {
      ui.alert(
        '✅ Atualização Disparada com Sucesso!',
        'O robô do GitHub Actions iniciou o processamento das graduações.\n\n' +
        'Ele irá ler a aba Kenshis, recalcular as posições da direita para a esquerda e gerar os novos arquivos.\n\n' +
        '⏳ Em cerca de 1 a 2 minutos o Looker Studio / Datastudio refletirá as novas plaquetas automaticamente!',
        ui.ButtonSet.OK
      );
    } else if (statusCode === 401 || statusCode === 403) {
      props.deleteProperty('GITHUB_TOKEN');
      ui.alert(
        'Erro de Autenticação (Código ' + statusCode + ')',
        'O Token do GitHub informado é inválido ou não possui permissão de gravação no repositório.\n\n' +
        'O token antigo foi removido. Clique novamente no menu "🥋 Nafudakake > ⚙️ Configurar / Trocar Token do GitHub" para inserir um token válido.',
        ui.ButtonSet.OK
      );
    } else {
      ui.alert(
        'Aviso do GitHub (Código ' + statusCode + ')',
        'Resposta do GitHub:\n' + response.getContentText(),
        ui.ButtonSet.OK
      );
    }
  } catch (err) {
    ui.alert(
      'Falha na Conexão',
      'Não foi possível contatar o GitHub:\n' + err.toString(),
      ui.ButtonSet.OK
    );
  }
}

/**
 * Função para configurar ou alterar o token do GitHub.
 */
function configurarTokenGitHub() {
  var ui = SpreadsheetApp.getUi();
  var props = PropertiesService.getScriptProperties();
  var atual = props.getProperty('GITHUB_TOKEN') ? '******** (já configurado)' : 'Nenhum';

  var promptRes = ui.prompt(
    'Configurar Token do GitHub',
    'Token atual: ' + atual + '\n\n' +
    'Insira o novo GitHub Personal Access Token (com permissão de repositório):',
    ui.ButtonSet.OK_CANCEL
  );

  if (promptRes.getSelectedButton() == ui.Button.OK) {
    var novoToken = promptRes.getResponseText().trim();
    if (novoToken) {
      props.setProperty('GITHUB_TOKEN', novoToken);
      ui.alert('Sucesso', 'Token do GitHub salvo com segurança na planilha!', ui.ButtonSet.OK);
    }
  }
}
