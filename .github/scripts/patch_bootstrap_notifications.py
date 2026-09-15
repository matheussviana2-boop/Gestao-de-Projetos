from pathlib import Path
import re

p = Path('Gestao-de-Projetos.html')
s = p.read_text(encoding='utf-8')

old = '''    async function loadBackendProjects(session) {
      const result = await apiRequest("listProjects", {}, session.token);
      return applyBootstrapData(result);
    }'''
new = '''    async function loadBackendProjects(session) {
      // Usa o snapshot completo para preservar projetos, atualizações, solicitações e usuários.
      const result = await apiRequest("bootstrap", {}, session.token);
      return applyBootstrapData(result);
    }'''

if old in s:
    s = s.replace(old, new)
elif 'apiRequest("bootstrap", {}, session.token)' not in s[s.find('async function loadBackendProjects'):s.find('async function loadBackendProjects') + 400]:
    raise SystemExit('loadBackendProjects não encontrado no formato esperado')

s = re.sub(r'const APP_CACHE_VERSION = "[^"]+";', 'const APP_CACHE_VERSION = "cache-2026-09-15-05";', s)

p.write_text(s, encoding='utf-8')
