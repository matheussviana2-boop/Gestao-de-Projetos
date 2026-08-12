from pathlib import Path
import re

path = Path('Gestao_de_Projetos.html')
html = path.read_text(encoding='utf-8')

html = html.replace('<title>CSC Gestão de Projetos | v87</title>', '<title>CSC Gestão de Projetos | v88</title>', 1)

old_header = '<button class="btn" type="button">Ver calendário completo</button>'
new_header = '''<div class="timeline-header-actions">
              <button id="showDeliveredProjects" class="btn timeline-delivered-btn" type="button">Ver entregues</button>
              <button id="openFullCalendar" class="btn" type="button">Ver calendário completo</button>
            </div>'''
if old_header not in html:
    raise SystemExit('Cabeçalho não localizado')
html = html.replace(old_header, new_header, 1)

anchor = '  <div id="updateModal" class="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="updateModalTitle">'
modal = '''  <div id="deliveredProjectsModal" class="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="deliveredProjectsTitle">
    <div class="modal delivered-projects-modal">
      <div class="modal-header">
        <div><h2 id="deliveredProjectsTitle">Projetos entregues</h2><p class="modal-helper">Últimas entregas concluídas, separadas da agenda de próximos prazos.</p></div>
        <button id="closeDeliveredProjectsModal" class="modal-close" type="button" aria-label="Fechar"><svg width="18" height="18"><use href="#i-x"/></svg></button>
      </div>
      <div id="deliveredProjectsList" class="delivered-projects-list"></div>
      <div id="deliveredProjectsEmpty" class="milestone-empty" hidden>Nenhum projeto concluído com data de entrega.</div>
    </div>
  </div>

'''
if 'id="deliveredProjectsModal"' not in html:
    if anchor not in html:
        raise SystemExit('Âncora de modal não localizada')
    html = html.replace(anchor, modal + anchor, 1)

pattern = re.compile(r'    function renderMilestones\(\) \{.*?\n    \}\n\n    const milestoneSummaryModal', re.S)
if not pattern.search(html):
    raise SystemExit('renderMilestones não localizada')
replacement = r'''    function milestoneDeadlineMeta(project) {
      const endDate = parseBrDate(project.end);
      if (!endDate || Number.isNaN(endDate.getTime())) return { label: "SEM DATA", overdue: false };
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      endDate.setHours(0, 0, 0, 0);
      const diff = Math.round((endDate - today) / 86400000);
      if (diff < 0) return { label: `ATRASADO · ${Math.abs(diff)} ${Math.abs(diff) === 1 ? "DIA" : "DIAS"}`, overdue: true };
      if (diff === 0) return { label: "HOJE", overdue: false };
      return { label: `EM ${diff} ${diff === 1 ? "DIA" : "DIAS"}`, overdue: false };
    }

    function renderMilestones() {
      const container = document.getElementById("milestones");
      const actionable = [...projects]
        .filter(project => project && project.end && project.status !== "Concluído" && project.status !== "Cancelado")
        .map(project => ({ project, meta: milestoneDeadlineMeta(project) }))
        .sort((a, b) => {
          const priority = item => (item.meta.overdue || item.project.status === "Em atraso") ? 0 : (item.project.status === "Pausado" ? 1 : 2);
          return priority(a) - priority(b) || (parseBrDate(a.project.end) - parseBrDate(b.project.end));
        });
      const visible = actionable.slice(0, MILESTONES_PER_PAGE);
      if (!visible.length) {
        container.innerHTML = `<div class="milestone-empty">Nenhuma próxima entrega com data definida.</div>`;
      } else {
        container.innerHTML = visible.map(({ project, meta }) => {
          const overdue = meta.overdue || project.status === "Em atraso";
          const stateClass = overdue ? "overdue" : (project.status === "Pausado" ? "paused" : "upcoming");
          return `<div class="milestone ${stateClass}" data-milestone-id="${escapeHtml(project.id)}" role="button" tabindex="0" aria-label="Abrir resumo do projeto ${escapeHtml(project.name)}">
            <div class="milestone-icon"><svg><use href="#i-flag"/></svg></div>
            <div class="milestone-main"><div class="milestone-deadline-badge">${escapeHtml(meta.label)}</div><time>${formatMilestoneDate(project.end)}</time><strong>${escapeHtml(project.name)}</strong><small>${escapeHtml(project.owner)} · ${escapeHtml(project.status)}</small></div>
            <div class="milestone-axis-label" aria-hidden="true"><strong>${formatMilestoneDate(project.end)}</strong></div>
          </div>`;
        }).join("");
      }
      container.querySelectorAll(".milestone[data-milestone-id]").forEach(card => {
        const openSummary = () => openMilestoneSummary(card.dataset.milestoneId);
        card.addEventListener("click", openSummary);
        card.addEventListener("keydown", event => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); openSummary(); } });
      });
    }

    const deliveredProjectsModal = document.getElementById("deliveredProjectsModal");
    const deliveredProjectsList = document.getElementById("deliveredProjectsList");
    const deliveredProjectsEmpty = document.getElementById("deliveredProjectsEmpty");

    function renderDeliveredProjects() {
      const delivered = [...projects].filter(project => project && project.end && project.status === "Concluído").sort((a, b) => parseBrDate(b.end) - parseBrDate(a.end)).slice(0, 5);
      deliveredProjectsEmpty.hidden = delivered.length > 0;
      deliveredProjectsList.innerHTML = delivered.map(project => `<button class="delivered-project-card" type="button" data-delivered-id="${escapeHtml(project.id)}"><span class="delivered-project-check"><svg><use href="#i-check"/></svg></span><span class="delivered-project-info"><strong>${escapeHtml(project.name)}</strong><small>${escapeHtml(project.owner)} · concluído</small></span><span class="delivered-project-date">${formatMilestoneDate(project.end)}</span></button>`).join("");
      deliveredProjectsList.querySelectorAll("[data-delivered-id]").forEach(card => card.addEventListener("click", () => { closeDialog(deliveredProjectsModal); openMilestoneSummary(card.dataset.deliveredId); }));
    }

    function openDeliveredProjects() { renderDeliveredProjects(); openDialog(deliveredProjectsModal); }

    const milestoneSummaryModal'''
