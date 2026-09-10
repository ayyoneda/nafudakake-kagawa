# Nafudakake Digital (名札掛け) — 洗心香武館 (Senshin Kabukan)
### Associação Kagawa de Kendo | Kendo & Iaido

Painel digital interativo e gerador vetorial de alta definição para o **Nafudakake tradicional do dojo**, com caligrafia clássica japonesa *Gyosho* vetorizada em curvas puras, texturas orgânicas de madeira Hinoki maciça e integração direta com o Google Sheets e Google Looker Studio.

---

## Sumário
1. [Visão Geral e Propósito](#visão-geral-e-propósito)
2. [Recursos Principais](#recursos-principais)
3. [Arquitetura do Projeto](#arquitetura-do-projeto)
4. [Como Executar Localmente](#como-executar-localmente)
5. [Como Sincronizar com a Planilha](#como-sincronizar-com-a-planilha)
6. [Publicação e Incorporação no Looker Studio](#publicação-e-incorporação-no-looker-studio)
7. [Regras Marciais e Critérios de Ordenação](#regras-marciais-e-critérios-de-ordenação)
8. [Estrutura de Arquivos](#estrutura-de-arquivos)

---

## Visão Geral e Propósito

Nas artes marciais tradicionais japonesas (*Budo*), o **Nafudakake** (名札掛け) é o painel de madeira exposto na parede de honra (*Kamiza*) do dojo contendo as plaquetas individuais (*Nafuda*) de todos os praticantes (*Kenshis*), organizadas estritamente de acordo com a hierarquia marcial.

Este projeto digitaliza o Nafudakake da **Associação Kagawa de Kendo**, permitindo:
- Visualização interativa na web com aproximação (*zoom*), navegação fluida (*pan*) e busca de praticantes.
- Exibição limpa em televisores e monitores do dojo, além de integração em dashboards do **Google Looker Studio**.
- Geração automatizada de arquivos vetoriais **SVG** (leves, nítidos em qualquer resolução) e imagens **PNG Ultra-HD**.
- Eliminação de manutenção manual: qualquer graduação ou novo atleta cadastrado na planilha mestre reflete automaticamente no painel.

---

## Recursos Principais

- **Vetorização Caligráfica Autêntica (Gyosho Bold)**: Todos os ideogramas japoneses (*Kanji*) são convertidos em curvas Bézier vetoriais (`<path>`) a partir da fonte [epgyobld.ttf](epgyobld.ttf). Não há dependência de fontes instaladas no sistema ou no navegador — zero risco de ideogramas não renderizados ("tofu").
- **Madeira Hinoki Realista Contínua**: Cada ripa possui grão e nervura verticais contínuos de cipreste japonês Hinoki, sem linhas de emenda ou repetições artificiais.
- **Multi-Modalidade Nativa**: Alternância instantânea entre **劍道 Kendo** e **居合道 Iaido** (e preparado para expansão futura para **杖道 Jodo**).
- **Barra Lateral Retrátil**: Painel retrátil com busca inteligente em tempo real por nome ocidental, ideograma ou graduação, permitindo aproveitar 100% da largura da tela para o quadro.
- **Saltos Rápidos por Dan**: Botões dinâmicos que destacam e focam instantaneamente nos praticantes de cada graduação (八段 a 無段).
- **Inspeção Detalhada (Tooltip)**: Passar o mouse ou clicar sobre uma plaqueta exibe nome completo, título de honra (*Shogo*), graduação e data oficial de registro.

---

## Arquitetura do Projeto

```text
[ Google Sheets ] (Aba mestre 'Kenshis')
        │
        ▼  (google_sync.py - Service Account)
[ Normalização & Desempate Hierárquico ]
        │
        ├────────────────────────┬────────────────────────┐
        ▼                        ▼                        ▼
[ Nafudakake_Kendo.svg ]  [ Nafudakake_Iaido.svg ]  [ cache_*.json ]
[ Nafudakake_Kendo.png ]  [ Nafudakake_Iaido.png ]
        │
        ▼ (GitHub Pages com HTTPS)
[ Visualizador Web Interativo ] (index.html + app.js + style.css)
        │
        ▼ (Embed Iframe)
[ Google Looker Studio / Telão do Dojo ]
```

---

## Como Executar Localmente

### Pré-requisitos
- Python 3.9+ instalado
- Dependências instaladas:
  ```bash
  pip install flask fonttools PySide6 google-api-python-client google-auth
  ```

### Iniciando o Servidor Local
Execute no terminal:
```bash
python server.py
```
Abra seu navegador em: **`http://localhost:5050`**

---

## Como Sincronizar com a Planilha

Sempre que a diretoria do dojo cadastrar novos praticantes ou novas graduações no Google Sheets:

1. Execute a sincronização manual:
   ```bash
   python google_sync.py
   ```
   *(Ou clique no botão **"Sincronizar Planilha"** na barra lateral da aplicação local).*

2. Atualize o repositório no GitHub:
   ```bash
   git add .
   git commit -m "Atualização de praticantes e graduações"
   git push
   ```

Em poucos segundos, o GitHub Pages e o Looker Studio atualizarão automaticamente com as novas plaquetas.

---

## Publicação e Incorporação no Looker Studio

O Google Looker Studio exige links seguros em **HTTPS** para componentes incorporados. O projeto utiliza o **GitHub Pages** para servir os arquivos estáticos de forma 100% gratuita:

1. No repositório GitHub, acesse **Settings > Pages**.
2. Em **Branch**, selecione `main` e pasta `/ (root)`, e clique em **Save**.
3. Copie a URL gerada: `https://SEU_USUARIO.github.io/NOME_DO_REPO/`.
4. No seu relatório do Looker Studio:
   - Clique em **Inserir > Incorporar URL** (ícone `< >`).
   - Cole a URL com o parâmetro de embed:
     ```text
     https://SEU_USUARIO.github.io/NOME_DO_REPO/?embed=true
     ```

*O parâmetro `?embed=true` oculta automaticamente botões administrativos de sincronização e nuvem, exibindo apenas o painel interativo limpo para os alunos e visitantes.*

---

## Regras Marciais e Critérios de Ordenação

As plaquetas são diagramadas da direita para a esquerda (*Migi-Keitai* tradicional) seguindo rigorosamente as diretrizes da Federação e tradições do Kagawa:

1. **Graduação (Dan / Kyu)**: Grau mais alto posicionado mais à direita e ao topo.
2. **Títulos de Maestria (Shogo)**:
   - **Hanshi (範士)**: Bônus hierárquico +3
   - **Kyoshi (教士)**: Bônus hierárquico +2
   - **Renshi (錬士)**: Bônus hierárquico +1
3. **Data do Exame**: Em caso de mesmo Dan e Shogo, o atleta mais antigo na graduação tem precedência (data mais antiga primeiro).
4. **Critério Etário**: Se graduados na mesma data, o atleta com maior idade cronológica (data de nascimento mais antiga) tem precedência.
5. **Alfabético**: Desempate final por ordem alfabética do nome.

---

## Estrutura de Arquivos

```text
├── index.html               # Aplicação web frontend (servida na raiz pelo GitHub Pages)
├── app.js                   # Lógica interativa (pan/zoom, busca, chips, barra retrátil)
├── style.css                # Estilos visuais japoneses e responsividade
├── server.py                # Servidor local Flask com APIs de exportação e sync
├── Nafudakake.py            # Motor gráfico de renderização SVG, PNG e vetorização de glifos
├── google_sync.py           # Conector Google Sheets (aba Kenshis) e Google Drive
├── Nafudakake_Kendo.svg     # Vetor estático de Kendo para GitHub Pages & Looker Studio
├── Nafudakake_Iaido.svg     # Vetor estático de Iaido para GitHub Pages & Looker Studio
├── Nafudakake_Kendo.png     # Imagem Ultra-HD de Kendo (para impressão ou arquivo)
├── Nafudakake_Iaido.png     # Imagem Ultra-HD de Iaido (para impressão ou arquivo)
├── cache_kendo.json         # Base processada de Kendo para execução estática no GitHub Pages
├── cache_iaido.json         # Base processada de Iaido para execução estática no GitHub Pages
├── AKK_colorido.png         # Brasão oficial da Associação Kagawa de Kendo
├── epgyobld.ttf             # Fonte de caligrafia tradicional Gyosho Bold
├── textures/                # Texturas fotográficas de madeira Hinoki e cedro
│   ├── hinoki_wood_texture.jpg
│   ├── hinoki_wood_vertical.jpg
│   ├── hinoki_wood_amber.jpg
│   ├── hinoki_solid_plank.jpg
│   └── dojo_dark_wood.jpg
├── credentials.example.json # Modelo de credenciais do Google Cloud
├── .gitignore               # Proteção de credenciais (credentials.json) e arquivos temporários
└── Contexto.md              # Contexto histórico e registros da instituição
```

---

## Licença e Créditos

Desenvolvido para a **Associação Kagawa de Kendo (洗心香武館)**.  
Todos os direitos reservados à diretoria e mestres do dojo.
