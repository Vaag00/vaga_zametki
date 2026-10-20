// «Бэкенд» на localStorage — работает через Go Live и file://, сервер не нужен.
class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

/* ---------- хранилище ---------- */
function load(key, def) {
  try { return JSON.parse(localStorage.getItem(key)) ?? def; } catch { return def; }
}
function save(key, val) {
  try { localStorage.setItem(key, JSON.stringify(val)); } catch {}
}

const getUsers   = () => load('_users', {});
const getNotes   = () => load('_notes', []);
const getSession = () => load('_session', null);
const saveUsers  = u => save('_users', u);
const saveNotes  = n => save('_notes', n);
const saveSession = s => save('_session', s);

const uid = () => Math.random().toString(36).slice(2) + Date.now().toString(36);
const now = () => new Date().toISOString();

function currentUser() {
  const s = getSession();
  if (!s) return null;
  return getUsers()[s] ? { username: s } : null;
}
function requireUser() {
  const u = currentUser();
  if (!u) throw new ApiError(401, 'Не авторизован');
  return u;
}

/* ---------- Auth ---------- */
const Auth = {
  me() {
    const u = currentUser();
    if (!u) throw new ApiError(401, 'Не авторизован');
    return Promise.resolve({ username: u.username });
  },
  login(username, password) {
    const key = username.toLowerCase().trim();
    const users = getUsers();
    if (!users[key] || users[key].password !== password)
      throw new ApiError(401, 'Неверный логин или пароль');
    saveSession(key);
    return Promise.resolve({ username: key });
  },
  register(username, password) {
    const key = username.toLowerCase().trim();
    if (!/^[\w.\-а-яёА-ЯЁ]{3,30}$/u.test(key))
      throw new ApiError(422, 'Логин: 3–30 символов, только буквы, цифры, _ . -');
    if (!password || password.length < 8)
      throw new ApiError(422, 'Пароль должен быть не менее 8 символов');
    const users = getUsers();
    if (users[key]) throw new ApiError(409, 'Пользователь уже существует');
    users[key] = { password };
    saveUsers(users);
    saveSession(key);
    return Promise.resolve({ username: key });
  },
  logout() {
    saveSession(null);
    return Promise.resolve(null);
  },
};

/* ---------- NotesStore ---------- */
const NotesStore = {
  list() {
    const u = requireUser();
    return Promise.resolve(getNotes().filter(n => n.owner === u.username && !n.deleted_at));
  },
  create(data) {
    const u = requireUser();
    const note = {
      id: uid(), owner: u.username,
      title: data.title ?? '', body: data.body ?? '',
      tags: data.tags ?? [], color: data.color ?? 'default',
      pinned: data.pinned ?? false, archived: data.archived ?? false,
      created_at: now(), updated_at: now(), deleted_at: null,
    };
    const notes = getNotes();
    notes.push(note);
    saveNotes(notes);
    return Promise.resolve(note);
  },
  update(id, patch) {
    const u = requireUser();
    const notes = getNotes();
    const i = notes.findIndex(n => n.id === id && n.owner === u.username);
    if (i === -1) throw new ApiError(404, 'Заметка не найдена');
    Object.assign(notes[i], patch, { updated_at: now() });
    saveNotes(notes);
    return Promise.resolve(notes[i]);
  },
  remove(id) {
    const u = requireUser();
    const notes = getNotes();
    const i = notes.findIndex(n => n.id === id && n.owner === u.username);
    if (i === -1) throw new ApiError(404, 'Заметка не найдена');
    notes[i].deleted_at = now();
    saveNotes(notes);
    return Promise.resolve(null);
  },
  restore(id) {
    const u = requireUser();
    const notes = getNotes();
    const i = notes.findIndex(n => n.id === id && n.owner === u.username);
    if (i === -1) throw new ApiError(404, 'Заметка не найдена');
    notes[i].deleted_at = null;
    notes[i].updated_at = now();
    saveNotes(notes);
    return Promise.resolve(notes[i]);
  },
};
