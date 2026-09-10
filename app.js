/**
 * Nafudakake Digital - Lógica de Interatividade, Pan/Zoom e Sincronização
 * 洗心香武館 (Associação Kagawa de Kendo)
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elementos do DOM
  const viewport = document.getElementById("viewport");
  const canvasWrapper = document.getElementById("canvas-wrapper");
  const svgContainer = document.getElementById("svg-container");
  const tooltip = document.getElementById("tooltip");
  const searchInput = document.getElementById("search-input");
  const clearSearchBtn = document.getElementById("clear-search");
  const searchStats = document.getElementById("search-stats");
  const danChipsContainer = document.getElementById("dan-chips-container");
  const toggleRomaji = document.getElementById("toggle-romaji");
  const btnCloseSidebar = document.getElementById("btn-close-sidebar");
  const btnOpenSidebar = document.getElementById("btn-open-sidebar");
  const appLayout = document.querySelector(".app-layout");
  const btnSync = document.getElementById("btn-sync");
  const btnUploadDrive = document.getElementById("btn-upload-drive");
  const feedbackMsg = document.getElementById("feedback-msg");
  const sourcePillText = document.getElementById("source-text");
  const totalKenshisEl = document.getElementById("total-kenshis");

  // Seletor de Modalidade (Kendo / Iaido)
  const btnModalityKendo = document.getElementById("btn-modality-kendo");
  const btnModalityIaido = document.getElementById("btn-modality-iaido");
  const countKendoEl = document.getElementById("count-kendo");
  const countIaidoEl = document.getElementById("count-iaido");
  const btnDownloadSvg = document.getElementById("btn-download-svg");
  const btnDownloadPng = document.getElementById("btn-download-png");

  // Estado da Aplicação
  let currentModalidade = "kendo";
  let scale = 1.0;
  let translateX = 0;
  let translateY = 0;
  let isDragging = false;
  let startX = 0;
  let startY = 0;

  // Estado dos Dados
  let membersList = [];
  let membersMap = new Map();

  // ==========================================
  // 1. CARREGAMENTO DO SVG E DADOS
  // ==========================================
  async function loadNafudakakeSvg() {
    try {
      const cols = 18;
      const showRomaji = toggleRomaji ? toggleRomaji.checked : true;
      let res = await fetch(
        `/api/nafudakake.svg?modalidade=${currentModalidade}&placas_por_linha=${cols}&show_romaji=${showRomaji}&t=${Date.now()}`
      ).catch(() => null);

      // Fallback estático para GitHub Pages (sem backend Flask)
      if (!res || !res.ok) {
        const cap = currentModalidade.charAt(0).toUpperCase() + currentModalidade.slice(1);
        res = await fetch(`Nafudakake_${cap}.svg?t=${Date.now()}`);
      }

      if (!res.ok) throw new Error("Erro ao carregar SVG");
      const svgText = await res.text();
      svgContainer.innerHTML = svgText;
      
      initPlaqueInteractions();
      fitToScreen();
    } catch (err) {
      console.error("Falha ao carregar SVG:", err);
      showFeedback("Falha ao renderizar o quadro SVG.", "error");
    }
  }

  async function loadMembersData() {
    try {
      let res = await fetch(`/api/members?modalidade=${currentModalidade}`).catch(() => null);
      let data = null;

      if (res && res.ok) {
        data = await res.json();
      } else {
        // Fallback para cache local JSON (funciona 100% no GitHub Pages)
        const cacheRes = await fetch(`cache_${currentModalidade}.json`);
        if (cacheRes.ok) {
          const raw = await cacheRes.json();
          data = {
            members: raw,
            source: "Base Sincronizada"
          };
        }
      }

      const rawList = (data && data.members) ? data.members : [];
      membersList = rawList.map((m) => {
        const ordem = m.ordem || m.Ordem || "";
        const nomeCompleto = m.nome_completo || m["Nome completo"] || m.nome_abreviado || m["Nome abreviado"] || "";
        const nomeAbreviado = m.nome_abreviado || m["Nome abreviado"] || nomeCompleto;
        const jap = m.jap || m["Japonês"] || "";
        const gradRaw = m.grad_raw || m.graduacao || m["Graduação"] || "";
        const shogo = m.shogo || m.Shogo || "";
        const dataGrad = m.data_grad || m["Data Graduação"] || m["Data Registro"] || "";

        let danWeight = 0;
        if (m.dan_weight !== undefined && m.dan_weight !== null && !isNaN(Number(m.dan_weight))) {
          danWeight = Number(m.dan_weight);
        } else if (m.base_weight !== undefined && m.base_weight !== null && !isNaN(Number(m.base_weight))) {
          danWeight = Number(m.base_weight);
        } else if (m.Peso !== undefined && m.Peso !== null && !isNaN(Number(m.Peso))) {
          danWeight = Number(m.Peso);
        }

        return {
          ordem: String(ordem),
          nome_completo: nomeCompleto,
          nome_abreviado: nomeAbreviado,
          romaji: nomeAbreviado,
          jap: jap,
          grad_raw: gradRaw,
          graduacao: gradRaw,
          dan_weight: danWeight,
          shogo: shogo,
          data_grad: dataGrad
        };
      });

      totalKenshisEl.textContent = membersList.length;
      sourcePillText.textContent = (data && data.source) ? data.source : "Base Local";

      if (currentModalidade === "kendo" && countKendoEl) {
        countKendoEl.textContent = membersList.length;
      } else if (currentModalidade === "iaido" && countIaidoEl) {
        countIaidoEl.textContent = membersList.length;
      }

      membersMap.clear();
      membersList.forEach((m) => {
        const id = `kenshi-${m.ordem}`;
        membersMap.set(id, m);
      });

      renderDanChips();
    } catch (err) {
      console.warn("Erro ao buscar dados JSON dos membros:", err);
    }
  }

  // ==========================================
  // 2. PAN & ZOOM (ACELERAÇÃO POR GPU)
  // ==========================================
  function updateTransform() {
    svgContainer.style.transform = `translate3d(${translateX}px, ${translateY}px, 0) scale(${scale})`;
  }

  function fitToScreen() {
    const svgEl = svgContainer.querySelector("svg");
    if (!svgEl) return;

    const vpRect = viewport.getBoundingClientRect();
    const svgWidth = parseFloat(svgEl.getAttribute("width")) || 1147;
    const svgHeight = parseFloat(svgEl.getAttribute("height")) || 1837;

    const scaleX = (vpRect.width - 60) / svgWidth;
    const scaleY = (vpRect.height - 60) / svgHeight;
    scale = Math.min(scaleX, scaleY, 1.0);

    translateX = (vpRect.width - svgWidth * scale) / 2;
    translateY = (vpRect.height - svgHeight * scale) / 2;

    updateTransform();
  }

  // Zoom no cursor com a roda do mouse
  viewport.addEventListener("wheel", (e) => {
    e.preventDefault();
    const zoomFactor = 1.15;
    const vpRect = viewport.getBoundingClientRect();
    const mouseX = e.clientX - vpRect.left;
    const mouseY = e.clientY - vpRect.top;

    const newScale = e.deltaY < 0 ? scale * zoomFactor : scale / zoomFactor;
    // Limites de zoom: 0.15x a 4.0x
    const clampedScale = Math.max(0.15, Math.min(4.5, newScale));

    // Ajusta o pan para dar zoom exatamente onde o mouse aponta
    translateX = mouseX - (mouseX - translateX) * (clampedScale / scale);
    translateY = mouseY - (mouseY - translateY) * (clampedScale / scale);
    scale = clampedScale;

    updateTransform();
  }, { passive: false });

  // Arraste com o Mouse (Pan) com bloqueio absoluto de clique pós-arrasto
  let hasDragged = false;
  let lastDragEndTime = 0;
  let dragOriginX = 0;
  let dragOriginY = 0;

  viewport.addEventListener("mousedown", (e) => {
    // Apenas botão esquerdo (0) ou do meio (1)
    if (e.button !== 0 && e.button !== 1) return;
    isDragging = true;
    hasDragged = false;
    dragOriginX = e.clientX;
    dragOriginY = e.clientY;
    startX = e.clientX - translateX;
    startY = e.clientY - translateY;
    viewport.style.cursor = "grabbing";
    e.preventDefault();
  });

  window.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    const dist = Math.hypot(e.clientX - dragOriginX, e.clientY - dragOriginY);
    if (dist > 3) {
      hasDragged = true;
    }
    translateX = e.clientX - startX;
    translateY = e.clientY - startY;
    updateTransform();
  });

  window.addEventListener("mouseup", () => {
    if (isDragging) {
      isDragging = false;
      viewport.style.cursor = "grab";
      if (hasDragged) {
        lastDragEndTime = Date.now();
      }
      setTimeout(() => {
        hasDragged = false;
      }, 350);
    }
  });

  window.addEventListener("mouseleave", () => {
    if (isDragging) {
      isDragging = false;
      viewport.style.cursor = "grab";
      if (hasDragged) {
        lastDragEndTime = Date.now();
      }
      setTimeout(() => {
        hasDragged = false;
      }, 350);
    }
  });

  // Intercepta e anula absolutamente cliques gerados após arrasto (captura global)
  window.addEventListener("click", (e) => {
    if (hasDragged || (Date.now() - lastDragEndTime < 350)) {
      e.stopPropagation();
      e.stopImmediatePropagation();
      e.preventDefault();
    }
  }, true);

  // Botões de Zoom Flutuantes (ancorados no centro da tela)
  document.getElementById("btn-zoom-in").addEventListener("click", () => {
    const vpRect = viewport.getBoundingClientRect();
    const cx = vpRect.width / 2;
    const cy = vpRect.height / 2;
    const newScale = Math.min(4.5, scale * 1.3);
    translateX = cx - (cx - translateX) * (newScale / scale);
    translateY = cy - (cy - translateY) * (newScale / scale);
    scale = newScale;
    updateTransform();
  });

  document.getElementById("btn-zoom-out").addEventListener("click", () => {
    const vpRect = viewport.getBoundingClientRect();
    const cx = vpRect.width / 2;
    const cy = vpRect.height / 2;
    const newScale = Math.max(0.15, scale / 1.3);
    translateX = cx - (cx - translateX) * (newScale / scale);
    translateY = cy - (cy - translateY) * (newScale / scale);
    scale = newScale;
    updateTransform();
  });

  document.getElementById("btn-zoom-reset").addEventListener("click", fitToScreen);

  window.addEventListener("resize", () => {
    if (scale <= 1.05) fitToScreen();
  });

  document.getElementById("btn-fullscreen").addEventListener("click", () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    } else {
      document.exitFullscreen().catch(() => {});
    }
  });

  // Controle da Barra Lateral Retrátil
  function setSidebarCollapsed(collapsed) {
    if (appLayout) {
      if (collapsed) {
        appLayout.classList.add("sidebar-collapsed");
      } else {
        appLayout.classList.remove("sidebar-collapsed");
      }
      setTimeout(() => {
        fitToScreen();
      }, 360);
    }
  }

  if (btnCloseSidebar) {
    btnCloseSidebar.addEventListener("click", () => setSidebarCollapsed(true));
  }
  if (btnOpenSidebar) {
    btnOpenSidebar.addEventListener("click", () => setSidebarCollapsed(false));
  }

  // ==========================================
  // 3. INTERAÇÃO E INSPEÇÃO DAS PLAQUETAS
  // ==========================================
  function initPlaqueInteractions() {
    const plaques = svgContainer.querySelectorAll(".kenshi-plaque");

    plaques.forEach((p) => {
      p.addEventListener("mouseenter", (e) => {
        const id = p.id;
        const info = membersMap.get(id);

        const romaji = p.getAttribute("data-nome") || (info ? info.romaji : "");
        const kanji = p.getAttribute("data-kanji") || (info ? info.jap : "");
        const danWeight = p.getAttribute("data-dan") || (info ? info.dan_weight : "");

        const ttShogo = document.getElementById("tt-shogo");
        const ttKanji = document.getElementById("tt-kanji");
        const ttRomaji = document.getElementById("tt-romaji");
        const ttGrad = document.getElementById("tt-grad");
        const ttData = document.getElementById("tt-data");

        if (info && info.shogo) {
          ttShogo.textContent = info.shogo;
          ttShogo.style.display = "inline-block";
        } else {
          ttShogo.style.display = "none";
        }

        ttKanji.textContent = kanji;
        ttRomaji.textContent = romaji;
        ttGrad.textContent = info ? info.grad_raw : `Dan Grau ${danWeight}`;
        ttData.textContent = (info && info.data_grad) ? info.data_grad : "Não informada";

        tooltip.classList.add("visible");
      });

      p.addEventListener("mousemove", (e) => {
        const vpRect = viewport.getBoundingClientRect();
        let left = e.clientX - vpRect.left + 16;
        let top = e.clientY - vpRect.top - 30;

        // Mantém dentro do viewport
        if (left + 220 > vpRect.width) left = e.clientX - vpRect.left - 230;
        if (top + 160 > vpRect.height) top = vpRect.height - 170;
        if (top < 10) top = 10;

        tooltip.style.left = `${left}px`;
        tooltip.style.top = `${top}px`;
      });

      p.addEventListener("mouseleave", () => {
        tooltip.classList.remove("visible");
      });

      p.addEventListener("click", (e) => {
        if (hasDragged || (Date.now() - lastDragEndTime < 350)) {
          e.stopPropagation();
          e.stopImmediatePropagation();
          e.preventDefault();
          return;
        }
        zoomToElement(p);
      });
    });
  }

  function zoomToElement(el) {
    const elRect = el.getBoundingClientRect();
    const vpRect = viewport.getBoundingClientRect();

    // Centraliza o elemento no viewport com zoom agradável (1.8x)
    const targetScale = 1.8;
    const svgEl = svgContainer.querySelector("svg");
    const ctm = el.getCTM();

    if (ctm) {
      const bbox = el.getBBox();
      const elemCenterX = bbox.x + bbox.width / 2;
      const elemCenterY = bbox.y + bbox.height / 2;

      scale = targetScale;
      translateX = (vpRect.width / 2) - (elemCenterX * scale);
      translateY = (vpRect.height / 2) - (elemCenterY * scale);
      updateTransform();
    }
  }

  // ==========================================
  // 4. BUSCA DINÂMICA E DESTAQUE NO NAFUDAKAKE
  // ==========================================
  function filterKenshis(query) {
    const q = query.trim().toLowerCase();
    const plaques = svgContainer.querySelectorAll(".kenshi-plaque");

    if (!q) {
      plaques.forEach((p) => {
        p.classList.remove("kenshi-highlight", "kenshi-dimmed");
      });
      searchStats.textContent = `Mostrando todos os ${plaques.length} praticantes`;
      clearSearchBtn.style.display = "none";
      return;
    }

    clearSearchBtn.style.display = "block";
    let matchCount = 0;
    let firstMatch = null;

    plaques.forEach((p) => {
      const nome = (p.getAttribute("data-nome") || "").toLowerCase();
      const kanji = (p.getAttribute("data-kanji") || "").toLowerCase();
      const info = membersMap.get(p.id);
      const grad = info ? info.grad_raw.toLowerCase() : "";

      const matches = nome.includes(q) || kanji.includes(q) || grad.includes(q);

      if (matches) {
        p.classList.add("kenshi-highlight");
        p.classList.remove("kenshi-dimmed");
        matchCount++;
        if (!firstMatch) firstMatch = p;
      } else {
        p.classList.remove("kenshi-highlight");
        p.classList.add("kenshi-dimmed");
      }
    });

    searchStats.textContent = matchCount === 0 
      ? "Nenhum praticante localizado" 
      : `${matchCount} praticante(s) encontrado(s)`;

    if (firstMatch && matchCount === 1) {
      zoomToElement(firstMatch);
    }
  }

  searchInput.addEventListener("input", (e) => filterKenshis(e.target.value));
  clearSearchBtn.addEventListener("click", () => {
    searchInput.value = "";
    filterKenshis("");
    fitToScreen();
  });

  // ==========================================
  // 4b. CHIPS DE DAN DINÂMICOS & TROCA DE MODALIDADE
  // ==========================================
  const DAN_LABELS = {
    80: "8º Dan",
    70: "7º Dan",
    60: "6º Dan",
    50: "5º Dan",
    40: "4º Dan",
    30: "3º Dan",
    20: "2º Dan",
    10: "1º Dan",
    1: "1º Kyu",
    0: "Sem Dan"
  };

  function renderDanChips() {
    if (!danChipsContainer) return;
    danChipsContainer.innerHTML = "";

    // Botão "Todos"
    const allBtn = document.createElement("button");
    allBtn.className = "chip active";
    allBtn.setAttribute("data-dan", "all");
    allBtn.textContent = "Todos";
    danChipsContainer.appendChild(allBtn);

    // Filtra graduações com ao menos um praticante na modalidade atual (excluindo valores nulos ou NaN)
    const uniqueDans = Array.from(
      new Set(
        membersList
          .map((m) => m.dan_weight)
          .filter((d) => d !== undefined && d !== null && !isNaN(d) && typeof d === "number")
      )
    ).sort((a, b) => b - a);

    uniqueDans.forEach((danVal) => {
      const label = DAN_LABELS[danVal] || (danVal >= 10 ? `${Math.floor(danVal / 10)}º Dan` : "Sem Dan");
      const btn = document.createElement("button");
      btn.className = "chip";
      btn.setAttribute("data-dan", danVal);
      btn.textContent = label;
      danChipsContainer.appendChild(btn);
    });

    const chips = danChipsContainer.querySelectorAll(".chip");
    chips.forEach((chip) => {
      chip.addEventListener("click", () => {
        chips.forEach((c) => c.classList.remove("active"));
        chip.classList.add("active");

        const danVal = chip.getAttribute("data-dan");
        if (danVal === "all") {
          searchInput.value = "";
          filterKenshis("");
          fitToScreen();
          return;
        }

        const headerEl = svgContainer.querySelector(`#header-${danVal}`);
        if (headerEl) {
          zoomToElement(headerEl);
        }

        const plaques = svgContainer.querySelectorAll(".kenshi-plaque");
        plaques.forEach((p) => {
          if (p.getAttribute("data-dan") === String(danVal)) {
            p.classList.add("kenshi-highlight");
            p.classList.remove("kenshi-dimmed");
          } else {
            p.classList.remove("kenshi-highlight");
            p.classList.add("kenshi-dimmed");
          }
        });
        searchStats.textContent = `Exibindo praticantes ${chip.textContent}`;
      });
    });
  }

  async function switchModalidade(mod) {
    if (currentModalidade === mod) return;
    currentModalidade = mod;

    if (mod === "kendo") {
      if (btnModalityKendo) btnModalityKendo.classList.add("active");
      if (btnModalityIaido) btnModalityIaido.classList.remove("active");
    } else {
      if (btnModalityIaido) btnModalityIaido.classList.add("active");
      if (btnModalityKendo) btnModalityKendo.classList.remove("active");
    }

    const cap = mod.charAt(0).toUpperCase() + mod.slice(1);
    if (btnDownloadSvg) {
      btnDownloadSvg.href = `/Nafudakake_${cap}.svg`;
      btnDownloadSvg.setAttribute("download", `Nafudakake_${cap}_SenshinKabukan.svg`);
    }
    if (btnDownloadPng) {
      btnDownloadPng.href = `/api/export-png?modalidade=${mod}`;
    }

    searchInput.value = "";
    clearSearchBtn.style.display = "none";
    searchStats.textContent = "Mostrando todas as plaquetas";

    await loadMembersData();
    await loadNafudakakeSvg();
  }

  if (btnModalityKendo) {
    btnModalityKendo.addEventListener("click", () => switchModalidade("kendo"));
  }
  if (btnModalityIaido) {
    btnModalityIaido.addEventListener("click", () => switchModalidade("iaido"));
  }

  // ==========================================
  // 5. AJUSTES VISUAIS EM TEMPO REAL
  // ==========================================
  if (toggleRomaji) {
    toggleRomaji.addEventListener("change", () => {
      loadNafudakakeSvg();
    });
  }

  // ==========================================
  // 6. AÇÕES: SINCRONIZAÇÃO E GOOGLE DRIVE
  // ==========================================
  let feedbackTimer = null;
  function showFeedback(text, type = "success") {
    if (feedbackTimer) clearTimeout(feedbackTimer);
    feedbackMsg.textContent = text;
    feedbackMsg.className = `feedback-msg ${type}`;
    feedbackMsg.style.display = "block";
    feedbackTimer = setTimeout(() => {
      feedbackMsg.style.display = "none";
    }, 8000);
  }

  btnSync.addEventListener("click", async () => {
    btnSync.disabled = true;
    btnSync.querySelector("span").textContent = "Sincronizando...";

    try {
      const res = await fetch("/api/sync", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          placas_por_linha: 18,
          show_romaji: toggleRomaji ? toggleRomaji.checked : true
        })
      });

      const data = await res.json();
      if (!data.success) throw new Error(data.error || "Erro desconhecido");

      if (data.total_kendo && countKendoEl) countKendoEl.textContent = data.total_kendo;
      if (data.total_iaido && countIaidoEl) countIaidoEl.textContent = data.total_iaido;

      showFeedback(data.message, "success");
      await loadMembersData();
      await loadNafudakakeSvg();
    } catch (err) {
      showFeedback(`Erro ao sincronizar: ${err.message}`, "error");
    } finally {
      btnSync.disabled = false;
      btnSync.querySelector("span").textContent = "Sincronizar Planilha";
    }
  });

  btnUploadDrive.addEventListener("click", async () => {
    btnUploadDrive.disabled = true;
    btnUploadDrive.querySelector("span").textContent = "Enviando ao Drive...";

    try {
      const res = await fetch("/api/upload-drive", { method: "POST" });
      const data = await res.json();
      if (!data.success) {
        // Se der erro por falta de credentials.json ou pasta não compartilhada, abre o modal
        if (data.error && data.error.includes("credentials.json")) {
          showFeedback("Arquivo credentials.json necessário para upload no Drive. Abrindo configurações...", "error");
          openGoogleModal();
          return;
        }
        if (data.error && (data.error.includes("não está compartilhada") || data.error.includes("File not found"))) {
          showFeedback("Pasta do Google Drive não compartilhada com a Conta de Serviço. Abrindo orientações...", "error");
          openGoogleModal();
          return;
        }
        throw new Error(data.error || "Erro ao fazer upload");
      }

      if (data.partial) {
        showFeedback(data.message, "info");
      } else {
        showFeedback(data.message || "Arquivos PNG e SVG atualizados com sucesso no Google Drive!", "success");
      }
    } catch (err) {
      showFeedback(`Falha no Google Drive: ${err.message}`, "error");
    } finally {
      btnUploadDrive.disabled = false;
      btnUploadDrive.querySelector("span").textContent = "Publicar no Google Drive";
    }
  });

  // ==========================================
  // 7. MODAL DE INTEGRAÇÃO GOOGLE CLOUD
  // ==========================================
  const modalGoogleSetup = document.getElementById("modal-google-setup");
  const btnOpenGoogleModal = document.getElementById("btn-open-google-modal");
  const btnCloseModal = document.getElementById("btn-close-modal");
  const btnModalOk = document.getElementById("btn-modal-ok");
  const btnTestConnection = document.getElementById("btn-test-connection");
  const testConnResult = document.getElementById("test-connection-result");
  const sheetsStatusBadge = document.getElementById("sheets-status-badge");
  const driveStatusBadge = document.getElementById("drive-status-badge");
  const activeSourceDetail = document.getElementById("active-source-detail");
  const dropZone = document.getElementById("drop-credentials-zone");
  const fileInput = document.getElementById("file-credentials-input");
  const credsUploadFeedback = document.getElementById("credentials-upload-feedback");
  const saEmailDisplay = document.getElementById("sa-email-display");
  const btnCopySaEmail = document.getElementById("btn-copy-sa-email");
  const driveDiagMsg = document.getElementById("drive-diag-msg");

  if (btnCopySaEmail && saEmailDisplay) {
    btnCopySaEmail.addEventListener("click", () => {
      const email = saEmailDisplay.textContent.trim();
      navigator.clipboard.writeText(email).then(() => {
        btnCopySaEmail.textContent = "✓ Copiado!";
        setTimeout(() => { btnCopySaEmail.textContent = "Copiar E-mail"; }, 2500);
      });
    });
  }

  function openGoogleModal() {
    modalGoogleSetup.classList.add("open");
    runDiagnosticTest();
  }

  function closeGoogleModal() {
    modalGoogleSetup.classList.remove("open");
  }

  if (btnOpenGoogleModal) {
    btnOpenGoogleModal.addEventListener("click", openGoogleModal);
  }
  if (btnCloseModal) {
    btnCloseModal.addEventListener("click", closeGoogleModal);
  }
  if (btnModalOk) {
    btnModalOk.addEventListener("click", closeGoogleModal);
  }

  modalGoogleSetup.addEventListener("click", (e) => {
    if (e.target === modalGoogleSetup) closeGoogleModal();
  });

  async function runDiagnosticTest() {
    sheetsStatusBadge.textContent = "Verificando...";
    sheetsStatusBadge.className = "status-badge warn";
    driveStatusBadge.textContent = "Verificando...";
    driveStatusBadge.className = "status-badge warn";

    try {
      const res = await fetch("/api/test-sheets");
      const diag = await res.json();

      if (diag.public_url_ok) {
        sheetsStatusBadge.textContent = "Conectado (Link Aberto)";
        sheetsStatusBadge.className = "status-badge ok";
      } else if (diag.service_account_ok) {
        sheetsStatusBadge.textContent = "Conectado (API)";
        sheetsStatusBadge.className = "status-badge ok";
      } else {
        sheetsStatusBadge.textContent = "Restrito (HTTP 401)";
        sheetsStatusBadge.className = "status-badge error";
      }

      if (diag.service_account_email && saEmailDisplay) {
        saEmailDisplay.textContent = diag.service_account_email;
      }

      if (!diag.service_account_configured) {
        driveStatusBadge.textContent = "Requer credentials.json";
        driveStatusBadge.className = "status-badge warn";
        if (driveDiagMsg) driveDiagMsg.textContent = "";
      } else if (diag.drive_folder_ok) {
        driveStatusBadge.textContent = "Pronto / Pasta Liberada";
        driveStatusBadge.className = "status-badge ok";
        if (driveDiagMsg) {
          driveDiagMsg.textContent = "✓ Permissão de gravação confirmada na pasta do Drive!";
          driveDiagMsg.style.color = "#86efac";
        }
      } else {
        driveStatusBadge.textContent = "Pasta Não Compartilhada";
        driveStatusBadge.className = "status-badge error";
        if (driveDiagMsg) {
          driveDiagMsg.textContent = diag.drive_folder_msg || "Compartilhe a pasta com o e-mail acima como Editor.";
          driveDiagMsg.style.color = "#fca5a5";
        }
      }

      activeSourceDetail.textContent = `Fonte em uso: ${diag.active_source}`;
      return diag;
    } catch (err) {
      sheetsStatusBadge.textContent = "Erro de Conexão";
      sheetsStatusBadge.className = "status-badge error";
      activeSourceDetail.textContent = `Erro ao verificar: ${err.message}`;
    }
  }

  if (btnTestConnection) {
    btnTestConnection.addEventListener("click", async () => {
      btnTestConnection.disabled = true;
      testConnResult.textContent = "Consultando Google...";
      testConnResult.style.color = "var(--text-muted)";

      const diag = await runDiagnosticTest();
      btnTestConnection.disabled = false;

      if (diag && (diag.public_url_ok || diag.service_account_ok)) {
        testConnResult.textContent = "✓ Conexão bem-sucedida!";
        testConnResult.style.color = "#86efac";
      } else {
        testConnResult.textContent = "⚠ Planilha privada (401). Compartilhe com 'Qualquer pessoa com o link'!";
        testConnResult.style.color = "#fca5a5";
      }
    });
  }

  // Upload do credentials.json por Drag & Drop ou clique
  if (dropZone && fileInput) {
    dropZone.addEventListener("click", () => fileInput.click());

    dropZone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropZone.style.background = "rgba(212, 175, 55, 0.18)";
    });

    dropZone.addEventListener("dragleave", () => {
      dropZone.style.background = "rgba(212, 175, 55, 0.04)";
    });

    dropZone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropZone.style.background = "rgba(212, 175, 55, 0.04)";
      if (e.dataTransfer.files.length > 0) {
        uploadCredentialsFile(e.dataTransfer.files[0]);
      }
    });

    fileInput.addEventListener("change", () => {
      if (fileInput.files.length > 0) {
        uploadCredentialsFile(fileInput.files[0]);
      }
    });
  }

  async function uploadCredentialsFile(file) {
    if (!file.name.endsWith(".json")) {
      credsUploadFeedback.textContent = "Por favor, selecione um arquivo no formato .json";
      credsUploadFeedback.style.color = "#fca5a5";
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    credsUploadFeedback.textContent = "Validando credenciais...";
    credsUploadFeedback.style.color = "var(--gold-primary)";

    try {
      const res = await fetch("/api/upload-credentials", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error);

      credsUploadFeedback.textContent = `✓ ${data.message}`;
      credsUploadFeedback.style.color = "#86efac";
      runDiagnosticTest();
      showFeedback("Arquivo credentials.json configurado com sucesso!", "success");
    } catch (err) {
      credsUploadFeedback.textContent = `Erro: ${err.message}`;
      credsUploadFeedback.style.color = "#fca5a5";
    }
  }

  // ==========================================
  // 8. MODO EMBED (LOOKER STUDIO / IFRAME)
  // ==========================================
  function checkEmbedMode() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("embed") === "true" || window.location.hash === "#embed") {
      document.body.classList.add("embed-mode");
    }
  }

  // ==========================================
  // 9. INICIALIZAÇÃO
  // ==========================================
  async function init() {
    checkEmbedMode();

    // Atualiza badges de contagem de ambas as modalidades
    fetch("/api/members?modalidade=kendo")
      .then((r) => r.json())
      .then((d) => {
        if (countKendoEl && d.total !== undefined) countKendoEl.textContent = d.total;
      })
      .catch(() => {
        fetch("cache_kendo.json").then((r) => r.json()).then((d) => {
          if (countKendoEl && d.length) countKendoEl.textContent = d.length;
        }).catch(() => {});
      });

    fetch("/api/members?modalidade=iaido")
      .then((r) => r.json())
      .then((d) => {
        if (countIaidoEl && d.total !== undefined) countIaidoEl.textContent = d.total;
      })
      .catch(() => {
        fetch("cache_iaido.json").then((r) => r.json()).then((d) => {
          if (countIaidoEl && d.length) countIaidoEl.textContent = d.length;
        }).catch(() => {});
      });

    await loadMembersData();
    await loadNafudakakeSvg();
  }

  init();
});