html = pattern.sub(replacement, html, count=1)

listener = re.compile(r'    document\.querySelectorAll\("\.timeline-panel \.btn"\)\.forEach\(button => \{.*?\n    \}\);', re.S)
if not listener.search(html):
    raise SystemExit('Listener da timeline não localizado')
listener_replacement = '''    document.getElementById("openFullCalendar")?.addEventListener("click", () => {
      const calendarButton = document.querySelector('.nav-button[data-section="Calendário"]');
      document.querySelectorAll(".nav-button").forEach(item => item.classList.remove("active"));
      if (calendarButton) calendarButton.classList.add("active");
      showPage("Calendário");
      populateCalendarYears();
      document.getElementById("calendarYear").value = new Date().getFullYear();
      renderCalendar();
    });
    document.getElementById("showDeliveredProjects")?.addEventListener("click", openDeliveredProjects);
    document.getElementById("closeDeliveredProjectsModal")?.addEventListener("click", () => closeDialog(deliveredProjectsModal));
    deliveredProjectsModal?.addEventListener("click", event => { if (event.target === deliveredProjectsModal) closeDialog(deliveredProjectsModal); });'''
html = listener.sub(listener_replacement, html, count=1)

html = html.replace('[updateModal, historyModal, milestoneSummaryModal].forEach(dialog => {', '[updateModal, historyModal, milestoneSummaryModal, deliveredProjectsModal].forEach(dialog => {', 1)
html = html.replace('if (milestoneSummaryModal.classList.contains("open")) closeDialog(milestoneSummaryModal);', 'if (milestoneSummaryModal.classList.contains("open")) closeDialog(milestoneSummaryModal);\n      if (deliveredProjectsModal?.classList.contains("open")) closeDialog(deliveredProjectsModal);', 1)
html = html.replace('<div class="calendar-project-description">${escapeHtml(projectDescription)}</div>', '<div class="calendar-project-description"><span class="calendar-description-label">Descrição resumida</span>${escapeHtml(projectDescription)}</div>', 1)

css = '''\n  <style data-csc-timeline-v88>
    .timeline-header-actions{display:flex;align-items:center;gap:9px;flex-wrap:wrap;justify-content:flex-end}.timeline-delivered-btn{border-color:rgba(43,156,96,.30)!important;color:#26794e!important;background:rgba(230,247,237,.72)!important}.milestone-deadline-badge{display:inline-flex;width:max-content;margin-bottom:6px;padding:3px 7px;border-radius:999px;font-size:.60rem;font-weight:850;color:#15739c;background:rgba(51,166,211,.11);border:1px solid rgba(51,166,211,.18)}.milestone.overdue{border-color:rgba(211,69,69,.34)!important;background:linear-gradient(145deg,rgba(255,242,242,.96),rgba(249,229,229,.88))!important}.milestone.overdue .milestone-icon{color:#c43c3c!important;background:rgba(255,225,225,.86)!important}.milestone.overdue .milestone-deadline-badge{color:#b22f2f;background:rgba(216,70,70,.10)}.milestone.paused{border-color:rgba(219,128,28,.32)!important;background:linear-gradient(145deg,rgba(255,248,236,.96),rgba(245,234,217,.88))!important}.milestone.paused .milestone-deadline-badge{color:#a65c0b;background:rgba(229,139,38,.11)}.delivered-projects-modal{max-width:620px!important}.delivered-projects-list{display:grid;gap:10px;padding:4px 0}.delivered-project-card{width:100%;border:1px solid rgba(50,155,96,.22);border-radius:13px;background:linear-gradient(145deg,rgba(239,250,244,.96),rgba(228,244,235,.88));padding:13px 14px;display:grid;grid-template-columns:36px 1fr auto;gap:11px;align-items:center;text-align:left;cursor:pointer;color:inherit}.delivered-project-check{width:32px;height:32px;border-radius:50%;display:grid;place-items:center;color:#278150;background:rgba(70,180,116,.13)}.delivered-project-check svg{width:17px;height:17px}.delivered-project-info{min-width:0;display:grid;gap:3px}.delivered-project-info strong{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:.84rem;color:#1d4431}.delivered-project-info small{color:#668075;font-size:.68rem}.delivered-project-date{white-space:nowrap;font-size:.68rem;font-weight:850;color:#26794e;background:rgba(70,180,116,.10);padding:5px 8px;border-radius:999px}.calendar-description-label{display:block;margin-bottom:4px;color:#315d70;font-size:.61rem;font-weight:850;text-transform:uppercase;letter-spacing:.045em}@media(max-width:680px){.timeline-header-actions{width:100%;justify-content:flex-start}.delivered-project-card{grid-template-columns:32px 1fr}.delivered-project-date{grid-column:2;justify-self:start}}
  </style>\n'''
if 'data-csc-timeline-v88' not in html:
    html = html.replace('</head>', css + '</head>', 1)

path.write_text(html, encoding='utf-8')
print('Patch v88 aplicado')
