# Contexto e Manual de Operação: Gerador do Nafudakake Digital (洗心香武館)

Este documento descreve a arquitetura, regras de negócio tradicionais do Kendo, instruções de uso e operação da ferramenta do **Nafudakake (名札掛け)** da **Associação Kagawa de Kendo (洗心香武館)**.

---

## 1. Visão Geral do Sistema

O Nafudakake Digital é uma plataforma híbrida composta por:
1. **Motor de Renderização Vetorial e Raster (Python):**
   * Processamento e classificação hierárquica oficial de Kendo (de `八段` a `無段`).
   * Desacoplamento de Shogo (`範士`, `教士`, `錬士`) para qualquer Dan onde atribuído.
   * Geração de arte vetorial SVG fotorrealista (Madeira Hinoki, Cedro, moldura entalhada, iluminação 3D e fonte caligráfica *Epson Gyosho Bold* embutida via Base64).
   * Exportação de imagens raster em altíssima definição (PNG 300 DPI / 4K / Ultra-HD) via PySide6.
2. **Aplicação Web Interativa (HTML5 / Modern CSS / Vanilla JS):**
   * Visualização com zoom e pan suave acelerado por GPU.
   * Localizador de kenshis em tempo real com spotlight dourado na plaqueta.
   * Navegação e salto rápido por graduação (filtros por Dan).
   * Ajustes visuais dinâmicos (plaquetas por trilho, visibilidade de romaji).
   * Ações com 1 clique para Sincronização, Download de SVG/PNG e Publicação no Google Drive.
3. **Módulo de Integração com Google Cloud (Sheets & Drive):**
   * Leitura oficial da planilha mestre de atletas via Google Sheets API (ou fallback gracioso para CSV local).
   * Upload e atualização automática dos arquivos SVG e PNG na pasta designada do Google Drive (`1gbzJWLZWGbTqYXSX419Lsuzbe6TTASC_`) para alimentação direta de dashboards no Looker Studio.

---

## 2. Estrutura dos Arquivos no Repositório

* **`server.py`**: Servidor local Flask com API REST (`http://localhost:5050`) conectando a interface gráfica ao motor de geração.
* **`Nafudakake.py`**: Motor principal de renderização vetorial, tipografia vertical e conversão PNG.
* **`google_sync.py`**: Módulo de autenticação segura e sincronização com Google Sheets e Google Drive.
* **`index.html`**, **`style.css`**, **`app.js`**: Frontend do Web App interativo.
* **`epgyobld.ttf`**: Fonte tipográfica oficial (*Epson Gyosho Bold* / 行書体).
* **`Cadastro - Atletas Kagawa (respostas) - Nafudakake.csv`**: Base local de dados para fallback offline.
* **`credentials.example.json`** e **`.env.example`**: Modelos seguros para configuração de credenciais.
* **`Nafudakake_Realista.svg`** e **`Nafudakake_Realista.png`**: Artefatos finais de altíssima definição gerados pelo sistema.

---

## 3. Como Executar

### Modo 1: Aplicação Web Interativa (Recomendado)

Inicie o servidor local:
```powershell
python server.py
```
Abra seu navegador em:
👉 **`http://localhost:5050`**

Recursos disponíveis na interface web:
* **Pan & Zoom:** Arraste com o mouse para navegar; use a roda do scroll para aproximar/afastar.
* **Buscar Atleta:** Digite no campo "Localizar Kenshi" (em romaji, kanji ou katakana) para a câmera focar e destacar a plaqueta.
* **Saltar por Graduação:** Clique nos botões `七段`, `五段`, `四段`, `三段`, `二段`, `初段`, `一級` ou `無段`.
* **Sincronizar:** Clique no botão `Sincronizar Planilha` para recarregar dados novos.
* **Exportar:** Baixe o arquivo SVG vetorial ou a imagem PNG Ultra-HD pronta para impressão ou uso digital.
* **Publicar no Drive:** Envia os arquivos gerados diretamente para a pasta do Google Drive da Kagawa.

---

### Modo 2: Linha de Comando (CLI / Automação em Lote)

Para gerar diretamente os arquivos `Nafudakake_Realista.svg` e `Nafudakake_Realista.png` sem abrir o navegador:
```powershell
python Nafudakake.py
```

---

## 4. Configuração do Google Cloud (Service Account)

Para habilitar a leitura online automática da planilha protegida e o upload direto no Google Drive:

1. No Google Cloud Console, crie uma **Service Account** com permissões para **Google Sheets API** e **Google Drive API**.
2. Baixe a chave no formato JSON e salve na raiz do projeto com o nome:
   `credentials.json`
3. Compartilhe a **Planilha** (`1EvY8vbAkRkP6fO65baB5J5v71cpk74RU8KMEw57p0SA`) e a **Pasta do Google Drive** (`1gbzJWLZWGbTqYXSX419Lsuzbe6TTASC_`) com o e-mail da Service Account (com permissão de *Editor*).
4. O arquivo `credentials.json` já está incluído no `.gitignore` para proteção absoluta contra vazamentos acidentais.

*(Nota: Na ausência do arquivo `credentials.json`, o sistema entra automaticamente em modo de contingência, utilizando o arquivo CSV local com total funcionalidade).*

---

## 5. Regras Tradicionais de Kendo Aplicadas

1. **Placa Superior do Dojo (*Gaku / 額*):** Cabeçalho esculpido em madeira nobre com a caligrafia oficial:
   * Kanji: **洗心香武館**
   * Subtítulo: **ASSOCIAÇÃO KAGAWA DE KENDO**
2. **Plaquetas de Cabeçalho de Dan:**
   * Distinção visual nobre para as categorias: `八段`, `七段`, `六段`, `五段`, `四段`, `三段`, `二段`, `初段`, `一級`, `無段`.
3. **Mestres e Shogo (*称号*):**
   * Insígnia tradicional no topo da plaqueta (`範士`, `教士`, `錬士`) em carmim profundo sobre fundo claro.
   * Suporte desacoplado de grau (atribuível a 8º, 7º, 6º ou 5º Dan conforme histórico).
4. **Tipografia e Caligrafia Vertical:**
   * Textos japoneses alinhados no sentido vertical tradicional, com conversão automática do traço longo de Katakana (*chōonpu*) para a forma vertical (`︱`).
   * Algoritmo de dimensionamento dinâmico que impede matematicamente que nomes longos em Katakana colidam com o nome em alfabeto romano.