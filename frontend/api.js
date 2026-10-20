// «Бэкенд» на localStorage — работает через Go Live и file://, сервер не нужен.
class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

/* ---------- хранилище ---------- */
function _load(key, def) {
  try { return JSON.parse(localStorage.getItem(key)) ?? def; } catch { return def; }
}
function _save(key, val) {
  try { localStorage.setItem(key, JSON.stringify(val)); } catch {}
}

const _getUsers   = () => _load('app_users', {});
const _getNotes   = () => _load('app_notes', []);
const _getSession = () => _load('app_session', null);

const _uid = () => Math.random().toString(36).slice(2) + Date.now().toString(36);
const _now = () => new Date().toISOString();

async function _currentUser() {
  const username = _getSession();
  if (!username) return null;
  const users = _getUsers();
  return users[username] ? { username } : null;
}

async function _requireUser() {
  const u = await _currentUser();
  if (!u) throw new ApiError(401, 'Не авторизован');
  return u;
}

/* ---------- Auth ---------- */
const Auth = {
  async me() {
    const u = await _currentUser();
    if (!u) throw new ApiError(401, 'Не авторизован');
    return { username: u.username };
  },

  async login(username, password) {
    const key = username.toLowerCase().trim();
    const users = _getUsers();
    if (!users[key] || users[key].password !== password)
      throw new ApiError(401, 'Неверный логин или пароль');
    _save('app_session', key);
    return { username: key };
  },

  async register(username, password) {
    const key = username.toLowerCase().trim();
    if (!/^[\w.\-а-яёА-ЯЁ]{3,30}$/u.test(key))
      throw new ApiError(422, 'Логин: 3–30 символов, только буквы, цифры, _ . -');
    if (!password || password.length < 8)
      throw new ApiError(422, 'Пароль должен быть не менее 8 символов');
    const users = _getUsers();
    if (users[key]) throw new ApiError(409, 'Пользователь уже существует');
    users[key] = { password };
    _save('app_users', users);
    _save('app_session', key);
    return { username: key };
  },

  async logout() {
    _save('app_session', null);
    return null;
  },
};

/* ---------- NotesStore ---------- */
const NotesStore = {
  async list() {
    const u = await _requireUser();
    return _getNotes().filter(n => n.owner === u.username && !n.deleted_at);
  },

  async create(data) {
    const u = await _requireUser();
    const note = {
      id: _uid(),
      owner: u.username,
      title: data.title ?? '',
      body: data.body ?? '',
      tags: data.tags ?? [],
      color: data.color ?? 'default',
      pinned: data.pinned ?? false,
      archived: data.archived ?? false,
      created_at: _now(),
      updated_at: _now(),
      deleted_at: null,
    };
    const notes = _getNotes();
    notes.push(note);
    _save('app_notes', notes);
    return note;
  },

  async update(id, patch) {
    const u = await _requireUser();
    const notes = _getNotes();
    const i = notes.findIndex(n => n.id === id && n.owner === u.username);
    if (i === -1) throw new ApiError(404, 'Заметка не найдена');
    Object.assign(notes[i], patch, { updated_at: _now() });
    _save('app_notes', notes);
    return notes[i];
  },

  async remove(id) {
    const u = await _requireUser();
    const notes = _getNotes();
    const i = notes.findIndex(n => n.id === id && n.owner === u.username);
    if (i === -1) throw new ApiError(404, 'Заметка не найдена');
    notes[i].deleted_at = _now();
    _save('app_notes', notes);
    return null;
  },

  async restore(id) {
    const u = await _requireUser();
    const notes = _getNotes();
    const i = notes.findIndex(n => n.id === id && n.owner === u.username);
    if (i === -1) throw new ApiError(404, 'Заметка не найдена');
    notes[i].deleted_at = null;
    notes[i].updated_at = _now();
    _save('app_notes', notes);
    return notes[i];
  },
};
