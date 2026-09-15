from pathlib import Path

SRC = Path('Gestao-de-Projetos.html')
OUT = Path('Diretoria.html')
PRETTY_OUT = Path('diretoria/index.html')
DIRECTOR_ACCESS_KEY = 'R6V6GoUib1PvwxwM42TCpJAsXodJDDBH'

s = SRC.read_text(encoding='utf-8')

# A Diretoria é derivada diretamente do sistema principal: mesmo HTML, mesmo CSS,
# mesmos componentes, gráficos, cards, descrições, links e calendário.
s = s.replace('<title>CSC Gestão de Projetos</title>', '<title>CSC Gestão de Projetos · Diretoria</title>', 1)
if 'name="robots"' not in s:
    viewport = '<meta name="viewport" content="width=device-width, initial-scale=1.0" />'
    s = s.replace(viewport, viewport + '\n  <meta name="robots" content="noindex,nofollow,noarchive" />', 1)

readonly_css = '''
  <style id="csc-director-readonly">
    /* Mesmo sistema, mas sem recursos de alteração. */
    #loginScreen,
    .nav-button[data-section="Cadastros"],
    .nav-button[data-section="Configurações"],
    [data-page="Cadastros"],
    [data-page="Configurações"],
    #cadastrosPage,
    #settingsPage,
    #notificationButton,
    #requestButton,
    #openNewProjectModal,
    #openUserModal,
    #currentUserSelect,
    #logoutButton,
    .user-switcher,
    .profile-menu,
    [data-project-edit],
    [data-project-delete],
    [data-edit-project],
    [data-delete-project],
    [data-request-action],
    [data-transfer-owner],
    [data-remove-member],
    .registration-disable-btn,
    .request-actions,
    .member-manage-actions,
    .structural-actions,
    .update-project-actions,
    .modal-save,
    .modal-delete { display:none !important; }

    body.auth-pending .app,
    body.session-checking .app,
    body.csc-director-mode .app {
      display:grid !important;
      visibility:visible !important;
      opacity:1 !important;
      pointer-events:auto !important;
    }

    body.csc-director-mode .view-only-note { display:inline-flex !important; }
    body.csc-director-mode .nav-button.permission-readonly { opacity:1 !important; }
  </style>
'''
if 'id="csc-director-readonly"' not in s:
    s = s.replace('</head>', readonly_css + '\n</head>', 1)

# Bloqueio técnico: mesmo que algum botão de escrita reapareça no futuro, esta
# página pública só consegue chamar leitura da Diretoria e health.
send_needle = '    async function sendApi(action, payload, token, timeoutMs) {\n'
send_guard = '''    async function sendApi(action, payload, token, timeoutMs) {\n      if (action !== "directorView" && action !== "health") {\n        throw new Error("Painel da Diretoria: acesso somente para visualização.");\n      }\n'''
if send_needle not in s:
    raise SystemExit('sendApi não encontrado')
s = s.replace(send_needle, send_guard, 1)

# Substitui somente a inicialização/autenticação. Toda a renderização do sistema
# principal é preservada.
start_marker = '    // Boot: com sessão válida a interface abre na hora com o cache local e o\n'
start = s.find(start_marker)
if start < 0:
    raise SystemExit('Início do boot não encontrado')
end_marker = '    })();\n  </script>'
end = s.find(end_marker, start)
if end < 0:
    raise SystemExit('Fim do boot não encontrado')
end += len('    })();')

boot = f'''    // Boot Diretoria: sem login, somente leitura e uma única consulta ao abrir.
    (async function bootDirector() {{
      document.body.classList.add("csc-director-mode");
      document.body.classList.remove("auth-pending", "session-checking");
      loginScreen.hidden = true;

      currentUser = {{
        id: "director-view",
        name: "Diretoria",
        email: "",
        role: "Acompanhamento Executivo",
        permission: "visualizador",
        initials: "DI",
        avatar: "a1",
        isAdmin: false,
        active: true
      }};

      try {{ renderCurrentUser(); }} catch (_) {{}}

      const sessionInfo = document.getElementById("sessionUserEmail");
      if (sessionInfo) sessionInfo.textContent = "Diretoria · Somente leitura";

      document.querySelectorAll('.nav-button[data-section="Cadastros"], .nav-button[data-section="Configurações"], [data-page="Cadastros"], [data-page="Configurações"]').forEach(el => {{
        el.hidden = true;
        el.style.display = "none";
      }});
      ["notificationButton", "requestButton", "logoutButton", "openNewProjectModal"].forEach(id => {{
        const el = document.getElementById(id);
        if (el) {{ el.hidden = true; el.style.display = "none"; }}
      }});

      // O endereço compartilhado pode ser apenas /diretoria/. A chave é aplicada
      // internamente pela página; o parâmetro ?k= continua aceito para compatibilidade.
      const key = new URLSearchParams(window.location.search).get("k") || "{DIRECTOR_ACCESS_KEY}";

      try {{
        const result = await apiRequest("directorView", {{ key }}, "", 25000);
        applyBootstrapData({{
          projects: Array.isArray(result.projects) ? result.projects : [],
          updates: Array.isArray(result.updates) ? result.updates : [],
          requests: [],
          serverTime: result.serverTime
        }});
        showPage("Visão Geral");
      }} catch (error) {{
        console.error("Falha ao carregar painel da Diretoria:", error);
        projects = [];
        renderAreaOptions();
        renderProjects();
        showPage("Visão Geral");
        showToast(error?.message || "Não foi possível carregar os projetos.");
      }}
    }})();'''

s = s[:start] + boot + s[end:]

OUT.write_text(s, encoding='utf-8')
PRETTY_OUT.parent.mkdir(parents=True, exist_ok=True)
PRETTY_OUT.write_text(s, encoding='utf-8')
print(f'Diretoria gerada com {len(s)} bytes a partir do sistema principal.')
