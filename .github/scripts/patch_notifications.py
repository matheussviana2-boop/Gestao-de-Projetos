from pathlib import Path
import re

# patch revision 2
p = Path('Gestao-de-Projetos.html')
s = p.read_text(encoding='utf-8')

s = s.replace(
    '      const owner = project.responsavel || "Não informado";',
    '      const owner = canonicalUserName(project.responsavel) || project.responsavel || "Não informado";'
)
s = s.replace(
    '        members: normalizeMembers(project.participantes),',
    '        members: normalizeMembers(project.participantes).map(name => canonicalUserName(name) || name).filter(name => name && !samePerson(name, owner)),'
)
s = s.replace(
    '        creator: project.criadoPor || owner,',
    '        creator: canonicalUserName(project.criadoPor) || project.criadoPor || owner,'
)

old = '''          id: item.id,
          dateTime: item.criadoEm ? new Date(item.criadoEm).toLocaleString("pt-BR") : "",
          actor: item.usuarioNome || "Sistema",
          type: item.tipo || "update",'''
new = '''          id: item.id,
          dateTime: item.criadoEm ? new Date(item.criadoEm).toLocaleString("pt-BR") : "",
          sortTime: item.criadoEm ? new Date(item.criadoEm).getTime() : (Number(item.id) || 0),
          actor: canonicalUserName(item.usuarioNome) || item.usuarioNome || "Sistema",
          type: item.tipo || "update",'''
if old in s:
    s = s.replace(old, new)

old = '''      project.updates.push({
        id: Date.now() + Math.random(),
        dateTime: formatDateTimeNow(),
        actor: currentUser.name,
        ...entry
      });'''
new = '''      const now = Date.now();
      project.updates.push({
        id: now + Math.random(),
        dateTime: formatDateTimeNow(),
        sortTime: now,
        actor: currentUser.name,
        ...entry
      });'''
if old in s:
    s = s.replace(old, new)

old = '''    function getAllProjectActivities() {
      return projects.flatMap(project =>
        (project.updates || []).map(update => ({ project, update }))
      ).sort((a, b) => {
        const aTime = Date.parse(a.update.dateTime) || Number(a.update.id) || 0;
        const bTime = Date.parse(b.update.dateTime) || Number(b.update.id) || 0;
        return bTime - aTime;
      });
    }'''
new = '''    function activityTimestamp(update) {
      const numeric = Number(update?.sortTime);
      if (Number.isFinite(numeric) && numeric > 0) return numeric;
      const raw = String(update?.dateTime || "").trim();
      const br = raw.match(/^(\\d{1,2})\\/(\\d{1,2})\\/(\\d{4})(?:,?\\s+(\\d{1,2}):(\\d{2})(?::(\\d{2}))?)?/);
      if (br) {
        const [, day, month, year, hour = "0", minute = "0", second = "0"] = br;
        return new Date(Number(year), Number(month) - 1, Number(day), Number(hour), Number(minute), Number(second)).getTime();
      }
      const direct = Date.parse(raw);
      if (Number.isFinite(direct)) return direct;
      const id = Number(update?.id);
      return Number.isFinite(id) ? id : 0;
    }

    function getAllProjectActivities() {
      return projects.flatMap(project =>
        (project.updates || []).map(update => ({ project, update }))
      ).sort((a, b) => activityTimestamp(b.update) - activityTimestamp(a.update));
    }'''
if old not in s and 'function activityTimestamp(update)' not in s:
    raise SystemExit('getAllProjectActivities não encontrado')
if old in s:
    s = s.replace(old, new)

marker = '''    function markProjectUpdatesAsRead(project, userName = currentUser.name) {
      project.readUpdatesBy = project.readUpdatesBy && typeof project.readUpdatesBy === "object"
        ? project.readUpdatesBy
        : {};
      project.readUpdatesBy[userName] = Array.isArray(project.updates) ? project.updates.length : 0;
    }
'''
if 'function markAllProjectUpdatesAsRead' not in s:
    helper = marker + '''
    function markAllProjectUpdatesAsRead(userName = currentUser.name) {
      projects.forEach(project => markProjectUpdatesAsRead(project, userName));
      persistProjects();
      updateNotificationBadge();
    }
'''
    if marker not in s:
        raise SystemExit('markProjectUpdatesAsRead não encontrado')
    s = s.replace(marker, helper)

old = '''    document.getElementById("notificationButton").addEventListener("click", () => {
      renderActivities();
      openDialog(notificationModal);
    });'''
new = '''    document.getElementById("notificationButton").addEventListener("click", async () => {
      openDialog(notificationModal);
      markAllProjectUpdatesAsRead();
      renderActivities();

      const session = readStoredSession();
      if (!session?.token) return;
      try {
        await loadBackendProjects(session);
        lastSyncAt = Date.now();
        markAllProjectUpdatesAsRead();
        renderActivities();
      } catch (error) {
        console.warn("Não foi possível atualizar o histórico agora:", error);
      }
    });'''
if old in s:
    s = s.replace(old, new)
elif 'markAllProjectUpdatesAsRead();\n      renderActivities();' not in s:
    raise SystemExit('listener notificationButton não encontrado')

start = s.find('    function applyBootstrapData(result) {')
end = s.find('\n    async function loadBackendProjects', start)
if start < 0 or end < 0:
    raise SystemExit('applyBootstrapData não encontrado')
block = s[start:end]
users_block = '''      if (Array.isArray(result.users) && currentUser?.isAdmin) {
        const previousUsers = [...users];
        users = result.users.map(mapApiUser);
        if (!users.some(user => user.id === currentUser.id)) users.unshift(currentUser);
        users = assignDistinctAvatarColors(users, previousUsers);
        refreshUserSwitcher();
        renderSystemUsers();
      }
'''
if users_block in block:
    block = block.replace(users_block, '')
    pos = block.find('\n') + 1
    block = block[:pos] + users_block + block[pos:]
    s = s[:start] + block + s[end:]

if 'function canonicalizeHistoryText(value)' not in s:
    anchor = '    function renderActivities() {'
    helper = '''    function canonicalizeHistoryText(value) {
      let text = String(value || "");
      text = text.replace(/Thais Ara\\?jo/g, "Thais Araújo");
      return text;
    }

'''
    if anchor in s:
        s = s.replace(anchor, helper + anchor)

s = s.replace('${escapeHtml(update.actor)}', '${escapeHtml(canonicalUserName(update.actor) || update.actor)}')
s = s.replace('${escapeHtml(update.note)}</p>', '${escapeHtml(canonicalizeHistoryText(update.note))}</p>')
s = re.sub(r'const APP_CACHE_VERSION = "[^"]+";', 'const APP_CACHE_VERSION = "cache-2026-09-15-04";', s)

p.write_text(s, encoding='utf-8')
