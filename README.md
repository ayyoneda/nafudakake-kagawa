# Nafudakake Digital (名札掛け) — 洗心香武館 (Senshin Kabukan)
### Associação Kagawa de Kendo | Kendo & Iaido

Painel digital interativo e gerador vetorial de alta definição para o **Nafudakake tradicional do dojo**, com caligrafia clássica japonesa *Gyosho* vetorizada em curvas puras, texturas orgânicas de madeira Hinoki maciça, diagramação tradicional da direita para a esquerda (*Migi-Keitai*) e integração com Google Sheets, Google Looker Studio e GitHub Pages.

---

## Sumário
1. [Visão Geral e Propósito](#visão-geral-e-propósito)
2. [Estrutura e Organização de Pastas](#estrutura-e-organização-de-pastas)
3. [Regras Marciais e Critérios de Ordenação](#regras-marciais-e-critérios-de-ordenação)
4. [Guia de Operação e Uso no Dia a Dia](#guia-de-operação-e-uso-no-dia-a-dia)
   - [Como Atualizar o Nafudakake após Exames de Graduação](#como-atualizar-o-nafudakake-após-exames-de-graduação)
   - [Como Publicar e Refletir no Looker Studio / Datastudio](#como-publicar-e-refletir-no-looker-studio--datastudio)
   - [Como Usar a Interface Local (localhost:5050)](#como-usar-a-interface-local-localhost5050)
5. [Arquitetura Técnica e Fluxo de Dados](#arquitetura-técnica-e-fluxo-de-dados)
6. [Configuração de Credenciais e Contingência Offline](#configuração-de-credenciais-e-contingência-offline)
7. [Licença e Créditos](#licença-e-créditos)

---

## Visão Geral e Propósito

Nas artes marciais tradicionais japonesas (*Budo*), o **Nafudakake** (名札掛け) é o painel de madeira exposto na parede de honra (*Kamiza*) do dojo contendo as plaquetas individuais (*Nafuda*) de todos os praticantes (*Kenshis*), organizadas estritamente de acordo com a hierarquia marcial.

Este projeto digitaliza o Nafudakake da **Associação Kagawa de Kendo**, permitindo:
- **Visualização interativa na web**: zoom fluído por GPU, navegação livre por arrasto (*pan*), busca instantânea e barra retrátil para máximo aproveitamento de tela.
- **Fidelidade à Tradição Japonesa**:
  - **Orientação Direita para a Esquerda (*Migi-Keitai*)**: o trilho superior inicia à direita com a graduação mais alta (7º Dan no Kendo / 5º Dan no Iaido) e flui para a esquerda; trilhos seguintes seguem a mesma regra.
  - **Curvas Vetoriais Puras (`<path>`)**: todos os ideogramas japoneses (*Kanji*) e nomes ocidentais são convertidos em geometria vetorial pura a partir da fonte tipográfica *Epson Gyosho Bold*. Não depende de fontes instaladas no cliente (zero risco de caracteres em branco ou *tofu*).
  - **Madeira Hinoki Realista Contínua**: veios contínuos de cipreste japonês sem emendas ou cortes artificiais.
- **Multi-Modalidade Nativa**: alternância com 1 clique entre **劍道 Kendo** e **居合道 Iaido** (já preparado para **杖道 Jodo**).
- **Sem Dependência de Servidores Pagos**: funciona 100% de forma estática no **GitHub Pages**, permitindo incorporação direta via HTTPS no **Google Looker Studio**.

---

## Estrutura e Organização de Pastas

A pasta do projeto é dividida por responsabilidades claras para facilitar manutenção futura:

```text
Nafudakake/
│
├── 🌐 [PÁGINA PÚBLICA / GITHUB PAGES] (Permanecem na raiz para o Datastudio)
│   ├── index.html              # Aplicação web frontend (HTML5 semântico)
│   ├── style.css               # Estilos visuais japoneses, tema escuro e modo embed
│   ├── app.js                  # Lógica interativa (pan/zoom, busca, filtros de Dan, drawer)
│   ├── AKK_colorido.png        # Brasão oficial da Associação Kagawa de Kendo
│   ├── Nafudakake_Kendo.svg    # Quadro vetorial oficial de Kendo (acessado pelo site)
│   ├── Nafudakake_Iaido.svg    # Quadro vetorial oficial de Iaido (acessado pelo site)
│   ├── cache_kendo.json        # Base de dados JSON de Kendo para navegação web
│   └── cache_iaido.json        # Base de dados JSON de Iaido para navegação web
│
├── ⚡ [ATALHOS RÁPIDOS PARA WINDOWS]
│   ├── atualizar_nafudakake.bat # Duplo-clique para reprocessar planilha e gerar arquivos
│   └── iniciar_servidor.bat    # Duplo-clique para rodar servidor local (localhost:5050)
│
├── 📂 src/                     # Código-fonte Python (Lógica de processamento e APIs)
│   ├── Nafudakake.py           # Motor gráfico de montagem e vetorização tipográfica
│   ├── google_sync.py          # Leitor da aba mestre 'Kenshis' e regras hierárquicas
│   ├── process_wood_textures.py # Extrator e gerador de texturas de Hinoki maciço
│   └── server.py               # Servidor local Flask para testes e sincronização
│
├── 📂 assets/                  # Insumos gráficos e fontes
│   ├── fonts/
│   │   └── epgyobld.ttf        # Fonte tipográfica japonesa Gyosho Bold
│   └── textures/               # Imagens fotográficas de alta resolução das madeiras
│       ├── hinoki_solid_master.jpg
│       ├── wall_dark.jpg
│       └── ...
│
├── 📂 exports/                 # Imagens rasterizadas em altíssima resolução (PNG)
│   ├── Nafudakake_Kendo.png    # Imagem PNG Ultra-HD de Kendo (2294x3674px)
│   ├── Nafudakake_Iaido.png    # Imagem PNG Ultra-HD de Iaido (2294x1564px)
│   └── Nafudakake_Realista.png # Cópia de compatibilidade
│
├── 📂 data/                    # Dados de contingência offline
│   └── Cadastro - Atletas Kagawa.csv # Cópia local caso esteja sem internet
│
├── 📂 tests_archive/           # Histórico de scripts e testes de validação técnica
│   └── (35 arquivos de prototipagem arquivados)
│
└── 📄 Configurações & Documentos
    ├── README.md               # Este guia completo de uso e arquitetura
    ├── Contexto.md             # Histórico de decisões e regras do dojo
    ├── credentials.json        # Chave de Conta de Serviço Google Cloud (privada)
    ├── credentials.example.json # Exemplo de arquivo de credenciais
    ├── .gitignore              # Protege arquivos sensíveis e temporários
    └── .env.example
```

---

## Regras Marciais e Critérios de Ordenação

A hierarquia marcial do Nafudakake é computada automaticamente pelo `src/google_sync.py`:

1. **Diagramação Tradicional da Direita para a Esquerda (*Migi-Keitai*)**:
   - As graduações mais altas ficam à **direita** (*Kamiza* / 上座).
   - O primeiro trilho (superior) abriga o topo da hierarquia, iniciando no canto superior direito e avançando para a esquerda.
   - Trilhos inferiores continuam a hierarquia, também preenchendo da direita para a esquerda.
2. **Graduação (Dan / Kyu)**:
   - 8º Dan (80) > 7º Dan (70) > 6º Dan (60) > 5º Dan (50) > 4º Dan (40) > 3º Dan (30) > 2º Dan (20) > 1º Dan (10) > 1º Kyu (1) > Iniciantes (0).
3. **Títulos Honoríficos (*Shogo*)**:
   - Aplicáveis a praticantes a partir do 5º Dan:
     - **Hanshi (範士)**: Bônus hierárquico +3
     - **Kyoshi (教士)**: Bônus hierárquico +2
     - **Renshi (錬士)**: Bônus hierárquico +1
4. **Data do Exame**:
   - Em caso de mesma graduação e mesmo *Shogo*, o atleta com data de exame mais antiga (maior tempo na graduação) tem precedência.
5. **Critério Etário (Data de Nascimento)**:
   - Se obtiveram a graduação na mesma data, o praticante com maior idade cronológica (nascimento anterior) tem precedência.
6. **Desempate Final**:
   - Ordem alfabética pelo nome.

---

## Guia de Operação e Uso no Dia a Dia

### Como Atualizar o Nafudakake após Exames de Graduação

Não é necessário atualizar o Nafudakake diariamente. O procedimento deve ser realizado apenas quando houver **exames de graduação**, **novas filiações** ou **alterações de dados** na planilha mestre:

#### Método Rápido (1 Clique no Windows):
1. Dê um duplo-clique no arquivo **`atualizar_nafudakake.bat`**.
2. O script irá:
   - Conectar diretamente na aba mestre `Kenshis` do Google Sheets.
   - Extrair e ordenar os praticantes ativos de Kendo e Iaido.
   - Vetorizar a nova diagramação e salvar os arquivos `Nafudakake_Kendo.svg`, `Nafudakake_Iaido.svg`, `cache_kendo.json` e as imagens em `exports/`.

#### Método por Linha de Comando:
```bash
python src/Nafudakake.py
```

---

### Como Publicar e Refletir no Looker Studio / Datastudio

Após rodar a atualização local, envie as alterações para o GitHub:

```bash
git add .
git commit -m "Atualização do Nafudakake: novos praticantes e graduações"
git push origin main
```

**Como refletir no Looker Studio?**
- **Nenhuma alteração é necessária no Looker Studio**: o relatório já está configurado para ler o link do GitHub Pages (`https://ayyoneda.github.io/nafudakake-kagawa/?embed=true`).
- O GitHub Pages publica automaticamente em **1 a 2 minutos**.
- Basta abrir o relatório no Looker Studio e pressionar **`Ctrl + F5`** (ou clicar nos três pontinhos do menu → **"Atualizar dados"**).

---

### Como Usar a Interface Local (localhost:5050)

Para explorar a ferramenta interativa no computador local, inspecionar plaquetas, testar a busca ou acionar o upload para o Google Drive:

1. Dê um duplo-clique em **`iniciar_servidor.bat`** (ou rode `python src/server.py` no terminal).
2. O navegador abrirá automaticamente em **`http://localhost:5050`**.
3. **Recursos da Interface**:
   - **Seletor de Modalidade**: alterne no topo entre `🥋 Kendo` e `⚔️ Iaido`.
   - **Barra Retrátil**: clique no botão de hambúrguer `☰` para recolher/expandir a barra lateral.
   - **Navegação**: arraste com o mouse para movimentar o quadro (*pan*), role a roda do mouse para *zoom* ou use os botões flutuantes no canto inferior direito.
   - **Saltos por Dan**: clique nos botões de graduação (`7º Dan`, `5º Dan`, etc.) para que a tela dê zoom diretamente nas plaquetas correspondentes.
   - **Busca**: digite qualquer parte do nome ou ideograma para destacar o praticante instantaneamente.

---

## Arquitetura Técnica e Fluxo de Dados

```text
[ Google Sheets ] (Aba mestre 'Kenshis')
        │
        ▼  (src/google_sync.py via Service Account)
[ Normalização & Desempate Hierárquico ]
        │
        ▼  (src/Nafudakake.py + fonttools + texturas Hinoki)
        ├────────────────────────┬────────────────────────┐
        ▼                        ▼                        ▼
[ Nafudakake_Kendo.svg ]  [ Nafudakake_Iaido.svg ]  [ cache_*.json ]
[ exports/Kendo.png    ]  [ exports/Iaido.png    ]
        │
        ▼  (Git Push para GitHub Pages com HTTPS)
[ Visualizador Web Interativo ] (index.html + app.js + style.css)
        │
        ▼  (Embed via Iframe: ?embed=true)
[ Google Looker Studio / Telão do Dojo ]
```

---

## Configuração de Credenciais e Contingência Offline

### 1. Conexão Online com o Google Cloud (`credentials.json`)
Para leitura automática da aba `Kenshis` da planilha e upload no Google Drive:
- Obtenha um arquivo de chave de **Conta de Serviço (Service Account)** no Google Cloud Console com as APIs *Google Sheets API* e *Google Drive API* habilitadas.
- Salve o arquivo na raiz do projeto com o nome **`credentials.json`**.
- Compartilhe a planilha do dojo e a pasta do Google Drive com o e-mail da Conta de Serviço (`client_email`), concedendo permissão de **Leitor** na planilha e **Editor** na pasta do Drive.
- O arquivo `credentials.json` está protegido pelo `.gitignore` e **nunca** é enviado ao GitHub.

### 2. Modo de Contingência Offline (Sem Internet)
Caso a máquina esteja sem conexão ou sem o arquivo `credentials.json`, o sistema aciona fallbacks automáticos em cascata:
1. Lê o cache local `cache_kendo.json` ou `cache_iaido.json`.
2. Caso não exista cache, lê o arquivo CSV local em `data/Cadastro - Atletas Kagawa (respostas) - Nafudakake.csv`.

---

## Licença e Créditos

Desenvolvido com respeito às tradições das artes marciais japonesas para a **Associação Kagawa de Kendo (洗心香武館 - Senshin Kabukan)**.  
Todos os direitos reservados à diretoria e mestres do dojo.
